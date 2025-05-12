3D Molecule-Text Interpretation Project
The 3D Molecule-Text Interpretation Project is an interactive web application built with Streamlit that interprets natural language queries or PubChem CIDs to visualize 3D molecular structures and retrieve chemical properties. By leveraging PubChem's API, RDKit, and py3Dmol, the app allows users to explore molecules through text inputs like "Acetylsalicylic acid" or numeric CIDs like "2244". The project combines natural language processing (via spaCy) with cheminformatics to provide a seamless user experience.
Features

Text Query Interpretation: Parse compound names from natural language inputs using spaCy.
CID Support: Directly query molecules using PubChem Compound IDs.
3D Visualization: Render interactive 3D molecular structures with atom labels using py3Dmol.
Chemical Properties: Retrieve properties like molecular weight, XLogP, complexity, and hydrogen bond counts from PubChem.
Dark Theme UI: A sleek, user-friendly interface with a dark theme for better visibility.
Error Handling: Robust handling of invalid inputs, API errors, and visualization issues.

Installation


Create a virtual environment (recommended):
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate


Install dependencies:
pip install -r requirements.txt


Install spaCy language model:
python -m spacy download en_core_web_sm



Usage

Run the Streamlit app:
streamlit run molecular_explorer.py


Access the app:

Open the URL provided by Streamlit (typically http://localhost:8501) in your web browser.


Explore molecules:

Select the input type: "Compound Name" or "CID".
Enter a query (e.g., "Acetylsalicylic acid" for a compound name or "2244" for a CID).
Click the "Visualize" button to display the 3D molecular structure, IUPAC name, SMILES string, and chemical properties.



Dependencies

Python 3.8+
Streamlit
RDKit
py3Dmol
spaCy
Requests
re

Install them using:
pip install streamlit rdkit py3dmol spacy requests

Example

Input:
Compound Name: "Acetylsalicylic acid"
CID: "2244"


Output:
3D molecular structure with labeled atoms.
Chemical Identifiers: IUPAC name, SMILES string.
Properties: Molecular weight, exact mass, XLogP, complexity, rotatable bond count, hydrogen bond donor/acceptor counts.



Contributing
We welcome contributions to enhance the project! To contribute:

Fork the repository.
Create a feature branch (git checkout -b feature/new-feature).
Commit your changes (git commit -m "Add new feature").
Push to the branch (git push origin feature/new-feature).
Open a Pull Request with a detailed description of your changes.

License
This project is licensed under the MIT License. See the LICENSE file for details.
Contact
For questions, feedback, or issues, please:

Open an issue on this repository.
Contact .

Acknowledgments

PubChem for providing chemical data via their API.
RDKit for cheminformatics tools.
py3Dmol for 3D molecular visualization.
spaCy for natural language processing.
Streamlit for the web app framework.


Built with ⚛️ by [vipin mishra].
