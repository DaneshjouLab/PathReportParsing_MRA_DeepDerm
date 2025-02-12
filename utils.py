# This source file is part of the Daneshjou Lab projects
#
# SPDX-FileCopyrightText: 2024 Stanford University and the project authors (see AUTHORS.md)
#
# SPDX-License-Identifier: MIT

"""
This module provides tools for extracting and processing pathology report data. 
The primary functions enable the extraction of accession numbers, specimen details, 
clinical impressions, diagnoses, and microscopic descriptions from pathology report text. 
"""

# Import dependencies
import re
import pandas as pd


def extract_accession_and_specimens_df(text):
    """
    Extracts the Accession Number and Specimens from the path report text in two formats
    and returns them in a DataFrame.

    Args:
        text (str): The input text containing the path report details.

    Returns:
        pd.DataFrame: A DataFrame with columns "Accession No", "Specimen Identifier", and
            "Specimen Description".
    """
    # Initialize storage for data
    accession_no = None
    specimen_data = []

    # Extract the Accession Number
    accession_match = re.search(r"Accession No:\s*(\S+)", text, re.IGNORECASE)
    if accession_match:
        accession_no = accession_match.group(1).strip()

    # Extract specimens after "SPECIMEN SUBMITTED:"
    specimen_section_match = re.search(
        r"SPECIMEN SUBMITTED:\s*(.+?)(?:\n\n|\Z)", text, re.IGNORECASE | re.DOTALL
    )
    if specimen_section_match:
        specimen_section = specimen_section_match.group(1).strip()

        # Check for format with identifiers (e.g., A., B., etc.)
        specimens_with_identifiers = re.findall(
            r"([A-Z])\.\s*([^\n]+)", specimen_section
        )
        if specimens_with_identifiers:
            for match in specimens_with_identifiers:
                specimen_id, specimen_desc = match[0], match[1].strip()
                specimen_data.append(
                    {
                        "Accession No": accession_no,
                        "Specimen Identifier": specimen_id,
                        "Specimen Description": specimen_desc,
                    }
                )
        else:
            # Format without identifiers (e.g., just list of specimens)
            specimens = specimen_section.split("\n")
            for index, specimen_desc in enumerate(specimens, start=1):
                specimen_data.append(
                    {
                        "Accession No": accession_no,
                        "Specimen Identifier": chr(
                            64 + index
                        ),  # Generate identifiers A, B, C, etc.
                        "Specimen Description": specimen_desc.strip(),
                    }
                )

    return pd.DataFrame(specimen_data)


def remove_text_after_newline(cell_text):
    """
    Removes all text starting from the first newline symbol ("\n") in the given string.

    Args:
        cell_text (str): The text to clean.

    Returns:
        str: The cleaned text.
    """
    if not isinstance(cell_text, str):
        return cell_text  # Ensure we handle non-string cases safely
    return cell_text.split("\n")[
        0
    ].strip()  # Keep only the part before the first newline


