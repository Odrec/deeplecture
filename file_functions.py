from useful_functions import tokenize
from files_path_variables import all_cleaned_manually_text_files, all_cleaned_corr_text_files
import json, pdb
from pathlib import Path

def insert_neighborhoods_into_files(neighborhoods_dict, start_indexes_dict, end_indexes_dict, databases=[all_cleaned_manually_text_files, all_cleaned_corr_text_files]):

    #Get the list of documents that have neighborhoods
    neighborhoods_documents_list = list(neighborhoods_dict.keys())

    #Control which documents have been processed and how many neighborhoods
    processed_documents = []
    number_of_saved_neighborhoods = 0

    #We want to insert the neighborhoods in the files that are cleaner first so the databases list uses first the files that are cleaner
    for d in databases:

        for file in d:
            
            #Open a file and extract its content
            with open(file) as json_file:
                text_data = json.loads(json_file.read())
    
            #Controls if there was a change in the documents to control if it gets saved
            change = False
    
            #Loop the documents in the file
            for document in text_data.keys():
    
                #Check the document hasn't already been processed and that it has neighborhoods to check for
                if document not in processed_documents and document in neighborhoods_documents_list:

                    #Go through all the neighborhoods in the document
                    for n, neighborhood in enumerate(neighborhoods_dict[document]):
    
                        #Get the start and end indexes of the neighborhood
                        start_index = start_indexes_dict[document][n]
                        end_index = end_indexes_dict[document][n]
    
                        original_neighborhood = text_data[document][start_index:end_index]
    
                        #Get the extracted neighborhood and tokenize it to add it to the original tokenized text
                        extracted_neighborhood = tokenize(neighborhoods_dict[document][n])
    
                        #Check if the original neighborhood and extracted neighborhood are different (modified)
                        if not original_neighborhood == extracted_neighborhood:
    
                            #Save this file
                            change = True
    
                            print(f"Replacing neighborhood number {n} of document {document}. Number of processed documents: {len(document)}")
                            number_of_saved_neighborhoods += 1
                            print(f"Total number of changed neighborhoods: {number_of_saved_neighborhoods}")
    
                            #Replace neighborhood in the text data
                            #print("NEW",extracted_neighborhood)
                            #print("\nOLD",original_neighborhood)
                            text_data[document][n] = text_data[document][:start_index] + extracted_neighborhood + text_data[document][end_index+1:]
    
                        #Add the document as processed
                        processed_documents.append(document)

                #Save file if any of the documents was changed
                if change:

                    #For now save in another folder to check if working fine
                    name_of_file = file.name
                    above_path = file.parent.parent
                    newly_edited_path = Path(above_path,'newly_edited')
                    # Create the directory if it doesn't exist
                    newly_edited_path.mkdir(parents=True, exist_ok=True)
                    file_path = newly_edited_path / name_of_file
                    
                    with open(file_path, "w") as json_file:
                        json.dump(text_data, json_file)

                    print(f"FIle {file_path} saved succesfully!")

    return text_data

    