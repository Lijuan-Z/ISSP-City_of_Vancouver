import pypdf
import json
import os
import time
import easyocr
from GeminiAPI import GeminiAPI



class ProcessToJSON:
    def __init__(self, folder_path):
        self.folder_path = folder_path
        # Load current JSON
        try:
            with open("processed.json", "r") as processed_file:
                self.current_data = json.load(processed_file)
        except FileNotFoundError:
            self.current_data = {}


    def read_PDFs(self, URL_info, image_included=False, file_list_inc_image=[]):
        global process_update
        nested_metadata_dict = self.current_data
        files_to_update = self.count_total_files(URL_info)
        file_update_counter = 0
        for root, dirs, files in os.walk(self.folder_path):
            for file_name in files:
                file_updated = URL_info[file_name[:-4]]['file_updated']
                if file_name.endswith('.pdf') and not file_updated:
                    file_path = os.path.join(root, file_name)
                    try:
                        with open(file_path, mode='rb') as file:
                            process_update = f"Updating file{file_update_counter} of {files_to_update}"
                            reader = pypdf.PdfReader(file)
                            nested_metadata_dict[file_name] = {}
                            nested_metadata_dict[file_name]['Pages'] = {}
                            for page in reader.pages:
                                page_num = str(page.page_number + 1)
                                if not image_included:
                                    page_text = page.extract_text()
                                elif image_included and page.images:
                                    page_text = self.get_image_text(page)
                                else:
                                    page_text = ""
                                nested_metadata_dict[file_name]['Pages'][page_num] = page_text
                    except Exception as e:
                        print(f"{file_name} could not be updated. Error: {e}")


        #Get info from the URL info
        nested_metadata_dict = self.add_file_info_to_JSON(nested_metadata_dict, URL_info)

        #Add the AI titles using gemini
        gemAI = GeminiAPI(nested_metadata_dict)
        nested_metadata_dict = gemAI.find_title()

        return nested_metadata_dict

    def count_total_files(self, URL_info):
        files_to_update = 0
        for root, dirs, files in os.walk(self.folder_path):
            for file_name in files:
                file_updated = URL_info[file_name[:-4]]['file_updated']
                if file_name.endswith('.pdf') and not file_updated:
                    files_to_update += 1

        return files_to_update

    def add_file_info_to_JSON(self, nested_metadata_dict, URL_info):
        for key in nested_metadata_dict.keys():
            dict_info = {}
            for value in URL_info:
                if key[:-4] == list(value.keys())[0]:
                    dict_info = value
                    break
            try:
                nested_metadata_dict[key]['Title'] = dict_info[key[:-4]]['title']
                nested_metadata_dict[key]['Link'] = dict_info[key[:-4]]['url']
                nested_metadata_dict[key]['Land Use Document Type'] = dict_info[key[:-4]]['type']
            except Exception as e:
                nested_metadata_dict[key]['Title'] = "No title"
                nested_metadata_dict[key]['Link'] = "No link"
                nested_metadata_dict[key]['Land Use Document Type'] = "No type"
                print(f"Error adding doc_info to dictionary {key}: {e}")

        return nested_metadata_dict


    def get_image_text(self, page):
        image_reader = easyocr.Reader(['en'])
        image_info = ""
        try:
            for image in page.images:
                # print(filename,' has image')
                result = image_reader.readtext(image.data, detail=0)
                image_text = ' '.join(result)
                image_info += f"IMAGE: {image_text}"
        except:
            print("Could not read image")
        page_text = page.extract_text()
        page_text += f" {image_info}"
        return page_text


if __name__ == '__main__':
    # folder_path = 'test_pdfs'
    folder_path = '../downloaded_pdfs'

    # Search for PDFs containing search term
    processor = ProcessToJSON(folder_path)
    URL_info = []
    with open('doc_type.json') as json_file:
        data = json.load(json_file)

    start = time.time()
    dict_info = processor.read_PDFs(image_included=False, URL_info=data)
    print(time.time() - start)

    with open('processed.json', 'w') as json_file:
        json.dump(dict_info, json_file, indent=4)
