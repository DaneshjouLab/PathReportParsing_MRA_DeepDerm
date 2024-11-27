# PathReportParsing_MRA_DeepDerm

This repo provides a tool for automatically extracting and processing pathology report data for the MRA-DeepDerm Study. The module is tailored to extract structured data for use in research and clinical applications.

---

## Features

- **Accession Number Extraction**: Automatically identifies and extracts accession numbers from pathology text.
- **Specimen Information Parsing**: Organizes specimen identifiers and their descriptions into a structured format.
- **Clinical Impressions and Diagnoses**: Captures detailed impressions and diagnostic details for each specimen.
- **Microscopic Descriptions**: Extracts findings from microscopic sections of pathology reports.
- **Batch Processing Support**: Processes multiple pathology reports in a single run using a pandas DataFrame.

---

## Installation

1. Clone the repository:
   ```bash
   git clone git@github.com:DaneshjouLab/PathReportParsing_MRA_DeepDerm.git
   cd PathReportParsing_MRA_DeepDerm
    ```
    
2. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

