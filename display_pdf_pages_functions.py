import fitz
from useful_functions import clean_string, tokenize
from global_variables import IMAGE_WIDTH, IMAGE_HEIGHT

#Create an image out of a pdf page
def create_image_from_pdf_page(page, width=IMAGE_WIDTH, height=IMAGE_HEIGHT, name=""):
    
    #create the image from the page
    pix = page.get_pixmap()
    
    #Change the name of the output file if the file is from the page before or next
    if name != "":
        image_path = f'output-{name}.jpg'  # Path to save the image
    else:
        image_path = 'output.jpg'  # Path to save the image
    
    #Save the image
    pix.save(image_path)
    #image = Image.open(image_path)

    # Resize the image
    #resized_image = image.resize((width, height))
    
    return image_path#resized_image

#Get the page of the pdf where the term is found
def get_pdf_page(pdf_path, start_index, width=IMAGE_WIDTH, height=IMAGE_HEIGHT):
    
    #Open pdf file
    doc = fitz.open(pdf_path)
    total_of_pages = doc.page_count
    current_index = 0
    
    #Flag for page found
    page_found = False
    
    for i in range(total_of_pages):
        page = doc.load_page(i)
        text = clean_string(page.get_text())
        tokenized_text = tokenize(text)
        current_index += len(tokenized_text)
        
        #Initialize variables for before and after pages
        page_before = None
        page_next = None
        image_before = None
        image_next = None
                
        #Does the page contain the index of the term we're looking for or is the page the last one (MAYBE DOESNT WORK ALWAYS)
        if current_index >= start_index or i == len(doc)-1:
            
            #Store page before if it exists
            if i != 0: 
                page_before = doc.load_page(i-1)
                print("PB i",page_before,total_of_pages)
                
                #Make sure the page exists before creating the image
                if page_before:
                    image_before = create_image_from_pdf_page(page_before, width, height, name="previous")
                
            #Store page after if it exists
            if i < total_of_pages-1: 
                page_next = doc.load_page(i+1)
                print("PN i",page_next)
                
                #Make sure the page exists before creating the image
                if page_next:
                    image_next = create_image_from_pdf_page(page_next, width, height, name="next")

            # Get the image from the chosen page
            resized_image = create_image_from_pdf_page(page)
            
            return resized_image, i, image_before, image_next
        
    return None, None, None, None

#Function to search for a pdf page and display the image
def search_pdf_pages(start_indexes):

    #Check if it's a valid neighborhood
    if current_neighborhood <= len(start_indexes)-1:

        #Search for the pdf page image with the neighborhood and the page image before and after in case the neighborhood overlaps
        pdf_page, page_number, pdf_page_before, pdf_page_next = get_pdf_page(pdf_path, start_indexes[current_neighborhood])

        #If the page was found
        if pdf_page != None:
            
            return pdf_page, pdf_page_before, pdf_page_next
            
        else:
            print(f"The page with the neighborhood was not found.")
            return None, None, None
    else:
        print(f"\nThe neighborhood number {number_of_neighborhood} in document {pdf_path.stem} doesn't exist.")
        return None, None, None