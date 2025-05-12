import requests
from rdkit import Chem
from rdkit.Chem import AllChem
import py3Dmol
import streamlit as st
import spacy
import re

# --- Styling and Configuration ---
st.set_page_config(
    page_title="⚛️ Molecular Explorer",
    page_icon="⚛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for a darker theme
st.markdown(
    """
    <style>
    body {
        color: #dcdcdc;
        background-color: #1e1e1e;
    }
    .stApp {
        background-color: #1e1e1e;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Load spaCy English model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    st.warning("Downloading spaCy language model 'en_core_web_sm'. This might take a moment.")
    import spacy.cli
    spacy.cli.download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

# --- Functions ---
def get_cid(compound_name):
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{compound_name}/cids/TXT"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text.strip()
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Error fetching CID: {e}")
        return None

def get_smiles_and_name_from_cid(cid):
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/property/IUPACName,CanonicalSMILES/JSON"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        props = data["PropertyTable"]["Properties"][0]
        return props.get("CanonicalSMILES"), props.get("IUPACName")
    except (requests.exceptions.RequestException, KeyError, IndexError) as e:
        st.error(f"❌ Error fetching SMILES and IUPAC name: {e}")
        return None, None

def generate_3d_structure(smiles):
    try:
        mol = Chem.MolFromSmiles(smiles, sanitize=True)
        if mol is None:
            st.error("❌ Invalid SMILES string.")
            return None
        mol = Chem.AddHs(mol)
        if AllChem.EmbedMolecule(mol, randomSeed=42) != 0:
            st.error("❌ Failed to embed molecule in 3D space.")
            return None
        AllChem.UFFOptimizeMolecule(mol, maxIters=200)
        return mol
    except Exception as e:
        st.error(f"❌ Error generating 3D structure: {e}")
        return None

def get_molecular_properties(cid):
    base_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/property/"
    properties = [
        "MolecularWeight", "ExactMass", "XLogP", "Complexity",
        "RotatableBondCount", "HydrogenBondDonorCount", "HydrogenBondAcceptorCount"
    ]
    available_props = {}
    for prop in properties:
        try:
            url = f"{base_url}{prop}/JSON"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()["PropertyTable"]["Properties"][0]
            available_props[prop] = data.get(prop, "N/A")
        except Exception:
            available_props[prop] = "Not Available"
    return available_props

def visualize_3d_structure(mol):
    try:
        mol_block = Chem.MolToMolBlock(mol)
        viewer = py3Dmol.view(width=600, height=400)
        viewer.addModel(mol_block, "mol")
        viewer.setStyle({'stick': {'radius': 0.15, 'colorscheme': 'cyanCarbon'}})
        viewer.addSurface("VDW", {"opacity": 0.3, "color": "white"})
        viewer.setBackgroundColor('#222222')
        labels = []
        for i, atom in enumerate(mol.GetAtoms()):
            pos = mol.GetConformer().GetAtomPosition(i)
            labels.append({
                'text': atom.GetSymbol(),
                'position': {'x': pos.x, 'y': pos.y, 'z': pos.z},
                'fontColor': 'white',
                'fontSize': 10,
                'backgroundOpacity': 0.6
            })
        viewer.addLabels(labels)
        viewer.zoomTo()
        html_content = viewer._make_html()
        if not html_content:
            st.error("❌ Failed to generate 3D visualization HTML.")
            return None
        return html_content
    except Exception as e:
        st.error(f"❌ Error during 3D structure visualization: {e}")
        return None

def parse_query(query, input_type):
    if input_type == "CID":
        if re.match(r'^\d+$', query.strip()):
            return query.strip(), True
        else:
            st.error("❌ Invalid CID format. Please enter a numeric CID.")
            return None, False
    else:
        doc = nlp(query.lower())
        for ent in doc.ents:
            if ent.label_ in ["CHEMICAL", "DRUG", "COMPOUND"]:
                return ent.text.capitalize(), False
        for token in doc:
            if token.pos_ in ["NOUN", "PROPN"]:
                return token.text.capitalize(), False
        return None, False

# --- Streamlit Web App ---
def main():
    st.title("⚛️ Interactive Molecular Explorer")
    st.markdown("Explore the 3D structures and properties of chemical compounds by name or PubChem CID.")
    st.markdown("---")

    input_type = st.selectbox("Select input type:", ["Compound Name", "CID"])
    user_query = st.text_input("🔍 Enter your query:", "Acetylsalicylic acid" if input_type == "Compound Name" else "2244")

    if st.button("Visualize"):
        compound_name, is_cid = parse_query(user_query, input_type)

        if not compound_name:
            st.error("❌ Could not identify a compound in your query. Please be more specific.")
            return

        if is_cid:
            cid = compound_name
            st.success(f"🔎 Using CID: {cid}")
        else:
            st.success(f"🔎 Searching for: {compound_name}")
            cid = get_cid(compound_name)

        if not cid:
            st.error("❌ Compound not found in PubChem.")
            return

        st.info(f"PubChem CID: {cid}")
        smiles, iupac_name = get_smiles_and_name_from_cid(cid)

        if not smiles:
            st.error("❌ SMILES not retrieved for this compound.")
            return

        mol = generate_3d_structure(smiles)

        if mol:
            st.subheader("✨ 3D Molecular Structure")
            html_3d = visualize_3d_structure(mol)
            if html_3d:
                st.components.v1.html(html_3d, height=400, width=600, scrolling=False)
            
            st.subheader("🏷️ Chemical Identifiers")
            st.write(f"**IUPAC Name:** {iupac_name if iupac_name else 'Not Available'}")
            st.write(f"**SMILES:** `{smiles}`")

            st.subheader("📊 Molecular Properties")
            props = get_molecular_properties(cid)
            if props:
                for key, val in props.items():
                    st.write(f"**{key}:** {val if val is not None else 'Not Available'}")
            else:
                st.warning("⚠️ Additional molecular properties could not be retrieved.")
        else:
            st.error("❌ Could not generate 3D structure.")

if __name__ == "__main__":
    main()