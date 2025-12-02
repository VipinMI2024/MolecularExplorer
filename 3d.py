import asyncio
import aiohttp
import numpy as np
from pybabylonjs import Scene, Vector3, Color3, HemisphericLight, PBRMetallicRoughnessMaterial, MeshBuilder, TransformNode
from pybabylonjs import GUI
from typing import Dict, List, Tuple, Optional

# Element Properties
element_props: Dict[str, Dict[str, any]] = {
    'H': {'color': Color3.White(), 'radius': 0.3 * 0.8, 'covalentRadius': 0.31},
    'C': {'color': Color3.Black(), 'radius': 0.7 * 0.8, 'covalentRadius': 0.76},
    'O': {'color': Color3.Red(), 'radius': 0.6 * 0.8, 'covalentRadius': 0.66},
    'N': {'color': Color3.Blue(), 'radius': 0.65 * 0.8, 'covalentRadius': 0.71},
    'S': {'color': Color3.Yellow(), 'radius': 0.75 * 0.8, 'covalentRadius': 1.05},
    'P': {'color': Color3(1, 0.5, 0), 'radius': 0.8 * 0.8, 'covalentRadius': 1.07},
    'Cl': {'color': Color3.Green(), 'radius': 0.7 * 0.8, 'covalentRadius': 1.02},
    'F': {'color': Color3(0.5, 1, 0.5), 'radius': 0.6 * 0.8, 'covalentRadius': 0.57},
    'Br': {'color': Color3(0.65, 0.16, 0.16), 'radius': 0.85 * 0.8, 'covalentRadius': 1.20},
    'I': {'color': Color3(0.58, 0.0, 0.83), 'radius': 0.95 * 0.8, 'covalentRadius': 1.39},
    'Na': {'color': Color3(0.67, 0.36, 0.94), 'radius': 1.54 * 0.8, 'covalentRadius': 1.66},
    'K': {'color': Color3(0.56, 0.25, 0.83), 'radius': 1.96 * 0.8, 'covalentRadius': 2.03},
    'Ca': {'color': Color3(0.24, 1.0, 0.0), 'radius': 1.74 * 0.8, 'covalentRadius': 1.76},
    'Fe': {'color': Color3(0.87, 0.39, 0.19), 'radius': 1.26 * 0.8, 'covalentRadius': 1.32},
    'Mg': {'color': Color3(0.54, 1.0, 0.0), 'radius': 1.45 * 0.8, 'covalentRadius': 1.41},
    'Zn': {'color': Color3(0.49, 0.5, 0.69), 'radius': 1.31 * 0.8, 'covalentRadius': 1.22},
    'Si': {'color': Color3(0.94, 0.78, 0.63), 'radius': 1.17 * 0.8, 'covalentRadius': 1.11},
    'B': {'color': Color3(1.0, 0.71, 0.71), 'radius': 0.85 * 0.8, 'covalentRadius': 0.84},
}
default_props = {'color': Color3.Gray(), 'radius': 0.5 * 0.8, 'covalentRadius': 0.7}

# Array of element symbols, indexed by atomic number (index 0 is unused)
symbols: List[str] = [
    '',  # 0 is unused
    'H', 'He', 'Li', 'Be', 'B', 'C', 'N', 'O', 'F', 'Ne',
    'Na', 'Mg', 'Al', 'Si', 'P', 'S', 'Cl', 'Ar', 'K', 'Ca',
    'Sc', 'Ti', 'V', 'Cr', 'Mn', 'Fe', 'Co', 'Ni', 'Cu', 'Zn',
    'Ga', 'Ge', 'As', 'Se', 'Br', 'Kr', 'Rb', 'Sr', 'Y', 'Zr',
    'Nb', 'Mo', 'Tc', 'Ru', 'Rh', 'Pd', 'Ag', 'Cd', 'In', 'Sn',
    'Sb', 'Te', 'I', 'Xe', 'Cs', 'Ba', 'La', 'Ce', 'Pr', 'Nd',
    'Pm', 'Sm', 'Eu', 'Gd', 'Tb', 'Dy', 'Ho', 'Er', 'Tm', 'Yb',
    'Lu', 'Hf', 'Ta', 'W', 'Re', 'Os', 'Ir', 'Pt', 'Au', 'Hg',
    'Tl', 'Pb', 'Bi', 'Po', 'At', 'Rn', 'Fr', 'Ra', 'Ac', 'Th',
    'Pa', 'U', 'Np', 'Pu', 'Am', 'Cm', 'Bk', 'Cf', 'Es', 'Fm',
    'Md', 'No', 'Lr', 'Rf', 'Db', 'Sg', 'Bh', 'Hs', 'Mt', 'Ds',
    'Rg', 'Cn', 'Nh', 'Fl', 'Mc', 'Lv', 'Ts', 'Og'
]

