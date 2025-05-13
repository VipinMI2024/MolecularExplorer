# 3D Molecule-Text Interpretation Project

The **3D Molecule-Text Interpretation Project** is an interactive web application built with **Streamlit** that interprets natural language queries or PubChem CIDs to visualize 3D molecular structures and retrieve chemical properties. By leveraging **PubChem's API**, **RDKit**, and **py3Dmol**, the app allows users to explore molecules using text inputs like `"Acetylsalicylic acid"` or numeric CIDs like `"2244"`. The project combines **natural language processing (spaCy)** with **cheminformatics** for a seamless user experience.

---

## ✨ Features

* **Text Query Interpretation**: Parse compound names from natural language inputs using **spaCy**.
* **CID Support**: Directly query molecules using **PubChem Compound IDs**.
* **3D Visualization**: Render interactive 3D molecular structures with atom labels using **py3Dmol**.
* **Chemical Properties**: Retrieve properties like molecular weight, XLogP, complexity, and hydrogen bond counts from **PubChem**.
* **Dark Theme UI**: Sleek, user-friendly interface for better visibility.
* **Robust Error Handling**: Graceful handling of invalid inputs, API errors, and visualization issues.

---

## 🚀 Installation

```bash
# Create a virtual environment (recommended)
python -m venv venv
# Activate the environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download spaCy language model
python -m spacy download en_core_web_sm
```

---

## 🌐 Usage

```bash
# Run the Streamlit app
streamlit run molecular_explorer.py
```

* Open the app in your browser (usually [http://localhost:8501](http://localhost:8501))
* Select input type: **"Compound Name"** or **"CID"**
* Enter a query (e.g., `"Acetylsalicylic acid"` or `"2244"`)
* Click **Visualize** to display:

  * 3D molecular structure with atom labels
  * IUPAC name and SMILES string
  * Chemical properties (MW, XLogP, etc.)

---

## 📊 Dependencies

* Python >= 3.8
* Streamlit
* RDKit
* py3Dmol
* spaCy
* Requests
* re

```bash
pip install streamlit rdkit py3dmol spacy requests
```

---

## 🔍 Example

### Input:

* Compound Name: `"Acetylsalicylic acid"`
* CID: `"2244"`

### Output:

* Interactive 3D molecular structure
* IUPAC Name, SMILES string
* Molecular Weight, Exact Mass, XLogP, Complexity
* Rotatable Bond Count, H-Bond Donors/Acceptors

---

## 🙌 Contributing

We welcome contributions!

1. **Fork** the repository
2. **Create** a feature branch:

   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Commit** your changes:

   ```bash
   git commit -m "Add your feature"
   ```
4. **Push** to your branch:

   ```bash
   git push origin feature/your-feature-name
   ```
5. **Open a Pull Request** with a clear description

---

## 📄 License

This project is licensed under the **MIT License**. See the `LICENSE` file for details.

---

## 📢 Contact

* Open an issue on this repository
* Connect via [YouTube - CartoonWorldVM](https://youtube.com/@cartoonworldvm9770)
* GitHub: [VipinMI2024](https://github.com/VipinMI2024)

---

## 📊 Acknowledgments

* **PubChem** for providing chemical data APIs
* **RDKit** for cheminformatics tools
* **py3Dmol** for molecular visualization
* **spaCy** for NLP
* **Streamlit** for web deployment

---

> Built with passion by **Vipin Mishra**
