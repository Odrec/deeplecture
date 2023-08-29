import json
from pathlib import Path

#Load all necessary paths
root_dir = Path("/media/odrec/TOSHIBA EXT/files_nlp_deeplecture_2/")
pdf_dir = Path("/media/odrec/TOSHIBA EXT/Korpus PFDs/")
corr_dir = Path(root_dir, "corr")
splitted_data_folder = Path(corr_dir,"all_cleaned_text")
corrected_data_folder = Path(corr_dir,"all_cleaned_corr_text")
manually_corrected_data_folder = Path(corr_dir,"all_cleaned_manually_corr_text")
neighborhoods_dir = Path(corr_dir, "neighborhoods")

#Path to rules file
path_to_rules_file = Path(corr_dir, "rules_for_values.csv")

#Load all uncorrected text
all_cleaned_text_files = list(splitted_data_folder.glob("*.json"))

#Load all the corrected text
all_cleaned_corr_text_files = list(corrected_data_folder.glob("*.json"))

# Load corrections
all_corrections_file = Path(corr_dir, "homogenize.corr")
with open(all_corrections_file) as json_file:
    correction_data = json.loads(json_file.read())

correction_data_keys = list(correction_data.keys())
correction_data_values = list(correction_data.values())