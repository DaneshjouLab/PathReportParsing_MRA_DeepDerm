# PathReportParsing_MRA_DeepDerm

This repo provides a tool for automatically extracting and processing pathology report data for the MRA-DeepDerm Study. The module is tailored to extract structured data for use in research and clinical applications.

---

## Features

- **Accession Number Extraction**: Automatically identifies and extracts accession numbers from pathology text.
- **Specimen Information Parsing**: Organizes specimen identifiers and their descriptions into a structured format.
- **Clinical Impressions and Diagnoses**: Captures detailed impressions and diagnostic details for each specimen.
- **Microscopic Descriptions**: Extracts findings from microscopic sections of pathology reports.
- **Batch Processing Support**: Processes multiple pathology reports from an input excel file.

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

## Usage

1. Prepare Your Input File
    Ensure your input file is an Excel file containing a sheet named "Per Lesion".
    Include a column titled Path Report Text containing the pathology report text to be processed.

2. Run the Notebook
    Update the input_file path to the location of your Excel file:
    ```bash
    input_file = "/path/to/the/excel/file"
    ```

3. Execute the notebook or script. If the Path Report Text column is present, the script will process the data and save the results to a new file named Processed_Pathology_Reports.xlsx.

4. Check the Output
    The processed data will be saved as an Excel file in the working directory.
    Example file name: Processed_Pathology_Reports.xlsx.


```python
# Import packages
import pandas as pd
from utils import process_pathology_reports

# Load the Excel file into a DataFrame
input_file = "/path/to/the/excel/file"
df = pd.read_excel(input_file, sheet_name="Per Lesion", engine="openpyxl")

# Ensure the 'Path Report Text' column exists
if "Path Report Text" not in df.columns:
    processed_df = process_pathology_reports(df)

    # Save the processed DataFrame to a new Excel file
    output_file = "Processed_Pathology_Reports.xlsx"
    processed_df.to_excel(output_file, engine="openpyxl", index=False)
    print(f"Processed data saved to {output_file}")
else:
    print("Error: 'Path Report Text' column not found in the input file.")
```
