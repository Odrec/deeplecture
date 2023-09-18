#Functions for neighborhoods

from files_path_variables import neighborhoods_dir
from files_path_variables import all_cleaned_corr_text_files, all_cleaned_manually_text_files

from useful_functions import load_dicts_from_file, paint_term, save_dicts_to_file

from global_variables import NEIGHBORHOOD_SIZE

from pathlib import Path

import json, pdb

#Find the index or indexes of a term in a text
def find_indexes(text_data, term):
    try:
        return [i for i ,e in enumerate(text_data) if e == term]
    except ValueError:
        print(f"\nTerm {term} not found in the list.")
        return None

#Find the closest index or indexes to another index or indexes
#When corrected the indexes of the terms in the corrected text could change
def find_closest_indexes(index_original_list, index_target_list):
    closest_indexes = []

    for index_original in index_original_list:
        closest_index = None
        min_difference = float('inf')  # Initialize with a large value

        for index_target in index_target_list:
            difference = abs(index_original - index_target)
            if difference < min_difference:
                min_difference = difference
                closest_index = index_target

        closest_indexes.append(closest_index)

    return closest_indexes

#Function to get a list of neighborhoods based on a term
def get_neighborhoods_list(text_data, term, indexes, size=NEIGHBORHOOD_SIZE, paint=False):
    neighborhoods_list = []
    start_indexes_list = []
    end_indexes_list = []

    for a,index in enumerate(indexes):
        if index != -1:
            #Calculate the start and end indexes for this neighborhood
            start = max(0, index - size)
            #adds 1 for the term
            end = index + 1 + size
            start_indexes_list.append(start)
            end_indexes_list.append(end)
            
            #Getting the neighborhood
            utterances = text_data[start:end]

            #Painting the term if required
            if paint:
                utterances = paint_term(utterances, term)
            
            #Store neighborhood on list
            neighborhood = " ".join(utterances)
            neighborhoods_list.append(neighborhood)
    return neighborhoods_list, start_indexes_list, end_indexes_list

#Find the neighborhood of a term
def find_neighborhoods(text_data, term=None, indexes_original=-1, \
                       size=NEIGHBORHOOD_SIZE, search_close_to_index=False):
    
    #if indexes == -1:
    indexes = find_indexes(text_data, term)
    if not indexes: return None
    #else:
    #term = text_data[indexes_original[0]]
    
    #search the closest indexes to the original so only the corrected neighborhoods are searched
    #and avoid neighborhoods with terms that were not corrected
    if search_close_to_index and len(indexes) != len(indexes_original):
        indexes = find_closest_indexes(indexes_original, indexes)
        
    neighborhoods_list, start, end = get_neighborhoods_list(text_data, term, indexes, size)
    
    return neighborhoods_list, indexes, start, end

def search_save_neighborhoods(term_to_search, size=NEIGHBORHOOD_SIZE, databases=[all_cleaned_manually_text_files, all_cleaned_corr_text_files]):
    #Start variables to store all data
    start_indexes_dictionary = {}
    end_indexes_dictionary = {}
    indexes_term_dictionary = {}
    neighborhoods_dictionary = {}
    number_of_neighborhoods = 0

    #Control which documents have been processed
    processed_documents = []

    #Sometimes we want to search for neighborhoods from different sources (where a source is more "clean" than another for example)
    #Always set the "cleaner" database in the first element of the databases list
    for d in databases:

        #Loop over all cleaned and corrected files
        for file in d:
            
            #Open a file and extract its content
            with open(file) as json_file:
                text_data = json.loads(json_file.read())
    
            for document in text_data.keys():

                if document not in processed_documents:
                    if term_to_search in set(text_data[document]):
                    
                        neighborhoods_list, indexes, start, end = find_neighborhoods(text_data[document], term=term_to_search, size=size)
        
                        #Fill in the variables with the data
                        neighborhoods_dictionary[document] = neighborhoods_list
                        indexes_term_dictionary[document] = indexes
                        number_of_neighborhoods += len(neighborhoods_list)
        
                        #Create a list of lists of start and finish indexes for each neighborhood
                        start_indexes_dictionary[document] = start
                        end_indexes_dictionary[document] = end
    
                        processed_documents.append(document)


    print(f"\nFound {number_of_neighborhoods} of the term {term_to_search} in the text data.")

    save = input("\nSave the list of neighborhoods? (yes/no default no):")

    if save == "yes" or save == "y":

        #Collect all dictionaries in a file
        dicts = [neighborhoods_dictionary, indexes_term_dictionary, start_indexes_dictionary, end_indexes_dictionary]
        
        #name the file with the length of neighborhoods and the term
        filename = Path(neighborhoods_dir,f"neighborhoods-{term_to_search}-{NEIGHBORHOOD_SIZE}.pkl")
        
        #save the file
        save_dicts_to_file(dicts, filename)
        
        print(f"\nThe file {filename} was succesfully saved.")
    
    else:
        print(f"\nThe neighborhoods were not saved.")

    return neighborhoods_dictionary, indexes_term_dictionary, start_indexes_dictionary, end_indexes_dictionary

