import pypdf
import json
import os
import time


class ProcessToJSON:
    def __init__(self, folder_path):
        self.folder_path = folder_path

    def read_PDFs(self, image_included, URL_info):
        nested_metadata_dict = {}
        for root, dirs, files in os.walk(self.folder_path):
            for file_name in files:
                if file_name.endswith('.pdf'):
                    file_path = os.path.join(root, file_name)
                    try:
                        with open(file_path, mode='rb') as file:
                            reader = pypdf.PdfReader(file)
                            nested_metadata_dict[file_name] = {}
                            nested_metadata_dict[file_name]['Title'] = reader.metadata.title
                            nested_metadata_dict[file_name]['Pages'] = {}

                            for page_num, page in enumerate(reader.pages, start=1):
                                page_text = ""
                                try:
                                    page_text = page.extract_text()
                                except Exception as e:
                                    print(f"Error extracting text from page {page_num} of '{file_name}': {e}")
                                nested_metadata_dict[file_name]['Pages'][str(page_num)] = page_text
                    except Exception as e:
                        print(f"Error reading PDF file '{file_name}': {e}")

        nested_metadata_dict = self.add_file_info_to_JSON(nested_metadata_dict, URL_info)

        return nested_metadata_dict

    def add_file_info_to_JSON(self, nested_metadata_dict, URL_info):
        for key in nested_metadata_dict.keys():
            dict_info = {}
            for value in URL_info:
                if key[:-4] == list(value.keys())[0]:
                    dict_info = value
                    break
            try:
                nested_metadata_dict[key]['Link'] = dict_info[key[:-4]]['url']
                nested_metadata_dict[key]['Land Use Document Type'] = dict_info[key[:-4]]['type']
            except Exception as e:
                nested_metadata_dict[key]['Link'] = "No link"
                nested_metadata_dict[key]['Land Use Document Type'] = "No type"
                print(f"Error adding doc_info to dictionary {key}: {e}")

        return nested_metadata_dict


if __name__ == '__main__':
    folder_path = '../test_pdfs'
    # folder_path = '../downloaded_pdfs'

    # Search for PDFs containing search term
    processor = ProcessToJSON(folder_path)
    URL_info = []
    with open('doc_type.json') as json_file:
        data = json.load(json_file)

    start = time.time()
    dict_info = processor.read_PDFs(False, URL_info=data)
    print(time.time() - start)

    with open('processed.json', 'w') as json_file:
        json.dump(dict_info, json_file, indent=4)