def extract_clinical_impression(text):
    """
    Extracts Clinical Impression information for each specimen. If no specimen-specific
    identifiers are found after "CLINICAL IMPRESSION:", assumes the same text applies to all
    specimens.

    Args:
        text (str): The input text containing the Clinical Impression section.

    Returns:
        dict: A dictionary where keys are specimen identifiers (e.g., A, B) and values are the
          impressions.
    """
    # Step 1: Extract Specimen Mapping from "SPECIMEN SUBMITTED"
    specimen_mapping = {}
    specimen_submitted_section = re.search(
        r"SPECIMEN SUBMITTED:\s*(.+?)(?=\n\n|DIAGNOSIS:)",
        text,
        re.IGNORECASE | re.DOTALL,
    )
    if specimen_submitted_section:
        specimens = re.findall(
            r"([A-Z])[\.\):]?\s*(.+)", specimen_submitted_section.group(1)
        )
        for idx, (identifier, _) in enumerate(specimens, start=1):
            specimen_mapping[str(idx)] = identifier.strip()  # Map #1, #2 to A, B, etc.
            specimen_mapping[identifier.strip()] = (
                identifier.strip()
            )  # Map A, B directly

    # Initialize impressions dictionary
    impressions = {specimen: "" for specimen in specimen_mapping.values()}

    # Step 2: Locate the Clinical Impression section
    clinical_impression_section = re.search(
        r"CLINICAL IMPRESSION:\s*(.+?)(?=\n[A-Z ]+:|$)",  # Stop at the next section or end of text
        text,
        re.IGNORECASE | re.DOTALL,
    )
    if clinical_impression_section:
        clinical_impression_text = clinical_impression_section.group(1).strip()

        # Step 3: Detect identifiers
        identifiers = re.findall(
            r"([A-Z]\)|[A-Z]:|#\d+-|Lesion [A-Z])",
            clinical_impression_text,
            re.IGNORECASE,
        )

        if identifiers:
            # Step 4: Extract information for each identifier
            for idx, identifier in enumerate(identifiers):
                # Define the start of the identifier
                start_pos = clinical_impression_text.find(identifier)

                # Define the end of the identifier's information (next identifier or end of text)
                end_pos = (
                    clinical_impression_text.find(identifiers[idx + 1])
                    if idx + 1 < len(identifiers)
                    else len(clinical_impression_text)
                )

                # Extract the text for this identifier
                impression_text = clinical_impression_text[
                    start_pos + len(identifier) : end_pos
                ].strip()

                # Map to corresponding specimen, cleaning up format
                # (e.g., "A)" -> "A", "A:" -> "A", "#1-" -> "1")
                clean_identifier = (
                    re.sub(r"[\)\-:#]", "", identifier).replace("Lesion ", "").strip()
                )
                if clean_identifier in specimen_mapping:
                    # mapped_id = specimen_mapping[clean_identifier]
                    impressions[specimen_mapping[clean_identifier]] += (
                        impression_text.strip() + " "
                    )
        else:
            # No identifiers found.
            for specimen in impressions.keys():
                impressions[specimen] = clinical_impression_text

    # Clean up impressions (remove extra spaces)
    impressions = {k: v.strip() for k, v in impressions.items()}

    return impressions


def add_microscopic_description(text, specimen_data):
    """
    Extract and populate the Microscopic Description column in the DataFrame.

    Args:
        text (str): The input text containing the Path Report.
        specimen_data (pd.DataFrame): The DataFrame containing specimen details.

    Returns:
        pd.DataFrame: Updated DataFrame with Microscopic Description.
    """
    # Capture text until the next section header or end of text
    micro_desc_section = re.search(
        r"MICROSCOPIC DESCRIPTION:\s*(.+?)(?=\n[A-Z ]+:|$)",
        text,
        re.IGNORECASE | re.DOTALL,
    )
    if not micro_desc_section:
        return specimen_data

    micro_desc_text = micro_desc_section.group(1).strip()

    # Try to match specimen-specific identifiers and descriptions
    micro_desc_matches = re.findall(
        r"^([A-Z][\.\):])\s*(.*?)\s*-\s*(.+)$",  # Match identifier, location, and description
        micro_desc_text,
        re.IGNORECASE | re.DOTALL | re.MULTILINE,
    )

    if micro_desc_matches:
        # Case: Multiple specimens with identifiers
        for match in micro_desc_matches:
            specimen_id, _, description = (
                match[0][0],
                match[1].strip(),
                match[2].strip(),
            )
            specimen_data.loc[
                specimen_data["Specimen Identifier"] == specimen_id,
                "Microscopic Description",
            ] = description
    else:
        # Case: No valid identifiers and apply the entire description to all specimens
        for specimen in specimen_data["Specimen Identifier"]:
            specimen_data.loc[
                specimen_data["Specimen Identifier"] == specimen,
                "Microscopic Description",
            ] = micro_desc_text

    return specimen_data


