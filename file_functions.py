from useful_functions import tokenize
from files_path_variables import all_cleaned_manually_text_files, all_cleaned_corr_text_files
import json, pdb, re
from pathlib import Path

def modify_neighborhoods(document, neighborhoods_dict, start_indexes_dict, end_indexes_dict, text_data, processed_documents, number_of_saved_neighborhoods, modified=False):

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
            modified = True

            print(f"\nReplacing neighborhood number {n} of document {document}. Number of processed documents: {len(processed_documents)}")
            number_of_saved_neighborhoods += 1
            print(f"Total number of changed neighborhoods: {number_of_saved_neighborhoods}")

            #Replace neighborhood in the text data
            text_data[document] = text_data[document][:start_index] + extracted_neighborhood + text_data[document][end_index+1:]

    return text_data, modified, number_of_saved_neighborhoods

def insert_neighborhoods_into_files(neighborhoods_dict, start_indexes_dict, end_indexes_dict, databases=[all_cleaned_manually_text_files, all_cleaned_corr_text_files], single_document = None):

    #Get the list of documents that have neighborhoods
    neighborhoods_documents_list = list(neighborhoods_dict.keys())

    #Control which documents have been processed and how many neighborhoods
    processed_documents = []

    #Maybe define it as set in case a document is repeated but check first to see if there are repeated cases
    processed_files = []
    
    number_of_saved_neighborhoods = 0

    #Controls if there was a change in the documents to control if it gets saved
    modified = False

    #We want to insert the neighborhoods in the files that are cleaner first so the databases list uses first the files that are cleaner
    for d in databases:

        for file in d:

            #Open a file and extract its content
            with open(file) as json_file:
                text_data = json.loads(json_file.read())

            #If only one document to save was provided
            if single_document:
                #If the document exists in the file and in the neighborhoods list then modify it
                if single_document in text_data and single_document in neighborhoods_documents_list:
                    print(f"\nModifying document {single_document} in file {file}.\n")
                    text_data, modified, number_of_saved_neighborhoods = modify_neighborhoods(single_document, neighborhoods_dict, start_indexes_dict, end_indexes_dict, text_data, processed_documents, number_of_saved_neighborhoods)
                
            #Else process all documents
            else:
                #Loop the documents in the file
                for document in text_data.keys():
        
                    #Check the document hasn't already been processed and that it has neighborhoods to check for
                    if document not in processed_documents and document in neighborhoods_documents_list:
    
                        text_data, modified, number_of_saved_neighborhoods = modify_neighborhoods(document, neighborhoods_dict, start_indexes_dict, end_indexes_dict, text_data, processed_documents, number_of_saved_neighborhoods, modified)
        
                        #Add the document as processed
                        processed_documents.append(document)

            #Save file if any of the documents was changed
            if modified:
                
                with open(Path(file.parent,"../newly_edited/",file.name), "w") as json_file:
                    json.dump(text_data, json_file)

                print(f"\nFile {file} saved succesfully!")

                #If it's a single document then stop the loop
                if single_document: 
                    print("\nProcessing finished.")
                    return text_data

                #Set modification variable back to False
                modified = False

                processed_files.append(file.name)

    print("Finished processing all files!")

    return text_data


# Create a function to check and modify strings
def check_and_modify_string(input_string, term):

    # Define the regular expression to look for in the string with word boundaries
    pattern = re.compile(r'\b' + re.escape(term) + r'\b', re.IGNORECASE)

    # Use re.sub to replace the matched term with spaces around it
    modified_str = pattern.sub(' ' + term + ' ', input_string)

    # Remove extra spaces that may have been added by the previous operation
    modified_str = ' '.join(modified_str.split())

    return modified_str

#Separates the term inside each word if it exists
#For example if the term to look for is naturaleza and it finds the word "grandenaturaleza" in one of the words 
#then it returns "grande naturaleza" as two separate terms and saves the file with the separated terms
def separate_term(term, databases=[all_cleaned_manually_text_files, all_cleaned_corr_text_files]):

    # Define compiled regex pattern
    #pattern = re.compile(r'\b'+term+'\b', re.IGNORECASE)

    #Control which documents have been processed and how many neighborhoods
    processed_documents = []

    #Control which files and documents were modified
    modified_files = []
    modified_documents = []

    #Maybe define it as set in case a document is repeated but check first to see if there are repeated cases
    processed_files = []

    modified = False

    #We want to insert the neighborhoods in the files that are cleaner first so the databases list uses first the files that are cleaner
    for d in databases:

        for file in d:

            modified = False  # Flag to track if any modification was made in this file

            print(f"Processing file {file.name} in directory {file.parent.name}.")
            #Open a file and extract its content
            with open(file) as json_file:
                text_data = json.loads(json_file.read())
    
            #Loop the documents in the file
            for document, text in text_data.items():

                #Check the document hasn't already been processed and that it has neighborhoods to check for
                if document not in processed_documents:

                    if isinstance(text, list):
                        # Iterate over lists
                        for i, item in enumerate(text):
                            modified_item = check_and_modify_string(item, term)
                            if modified_item != item:
                                text[i] = modified_item
                                modified = True
                                modified_documents.append(document)

                processed_documents.append(document)

            # Save the modified dictionary back to the file if any modification was made
            if modified:
                with open(file, 'w') as json_file:
                    json.dump(text_data, json_file)
                modified_files.append(file)
                modified = False

            processed_files.append(file)


    # Print the list of modified files
    print(f"\n{len(processed_documents)} documents were processed from {len(processed_files)} JSON files. This is the list of {len(modified_files)} modified files where {len(modified_documents)} modified documents where the term {term} was found and separated:\n")
    for fil in modified_files:
        print(fil)


                

    

    