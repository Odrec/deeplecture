import json
from pathlib import Path

#Load all necessary paths
root_dir = Path("/media/odrec/TOSHIBA EXT/")
files_dir = Path(root_dir, "files_nlp_deeplecture_2/")
pdf_dir = Path(root_dir, "Korpus PFDs/")
metadata_dir = Path(files_dir, "csv")
corr_dir = Path(files_dir, "corr")
splitted_data_folder = Path(corr_dir,"all_cleaned_text")
corrected_data_folder = Path(corr_dir,"all_cleaned_corr_text")
manually_corrected_data_folder = Path(corr_dir,"all_cleaned_manually_corr_text")
neighborhoods_dir = Path(corr_dir, "neighborhoods")

#Path to all metadata file
metadata_file = Path(metadata_dir, "all_codes.csv.current")

#Path to rules file
path_to_rules_file = Path(corr_dir, "rules_for_values.csv")

#Load all uncorrected text
all_cleaned_text_files = list(splitted_data_folder.glob("*.json"))

#Load all automatically the corrected text
all_cleaned_corr_text_files = list(corrected_data_folder.glob("*.json"))

#Load all manually the corrected text
all_cleaned_manually_text_files = list(manually_corrected_data_folder.glob("*.json"))

# Load corrections
all_corrections_file = Path(corr_dir, "homogenize.corr")
with open(all_corrections_file) as json_file:
    correction_data = json.loads(json_file.read())

correction_data_keys = list(correction_data.keys())
correction_data_values = list(correction_data.values())