def atomic_number_to_symbol(num: int) -> str:
    if not isinstance(num, int) or num < 1 or num > 118:
        return 'Unknown'
    return symbols[num]

def parse_formula(formula: str) -> List[str]:
    import re
    atoms = []
    for match in re.finditer(r'([A-Z][a-z]?)(\d*)', formula):
        element, count = match.groups()
        count = int(count) if count else 1
        atoms.extend([element] * count)
    return atoms

async def poll_for_result(list_key: str) -> Optional[List[int]]:
    delay = 2.0
    max_attempts = 10
    attempts = 0

    async with aiohttp.ClientSession() as session:
        while attempts < max_attempts:
            async with session.get(f'https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/listkey/{list_key}/cids/JSON') as response:
                data = await response.json()
                if 'Waiting' in data:
                    await asyncio.sleep(delay)
                    attempts += 1
                elif 'IdentifierList' in data and 'CID' in data['IdentifierList']:
                    return data['IdentifierList']['CID']
                else:
                    raise ValueError('Failed to retrieve results')
        raise TimeoutError('Request timed out')

async def fetch_molecule_data(formula: str) -> Optional[Dict[str, any]]:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/formula/{formula}/cids/JSON') as response:
                cid_data = await response.json()

            if 'Waiting' in cid_data:
                cids = await poll_for_result(cid_data['Waiting']['ListKey'])
                if not cids or len(cids) == 0:
                    return None
                cid = cids[0]
            elif 'IdentifierList' in cid_data and 'CID' in cid_data['IdentifierList']:
                cid = cid_data['IdentifierList']['CID'][0]
            else:
                return None

            async with session.get(f'https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/record/JSON?record_type=3d') as response:
                record_data = await response.json()

            if not record_data.get('PC_Compounds') or len(record_data['PC_Compounds']) == 0:
                return None

            compound = record_data['PC_Compounds'][0]
            atoms = [atomic_number_to_symbol(num) for num in compound['atoms']['element']]
            coords = next((c for c in compound['coords'] if 5 in c['type']), None)
            if not coords or 'conformers' not in coords:
                return None

            conformer = coords['conformers'][0]
            positions = [Vector3(x, y, z) for x, y, z in zip(conformer['x'], conformer['y'], conformer['z'])]
            bonds = [(aid1 - 1, aid2 - 1) for aid1, aid2 in zip(compound['bonds']['aid1'], compound['bonds']['aid2'])]
            bond_orders = [float(order) for order in compound['bonds'].get('order', [1] * len(bonds))]

            return {'atoms': atoms, 'positions': positions, 'bonds': bonds, 'bond_orders': bond_orders}
    except Exception as e:
        print(f'Error fetching data: {e}')
        return None

def create_simplified_molecule(atoms: List[str], scene: Scene, atom_size_scale: float = 1.0, parent: Optional[TransformNode] = None) -> None:
    x = 0
    spacing = 2
    for atom in atoms:
        props = element_props.get(atom, default_props)
        sphere = MeshBuilder.CreateSphere(atom, {'diameter': props['radius'] * 2 * atom_size_scale}, scene)
        sphere.position.x = x
        if parent:
            sphere.parent = parent
        material = PBRMetallicRoughnessMaterial(f'{atom}_mat', scene)
        material.base_color = props['color']
        sphere.material = material
        x += spacing

