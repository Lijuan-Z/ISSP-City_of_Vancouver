import easyocr
import json
import os
import pypdf
from pdfminer.layout import LTImage


def extract_metadata(pdf_path):
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = pypdf.PdfReader(file)
            metadata = {
                'Title': pdf_reader.metadata.title
            }
    except Exception as e:
        print(f"Error reading PDF file '{pdf_path}': {e}")
        metadata = None

    return metadata


def find_last_outline(pdf_file, page):
    outlines = pdf_file.outline
    if outlines:
        last_title = outlines[0].get('/Title')
        for outline in outlines:
            page_num = pdf_file.get_destination_page_number(outline)
            if page_num == page:
                return outline.get('/Title')
            if page_num > page:
                return last_title
            last_title = outline.get('/Title')
        return None
    else:
        return None

def extract_text(pdf_path, keywords):
    try:
        pdf_file = pypdf.PdfReader(pdf_path)
        text_with_page = []
        for page_num in range(len(pdf_file.pages)):
            page = pdf_file.pages[page_num]
            page_text = page.extract_text()
            sentences = page_text.split('.')
            for i, sentence in enumerate(sentences):
                cleaned_sentence = sentence.strip().replace('\n', '') + '.'
                for keyword in keywords:
                    if keyword.lower() in cleaned_sentence.lower():
                        # Extract the sentence containing the search term
                        start_index = max(0, i - 2)
                        end_index = min(len(sentences), i + 3)
                        context = '. '.join(sentences[start_index:end_index])
                        # Remove newline characters from the context
                        context = context.replace('\n', '')
                        text_with_page.append((context, page_num + 1))
                        break  # Move to the next sentence after finding a keyword
    except Exception as e:
        print(f"Error extracting text from PDF file '{pdf_path}': {e}")
        text_with_page = []

    return text_with_page


def create_metadata_dictionary(folder_path, search_term=None):
    nested_metadata_dict = {}
    for root, dirs, files in os.walk(folder_path):
        for file_name in files:
            if file_name.endswith('.pdf'):
                file_path = os.path.join(root, file_name)
                if search_term is not None:
                    instances = []
                    text_with_pages = extract_text(file_path, search_term)
                    # for extracted_text, page_number, outline_title in text_with_pages:
                    for extracted_text, page_number in text_with_pages:
                        if extracted_text:
                            instances.append({
                                'Page number': page_number,
                                'Reference': extracted_text.strip(),
                                # 'Chapter/Section': outline_title
                            })
                    if instances:
                        metadata = extract_metadata(file_path)
                        if metadata is not None:
                            metadata['Search terms'] = [term for term in search_terms if term in extracted_text]
                            metadata['Instances'] = instances
                            nested_metadata_dict[file_name] = metadata
    return nested_metadata_dict


if __name__ == '__main__':
    folder_path = 'test_pdfs'
    # folder_path = 'downloaded_pdfs'

    # Search for PDFs containing search term
    search_terms = ['parking', 'road']
    nested_metadata_dict = create_metadata_dictionary(folder_path, search_term=search_terms)

    # Convert metadata dictionary to JSON string
    json_str = json.dumps(nested_metadata_dict, indent=4)
    print(json_str)
