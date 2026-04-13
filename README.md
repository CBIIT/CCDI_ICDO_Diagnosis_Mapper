# ICD-O Diagnosis Group Mapper
A specialized tool for mapping ICD-O diagnosis codes (4-digits) and terms to diagnostic groups(3-digit).

# Overview
This tool automates the classification of International Classification of Diseases (ICD) oncology diagnoses into their broader diagnostic categories. It is designed to accept user-provided data, validate the format, and return a file with additional columns containing group information.

### Output Example
The following table illustrates how the tool processes input identifiers into standardized output:

| Code | Term | Range | Group |
|:---|:---|:---|:---|
| `8000/0` | Neoplasm, benign | 800 | Neoplasms, NOS |
| `8000/1` | Tumor, NOS | 800 | Neoplasms, NOS |
| `8010/0` | Epithelial tumor | 801-804 | Epithelial neoplasms, NOS |
| `9380/3` | Glioma, malignant | 938-948 | Gliomas |

---

# Usage Instructions

### 1. File Preparation
Place your data file containing your diagnoses identifiers (codes or terms) in the input/ directory. The tool supports the following file formats:
* **CSV** (`.csv`)
* **TSV** (`.tsv`)
* **Excel** (`.xlsx`)

*An example input file (and mapping files) are located in the `data/` directory.*

### 2. Data Requirements
* **Column Selection:** If your file contains multiple columns, only the **first column** will be used for group identification; all other columns will be preserved in the output.
* **Single-Type Columns:** Each column must contain only one type of data (either all codes or all terms). Mixed data types within a single column are not supported.
* **ICD-O Standards:** 
    * **Codes:** Must follow the standard `####/#` format (e.g., `9380/3`).
    * **Terms:** Must match the master ICD-O glossary exactly including specific punctuation, capitalization, and spacing (e.g., `Glioma, malignant`).

### Input Example
You may choose to include either or both of these columns:

| Input Code | Input Term |
|:---|:---|
| `8000/0` | Neoplasm, benign |
| `8000/1` | Tumor, NOS | 800 |
| `8010/0` | Epithelial tumor |
| `9380/3` | Glioma, malignant |
---

## Mapping Logic
* **Code-Based Mapping:** The tool extracts the 3-digit prefix from the code to determine the parent diagnostic group.
* **Term-Based Mapping:** The tool performs an exact string match against the master ICD-O glossary (including synonyms) to retrieve the corresponding group.
* **Data Validation:** Any entry that do not meet formatting standards or lack a match in the glossary will be flagged in a "Comments" column in the final output.

---

# 🛠 Setup & Installation

### 1. Clone Repository
```bash
git clone https://github.com/CBIIT/CCDI_ICDO_Diagnosis_Mapper
cd CCDI_ICDO_Diagnosis_Mapper
```
### 2. Install Dependencies
```bash
pip install -r requirements.txt
```
### 3. Run the Tool
Ensure your file is in the input/ folder, then execute from the project root:
```bash
python scripts/icdo_group_mapper.py
```

# 🧪 Running Tests
To ensure the the script is working correctly, you can run the test script. This will automatically generate a test file, process it, and verify the output against expected ICD-O standards.

From the project root, run:

```bash
python tests/test_script.py
```
Note: This test will briefly create and then remove files in the input/ and output/ folders.