async def create_molecule(
    formula: str,
    scene: Scene,
    atom_size_scale: float = 1.0,
    bond_thickness: float = 0.1,
    bond_split: bool = True,
    parent: Optional[TransformNode] = None
) -> None:
    global error_text
    data = await fetch_molecule_data(formula)
    error_text.text = ""
    if not data:
        error_text.text = "Molecule or its 3D definition not found in PubChem. Falling back to simplified model."
        atoms = parse_formula(formula)
        create_simplified_molecule(atoms, scene, atom_size_scale, parent)
        return

    atoms, positions, bonds, bond_orders = data['atoms'], data['positions'], data['bonds'], data['bond_orders']

    # Create materials for each element
    materials: Dict[str, PBRMetallicRoughnessMaterial] = {}
    for element in set(atoms):
        props = element_props.get(element, default_props)
        material = PBRMetallicRoughnessMaterial(f'{element}_mat', scene)
        material.base_color = props['color']
        material.metallic = 0.9
        material.roughness = 0.26
        materials[element] = material

    # Render atoms as spheres
    for i, (atom, pos) in enumerate(zip(atoms, positions)):
        props = element_props.get(atom, default_props)
        sphere = MeshBuilder.CreateSphere(f'{atom}_{i}', {'diameter': props['radius'] * 2 * atom_size_scale}, scene)
        sphere.position = pos
        if parent:
            sphere.parent = parent
        sphere.material = materials[atom]

    # Render bonds as cylinders
    for (i, j), order in zip(bonds, bond_orders):
        p1, p2 = positions[i], positions[j]
        atom1, atom2 = atoms[i], atoms[j]
        props1 = element_props.get(atom1, default_props)
        props2 = element_props.get(atom2, default_props)
        distance = Vector3.Distance(p1, p2)
        direction = (p2 - p1).normalize()
        midpoint = Vector3.Lerp(p1, p2, 0.5)

        expected_length = (props1['covalentRadius'] + props2['covalentRadius']) * 1.1
        scale_factor = min(1, expected_length / distance)
        adjusted_p1 = p1
        adjusted_p2 = p1 + direction * (distance * scale_factor)
        adjusted_midpoint = Vector3.Lerp(adjusted_p1, adjusted_p2, 0.5)

        thickness = bond_thickness * (1 if order == 1 else 1.2 if order == 1.5 else 1.5 if order == 2 else 2)

        def create_bond_half(start: Vector3, end: Vector3, color: Color3, offset: Vector3) -> None:
            half_length = Vector3.Distance(start, end)
            cylinder = MeshBuilder.CreateCylinder(f'bond_{i}_{j}', {
                'height': half_length,
                'diameter': thickness,
                'tessellation': 16
            }, scene)
            if parent:
                cylinder.parent = parent
            material = PBRMetallicRoughnessMaterial(f'bond_mat_{i}_{j}', scene)
            material.base_color = color
            cylinder.material = material
            mid = (start + end) / 2
            cylinder.position = mid + offset
            v = (end - start).normalize()
            if abs(v.y) > 0.999:
                cylinder.rotation_quaternion = Quaternion.Identity() if v.y > 0 else Quaternion.RotationAxis(Vector3.Right(), np.pi)
            else:
                axis = Vector3.Cross(Vector3.Up(), v).normalize()
                angle = np.arccos(Vector3.Dot(Vector3.Up(), v))
                cylinder.rotation_quaternion = Quaternion.RotationAxis(axis, angle)

        perpendicular = direction.cross(Vector3(0, 0, 1)).normalize() * (thickness * 1.5)
        if order in (1, 1.5):
            if bond_split:
                create_bond_half(adjusted_p1, adjusted_midpoint, props1['color'], Vector3.Zero())
                create_bond_half(adjusted_midpoint, adjusted_p2, props2['color'], Vector3.Zero())
            else:
                create_bond_half(adjusted_p1, adjusted_p2, Color3.Gray(), Vector3.Zero())
        elif order == 2:
            for sign in [-1, 1]:
                offset = perpendicular * sign
                if bond_split:
                    create_bond_half(adjusted_p1, adjusted_midpoint, props1['color'], offset)
                    create_bond_half(adjusted_midpoint, adjusted_p2, props2['color'], offset)
                else:
                    create_bond_half(adjusted_p1, adjusted_p2, Color3.Red(), offset)
        elif order == 3:
            if bond_split:
                create_bond_half(adjusted_p1, adjusted_midpoint, props1['color'], Vector3.Zero())
                create_bond_half(adjusted_midpoint, adjusted_p2, props2['color'], Vector3.Zero())
                for sign in [-1, 1]:
                    offset = perpendicular * sign
                    create_bond_half(adjusted_p1, adjusted_midpoint, props1['color'], offset)
                    create_bond_half(adjusted_midpoint, adjusted_p2, props2['color'], offset)
            else:
                create_bond_half(adjusted_p1, adjusted_p2, Color3.Blue(), Vector3.Zero())
                for sign in [-1, 1]:
                    create_bond_half(adjusted_p1, adjusted_p2, Color3.Blue(), perpendicular * sign)

# Scene Setup
scene = Scene()
molecule_transform = TransformNode("moleculeTransform", scene)

# Add lighting
light = HemisphericLight("light", Vector3(0, 1, 0), scene)
light.intensity = 1

