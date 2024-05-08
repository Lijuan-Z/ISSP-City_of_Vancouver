import json
import os
import pypdf


def extract_metadata(pdf_path):
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = pypdf.PdfReader(file)
            metadata = {
                'Title': pdf_reader.metadata.title,
            }
    except Exception as e:
        print(f"Error reading PDF file '{pdf_path}': {e}")
        metadata = None

    return metadata


def extract_text(pdf_path, keyword):
    try:
        pdf_file = pypdf.PdfReader(pdf_path)
        text = ''
        for page_num in range(len(pdf_file.pages)):
            page = pdf_file.pages[page_num]
            page_text = page.extract_text()
            keyword_index = page_text.lower().find(keyword.lower())
            if keyword_index != -1:
                # Find the nearest period ('.') character before the keyword
                start_index = max(0, page_text.rfind('.', 0, keyword_index) + 1)
                # Find the nearest period ('.') character after the keyword
                end_index = min(len(page_text), page_text.find('.', keyword_index))
                # Adjust the end_index if no period found after the keyword
                if end_index == -1:
                    end_index = len(page_text)
                # Find nearest space character before and after the keyword
                while start_index > 0 and not page_text[start_index].isspace():
                    start_index -= 1
                while end_index < len(page_text) - 1 and not page_text[end_index].isspace():
                    end_index += 1
                text += page_text[start_index:end_index]
        # Remove newline characters
        text = text.replace('\n', ' ')
    except Exception as e:
        print(f"Error extracting text from PDF file '{pdf_path}': {e}")
        text = None

    return text


def create_metadata_dictionary(folder_path, search_term=None):
    nested_metadata_dict = {}
    for root, dirs, files in os.walk(folder_path):
        for file_name in files:
            if file_name.endswith('.pdf'):
                file_path = os.path.join(root, file_name)
                if search_term is not None:
                    text = extract_text(file_path, search_term)
                    if text:
                        metadata = extract_metadata(file_path)
                        if metadata is not None:
                            # Additional data to be added
                            additional_data = {
                                'Search term': search_term,
                                'Reference': text.strip() if text else None
                            }
                            # Merge metadata and additional data
                            metadata.update(additional_data)
                            nested_metadata_dict[file_name] = metadata
    return nested_metadata_dict


if __name__ == '__main__':
    # folder_path = 'test_pdfs'
    folder_path = 'downloaded_pdfs'

    # Search for PDFs containing these keywords
    search_term = 'parking'
    nested_metadata_dict = create_metadata_dictionary(folder_path, search_term=search_term)

    # Convert nested metadata dictionary to JSON string
    json_str = json.dumps(nested_metadata_dict, indent=4)
    
    print(json_str)