def extract_specimen_details(text):
    """
    Extracts details (Diagnosis, Microscopic Description, Clinical Impression) for each specimen
    in the Path Report Text. Handles all identifiers and respects line breaks for Diagnosis and
    Impressions.

    Args:
        text (str): The input text containing the Path Report.

    Returns:
        pd.DataFrame: A DataFrame with columns:
                      - "Specimen Identifier"
                      - "Specimen Description"
                      - "Diagnosis"
                      - "Microscopic Description"
                      - "Clinical Impression"
    """
    specimen_data = extract_accession_and_specimens_df(text)

    # Initialize columns
    specimen_data["Diagnosis"] = ""
    specimen_data["Microscopic Description"] = ""
    specimen_data["Clinical Impression"] = ""

    specimen_mapping = {
        str(idx + 1): row["Specimen Identifier"]
        for idx, row in specimen_data.iterrows()
    }
    specimen_mapping.update(
        {
            row["Specimen Identifier"]: row["Specimen Identifier"]
            for _, row in specimen_data.iterrows()
        }
    )

    # Extract Diagnosis
    diagnosis_matches = re.findall(
        r"([A-Z])[\.\):]?\s*(.+?)\n\s*--\s*(.+?)(?=\n[A-Z][\.\):]|\n\n|$)",
        text,
        re.IGNORECASE | re.DOTALL,
    )
    for match in diagnosis_matches:
        specimen_id, _, diagnosis_text = (
            match[0],
            match[1].strip(),
            match[2].strip(),
        )
        specimen_data.loc[
            specimen_data["Specimen Identifier"] == specimen_id, "Diagnosis"
        ] = diagnosis_text

    # Extract Microscopic Description
    specimen_data = add_microscopic_description(text, specimen_data)

    # Extract Clinical Impressions
    clinical_impressions = extract_clinical_impression(text)
    # Regular expression for valid identifier formats
    valid_identifier_pattern = r"^[A-Z][\)\.:]|#[0-9]+$"

    for specimen_id, impression_text in clinical_impressions.items():
        # Check if specimen_id does not match any valid identifier format
        if not re.match(valid_identifier_pattern, specimen_id):
            # Populate all rows with the field value
            specimen_data["Clinical Impression"] = impression_text
        else:
            # Populate only matching rows
            specimen_data.loc[
                specimen_data["Specimen Identifier"] == specimen_id,
                "Clinical Impression",
            ] = impression_text

    # Clean newline artifacts
    for column in ["Diagnosis", "Microscopic Description", "Clinical Impression"]:
        specimen_data[column] = specimen_data[column].apply(remove_text_after_newline)

    return specimen_data


def process_pathology_reports(df):
    """
    Processes a DataFrame of pathology reports to extract structured details for
    each specimen mentioned in the reports.

    Args:
        df (pd.DataFrame): A DataFrame with a "Path Report Text" column.

    Returns:
        pd.DataFrame: A DataFrame where each row corresponds to a specimen with
                      columns for extracted details and original data.
    """
    collected_data = pd.DataFrame()
    # Replace NaN values with an empty string before processing
    df["Path Report Text"] = df["Path Report Text"].fillna("")

    # Process each row in the DataFrame
    for _, row in df.iterrows():
        # Extract details from the pathology report text
        extracted_df = extract_specimen_details(row["Path Report Text"])

        # Ensure extracted_df is not empty
        if not extracted_df.empty:
            # Replicate the original row for each new extracted row
            original_row = row.to_frame().T
            replicated_rows = pd.concat(
                [original_row] * len(extracted_df), ignore_index=True
            )

            # Combine the replicated original rows with the new columns
            combined_df = pd.concat(
                [
                    replicated_rows.reset_index(drop=True),
                    extracted_df.reset_index(drop=True),
                ],
                axis=1,
            )

            # Append to the collected_data DataFrame
            collected_data = pd.concat([collected_data, combined_df], ignore_index=True)

    return collected_data