# Directional light (assuming pybabylonjs supports similar functionality)
from pybabylonjs import DirectionalLight
light_opt = DirectionalLight(intensity=10)
light_opt.draw(scene)

# GUI Setup
advanced_texture = GUI.AdvancedDynamicTexture.CreateFullscreenUI("UI")

stack_panel = GUI.StackPanel()
stack_panel.vertical_alignment = GUI.Control.VERTICAL_ALIGNMENT_BOTTOM
stack_panel.horizontal_alignment = GUI.Control.HORIZONTAL_ALIGNMENT_CENTER
advanced_texture.add_control(stack_panel)

padding_inp = 10

formula_input = GUI.InputText("formulaInput")
formula_input.width = "400px"
formula_input.height = "80px"
formula_input.text = "C10H13N5O4"
formula_input.color = "#ffffff"
formula_input.font_size = 24
formula_input.padding_top_in_pixels = padding_inp
formula_input.padding_bottom_in_pixels = padding_inp
stack_panel.add_control(formula_input)

load_button = GUI.Button.CreateSimpleButton("loadButton", "Load Molecule")
load_button.width = "400px"
load_button.height = "80px"
load_button.color = "#1f1c1b"
load_button.background = "#f0cebb"
load_button.font_size = 32
load_button.padding_top_in_pixels = padding_inp
load_button.padding_bottom_in_pixels = padding_inp
stack_panel.add_control(load_button)

slider_label = GUI.TextBlock("sliderLabel", "Rotation Speed")
slider_label.height = "50px"
slider_label.color = "white"
stack_panel.add_control(slider_label)

rotation_slider = GUI.Slider()
rotation_slider.minimum = 0
rotation_slider.maximum = 2 * np.pi
rotation_slider.value = 0.5
rotation_slider.height = "20px"
rotation_slider.width = "400px"
stack_panel.add_control(rotation_slider)

error_text = GUI.TextBlock("errorText", "")
error_text.color = "red"
error_text.height = "40px"
stack_panel.add_control(error_text)

pubchem_button = GUI.Button.CreateSimpleButton("pubchemButton", "Copy URL To PubChem")
pubchem_button.width = "400px"
pubchem_button.height = "50px"
pubchem_button.color = "white"
stack_panel.add_control(pubchem_button)

# Open PubChem URL on button click
def on_pubchem_click():
    import pyperclip
    formula = formula_input.text.strip()
    if formula:
        pubchem_url = f"https://pubchem.ncbi.nlm.nih.gov/#query={formula}"
        pyperclip.copy(pubchem_url)

pubchem_button.on_pointer_up_observable.add(on_pubchem_click)

loading_text = GUI.TextBlock("loadingText", "Loading...")
loading_text.color = "white"
loading_text.font_size = 32
loading_text.horizontal_alignment = GUI.Control.HORIZONTAL_ALIGNMENT_CENTER
loading_text.vertical_alignment = GUI.Control.VERTICAL_ALIGNMENT_CENTER
loading_text.is_visible = False
advanced_texture.add_control(loading_text)

warning_text = GUI.TextBlock("warningText", "Warning: This Application is meant to be used purely for educational STEM purposes. Always double-check results with official sources. Data fetched from PubChem database.")
warning_text.color = "white"
warning_text.font_size = 24
warning_text.width = "100%"
warning_text.height = "40px"
stack_panel.add_control(warning_text)

# Rotation Logic
def render_function():
    delta_time = scene.get_engine().get_delta_time() / 1000
    molecule_transform.rotation.y += rotation_slider.value * delta_time

scene.register_render_function(render_function)

# Load Molecule on Button Click
async def on_load_click():
    formula = formula_input.text.strip()
    if not formula:
        return

    loading_text.is_visible = True
    error_text.text = ""
    for mesh in molecule_transform.get_child_meshes():
        mesh.dispose()

    try:
        await create_molecule(formula, scene, 1.0, 0.1, True, molecule_transform)
    except Exception:
        error_text.text = "Molecule not found or error occurred."
    finally:
        loading_text.is_visible = False

load_button.on_pointer_up_observable.add_async(on_load_click)

# Start Function
async def start():
    formula = formula_input.text.strip()
    if not formula:
        return

    loading_text.is_visible = True
    error_text.text = ""
    for mesh in molecule_transform.get_child_meshes():
        mesh.dispose()

    try:
        await create_molecule(formula, scene, 1.0, 0.1, True, molecule_transform)
    except Exception:
        error_text.text = "Molecule not found or error occurred."
    finally:
        loading_text.is_visible = False

asyncio.run(start())