def load_neighborhoods():

    #Get all the neighborhood saved files
    all_neighborhood_files = neighborhoods_dir.glob("*.pkl")
    
    #Initialize dict variable to save terms and length of neighborhoods
    files_info_dict = {}
    
    #Loop on all the neighborhoods
    for n_file in all_neighborhood_files:
        
        #Get the name of the file without extension
        name_of_file = n_file.stem
        
        #Split the name with the dashes
        name_of_file_splitted = name_of_file.split('-')
        
        #Get the term
        term = name_of_file_splitted[1]
        
        #Get the length of neighborhoods
        length_of_neighborhoods = name_of_file_splitted[2]
        
        #Check if the term already exists on the dict, if it doesn't add to dict and initializes list
        if term not in files_info_dict.keys():
            files_info_dict[term] = []
            
        #Add new length to existing file info
        files_info_dict[term].append(length_of_neighborhoods)
            
    print("\nThese are the available terms for neighborhood files:\n")
    
    #Gets all the terms
    terms_of_saved_files = list(files_info_dict.keys())
    
    #Loop and print the terms info
    for term in terms_of_saved_files:
        
        #Print the term
        print(f"-{term}")
    
    #Ask which term neighborhoods you want to load 
    term_of_neighborhoods = input("\nThe neighborhoods from which term do you want to load? ")
    
    #Check if the term exists
    if term_of_neighborhoods in terms_of_saved_files:
        
        print(f"\nThese are the lengths available for neighborhood files of the term {term_of_neighborhoods}:\n")
        
        neigh_lengths = files_info_dict[term_of_neighborhoods]
        
        for length in neigh_lengths:
            print(f"-{length}")
        
        #Ask which length of neighborhoods you want to load 
        length_of_neighborhoods = input(f"\nWhich neighborhoods length from term {term_of_neighborhoods} do you want to load? ")
        
        if length_of_neighborhoods in neigh_lengths:
            
            filename = Path(neighborhoods_dir,f"neighborhoods-{term_of_neighborhoods}-{length_of_neighborhoods}.pkl")
            
            print(f"\nLoading file {filename}...")
            
            dictionaries = load_dicts_from_file(filename)
                    
            neighborhoods_dictionary = dictionaries[0][0]
            indexes_term_dictionary = dictionaries[0][1]
            start_indexes_dictionary = dictionaries[0][2]
            end_indexes_dictionary = dictionaries[0][3]
            
            #Set variables for other cells
            term_to_search = term_of_neighborhoods
            NEIGHBORHOOD_SIZE = int(length_of_neighborhoods)
                    
            return neighborhoods_dictionary, indexes_term_dictionary, start_indexes_dictionary, end_indexes_dictionary, length_of_neighborhoods, term_to_search
            
        else:
            print(f"\nThere are no files available for neighborhoods of the term {term_of_neighborhoods} with length {length_of_neighborhoods}.")
    else:
        print(f"\nThere are no files available for the term {term_of_neighborhoods}.")

    return None, None, None, None, None, None


