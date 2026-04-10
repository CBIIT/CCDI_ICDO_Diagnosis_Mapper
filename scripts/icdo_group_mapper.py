# ICD-O Group Mapper
# This script takes user-supplied ICD-O codes or terms and returns their group information

# Data Loading: Loads mapping files and looks for any CSV, TSV, or Excel file in the /input directory
# load packages 
import pandas as pd
import re
from datetime import datetime
import glob
import os
import sys
from pathlib import Path

# set up error-handling
import logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def main():
    # obtain files and paths
    DIRECTORY = Path(__file__).resolve().parent.parent
    code_mapping_file = pd.read_csv(DIRECTORY / "data" / "code_mapping_file.tsv", sep='\t')  # doesn't have synonyms (if the user supplies codes)
    term_mapping_file = pd.read_csv(DIRECTORY / "data" / "term_mapping_file.tsv", sep='\t')  # has synonyms (if the user supplies terms)

    # look for any csv, tsv, or excel file in the input folder
    input_dir = DIRECTORY / "input"
    input_files = list(input_dir.glob("*.[ct]sv")) + list(input_dir.glob("*.xlsx"))

    if not input_files:
        logger.error("No input files found in the /input directory.")
        sys.exit()
    else:
        file_to_process = input_files[0]
        logger.info(f"Processing: {os.path.basename(file_to_process)}")
        if file_to_process.suffix.lower() == '.xlsx':
            user_input = pd.read_excel(file_to_process)
        else:
            user_input = pd.read_csv(file_to_process, sep=None, engine='python')


    ### Validation: Check if user-supplied data are codes or terms, and if they match the mapping files.
    data = user_input.iloc[:,0].astype(str).str.strip()
    invalid_rows = []

    code_pattern = r'^\d{4}/\d$'
    term_list = term_mapping_file['term']

    # if the user supplies codes
    if data.str.match(code_pattern).any():
        mapping_file = code_mapping_file
        key = 'code'
        user_input = user_input.rename(columns={user_input.columns[0]: key})
        if data.str.match(code_pattern).all():
            logger.info("✅ Validation Success: All entries are codes.")
        else:
            invalid_rows = data[~data.str.match(code_pattern)].tolist()
            logger.warning(f"❌ Recognition Error: Some rows do not follow ####/# format.")
            
    # if the user supplies terms
    elif data.isin(term_list).any():
        mapping_file = term_mapping_file
        key = 'term'
        user_input = user_input.rename(columns={user_input.columns[0]: key})
        if data.isin(term_list).all():
            logger.info("✅ Validation Success: All entries are terms.")
        else: 
            invalid_rows = data[~data.isin(term_list)].tolist()
            logger.warning(f"❌ Recognition Error: Some terms do not match ICD-O exactly.")
            
    # if user-supplied data is not recognized
    else:
        logger.error(f"❌ Recognition Error: No entries were recognized.")
        logger.error(f" Codes must follow the format ####/#. Terms must match ICD-O terms exactly (including commas/caps/spaces).")       

    if invalid_rows:
        logger.warning(f"Some entries were not recognized: {invalid_rows}") 

    # if second column is supplied, accept as terms/codes
    if len(user_input.columns) > 1:
        col2_data = user_input.iloc[:, 1].astype(str).str.strip()
        col2_name = user_input.columns[1]

        if key == 'code' and col2_data.isin(term_list).any():
            user_input = user_input.rename(columns={col2_name: 'term'})
            logger.info("✅ Column 2 recognized as terms.")
        
        elif key == 'term' and col2_data.str.match(code_pattern).any():
            user_input = user_input.rename(columns={col2_name: 'code'})
            logger.info("✅ Column 2 recognized as codes.")
        
        else:
            logger.warning(f"Column 2 ('{col2_name}') not recognized as ICD-O data. Keeping as-is.")


    ### Mapping: Map user-supplied data to the other column (code <-> term) using the mapping files.

    # look up the group information
    output = user_input.merge(
        mapping_file[['code', 'term', 'range', 'group']],
        on = key,
        how = 'left'
        )

    # remove duplicate columns, keeping user's terms
    cols_to_drop = [col for col in output.columns if col.endswith('_y')]
    output = output.drop(columns=cols_to_drop)
    output.columns = [col.replace('_x', '') for col in output.columns]


    ### Reporting: Save the output file and log summary statistics about the mapping results.

    # add comments column for unmatched entries
    total = len(output)
    unmatched = len(output[output['group'].isna()])
    if unmatched > 0:
        output['Comments'] = ""
        output.loc[output['group'].isna(), 'Comments'] = "No diagnosis group match found"
    logger.info(f"\nSummary:")
    logger.info(f"Total entries: {total}")
    logger.info(f"Successfully mapped: {total - unmatched}")
    logger.info(f"Unmatched: {unmatched}")

    # generate a timestamp string 
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")

    # create output file name
    original_filename = Path(file_to_process).stem
    tsv_filename = f"{DIRECTORY}/output/{original_filename}_icdomapper_output_{timestamp}.tsv"

    # export the file
    output.to_csv(tsv_filename, sep='\t', index=False)
    logger.info(f"✅ Files exported successfully: {tsv_filename}")

if __name__ == "__main__":
    main()