import nltk, string, fitz, pickle, json
from pathlib import Path
from ipywidgets import widgets

from global_variables import NEIGHBORHOOD_SIZE, IMAGE_WIDTH, IMAGE_HEIGHT
from files_path_variables import correction_data, correction_data_keys, pdf_dir

from nltk.corpus import stopwords
from nltk.corpus import words

#Function to tokenize spanish text
def tokenize(text):
    return nltk.word_tokenize(text, language='spanish')

#Function to find key based on value
def find_key(dictionary, search_value):
    for key, value in dictionary.items():
        if search_value in value:
            return key
    return None

#paint a specific term in the text
def paint_term(utterances, term=None, index=-1, color='red'):
    utterances_copy = utterances.copy()
    if index == -1:
        idxs = [i for i, x in enumerate(utterances_copy) if x.replace(',', '') == term or x.replace('.', '') == term]
    elif type(index) is list: idxs = index
    elif type(index) is int: idxs = [index]
    for i in idxs:
        #print(f"\nPosition of the term in text segment: {i}")
        utterances_copy[i] = f'<span style="color:{color}">{utterances_copy[i]}</span>'
    return utterances_copy

#delete painting from text
def remove_paint(text):
    return re.sub(r'<.*?>', '', text)

#Function to get a list of neighborhoods based on a term
def get_neighborhoods_list(text_data, term, indexes, size=NEIGHBORHOOD_SIZE):
    neighborhoods_list = []
    start_indexes_list = []
    finish_indexes_list = []

    for a,index in enumerate(indexes):
        if index != -1:
            #Calculate the start and finish indexes for this neighborhood
            start = max(0, index - size)
            finish = index + len(term) + size
            start_indexes_list.append(start)
            finish_indexes_list.append(finish)
            
            #Painting the term
            utterances = text_data[start:finish]
            utterances = paint_term(utterances, term)
            
            #Store neighborhood on list
            neighborhood = " ".join(utterances)
            neighborhoods_list.append(neighborhood)
    return neighborhoods_list, start_indexes_list, finish_indexes_list

#Returns the value of the neighborhood modified in the textarea
def return_textarea_value(textarea):
    return textarea.value

#Search for a pdf and return its path
def search_pdf(document_name):
    pdf_path = pdf_dir.glob(f"{document_name}.pdf")
    if pdf_path:
        return list(pdf_path)
    else:
        print(f"Pdf file with name {document_name} not found.")
        return None
    

# Define the click event handler
def on_button_clicked(image_index, page_number, page_images):
        
    #Get the amount of pages and the image index
    amount_of_pages = len(page_images)
    image_index = (image_index + 1) % amount_of_pages
    
    #Print which page number is going to be displayed
    if image_index == 2:
        #Next page
        page_number = page_number + 2
        #print("PDF page number:",page_number+2)
        
    image_number_text = widgets.Text(value=f"PDF page number: {page_number}")
            
    another_image = widgets.Image(value=open(page_images[image_index], 'rb').read(),format='jpg', width=IMAGE_WIDTH, height=IMAGE_HEIGHT)
    
    return image_number_text, another_image, image_index
        


#Gets an approximation of the percentages of valid spanish words in each of the texts
def calculate_spanish_word_percentage(texts):
    
    #Download necessary data
    nltk.download('stopwords')
    nltk.download('cess_esp')

    #Assign necessary data to variables
    spanish_words = set(nltk.corpus.cess_esp.words())
    spanish_stopwords = set(stopwords.words('spanish'))
    
    #Initialize variable to store percentages
    percentages = []
    
    for text in texts:
        
        #Tokenize 
        tokenized_text = set(tokenize(text.lower()))
    
        #Get the valid words while getting rid of stopwords
        valid_words = tokenized_text.intersection(spanish_words) - spanish_stopwords
    
        #Get the percentage of valid words
        percentages.append((len(valid_words) / len(tokenized_text)) * 100)
    
    return percentages

#Cleans a string from punctuation
def clean_string(input_string):
    # Remove punctuation
    cleaned_string = ''.join(char for char in input_string if char not in string.punctuation)
    return cleaned_string

#Save the corrected document
def save_file(files_found, document_to_search, corrected_data_folder, corrected_text_data):
    
    file_containing_document = find_key(files_found, document_to_search)

    with open(Path(manually_corrected_data_folder,file_containing_document), "w+") as file:
        json.dump(corrected_text_data, file)
        
    print(f"\nSaved file {file_containing_document} with the new corrected data for document {document_to_search}.")
        
    return True

#Save a list of dictionaries to a pickle file
def save_dicts_to_file(dicts, filename):
    with open(filename, 'wb') as file:
        pickle.dump(dicts, file)
        
#Load a list of dictionaries from a pickle file
def load_dicts_from_file(filename):
    with open(filename, 'rb') as file:
        dicts = []
        while True:
            try:
                d = pickle.load(file)
                dicts.append(d)
            except EOFError:
                break
        return dicts

#Get all the neighborhoods given a document, a keyword and the size of the neighborhood
def search_neighborhoods(document_to_search, term_to_search, size_of_neighborhood, splitted_data_folder, corrected_data_folder, file_containing_document):
    
    #Get the uncorrected file where the document is located and load it
    path_file_containing_document = Path(splitted_data_folder,file_containing_document)
    
    with open(path_file_containing_document) as json_file:
        text_data = json.loads(json_file.read())
            
    #Get the corrected file where the document is located and load it
    path_corrected_file_containing_document = Path(corrected_data_folder,file_containing_document)

    with open(path_corrected_file_containing_document) as json_file:
        corrected_text_data = json.loads(json_file.read())
        
    #Find the neighborhoods where the term is located in the uncorrected files
    original_neighborhoods_list, indexes, __, __ = find_neighborhoods(text_data[document_to_search], term_to_search, -1 ,size_of_neighborhood)

    #if the key doesn't exist in the correction_data it might be a regular term
    if term_to_search in correction_data_keys:
        corrected_neighborhoods_list, __, start_indexes, finish_indexes = find_neighborhoods(corrected_text_data[document_to_search], \
                                                                                             correction_data[term_to_search], indexes, \
                                                                                             size=size_of_neighborhood, search_close_to_index=True)
    else:
        corrected_neighborhoods_list, __, start_indexes, finish_indexes = find_neighborhoods(corrected_text_data[document_to_search], \
                                                                      term_to_search, -1, size_of_neighborhood)
    
    #Define variable to make editions and leave the original neighbors untouched
    new_corrected_neighborhoods_list = corrected_neighborhoods_list

    return original_neighborhoods_list, corrected_neighborhoods_list, start_indexes, text_data

def split_metadata_period(metadata_list):
    choices = set()
    for data in metadata_list:
        if isinstance(data, str):
            if '|' in data:
                choices.update(data.split('|'))
            else:
                choices.add(data)
    return sorted(choices)

def split_metadata_entity(metadata_list):
    choices = {}
    for data in metadata_list:
        if isinstance(data, str):
            if '|' in data:
                data_parts = data.split('|')
                if data_parts[0] not in choices:
                    choices[data_parts[0]] = set()
                choices[data_parts[0]].update(data_parts[1:])
            else:
                if data not in choices.keys():
                    choices[data] = set()
    return choices

def split_metadata_nationality(metadata_list):
    choices = {'europeo': set(), 'americano': set()}
    for data in metadata_list:
        if isinstance(data, str):
            if '|' in data:
                data_parts = data.split('|')
                for p in data_parts:
                    if p == 'americano' or p == 'europeo':
                        main_nationality = p
                    elif p != 'varios':
                        choices[main_nationality].add(p.strip())
    return choices
