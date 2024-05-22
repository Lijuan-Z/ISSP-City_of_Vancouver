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


    def read_PDFs(self, URL_info, image_included=False):

        URL_info = self.adjust_URL_info(URL_info)
        global process_update
        nested_metadata_dict = self.current_data
        files_to_update = self.count_total_files(URL_info)
        file_update_counter = 0
        startTime = time.time()
        for root, dirs, files in os.walk(self.folder_path):
            for file_name in files:
                try:
                    file_updated = URL_info[file_name[:-4]]['file_updated']
                except KeyError:
                    file_updated = False
                if file_name.endswith('.pdf') and not file_updated:
                    file_path = os.path.join(root, file_name)
                    try:
                        with open(file_path, mode='rb') as file:
                            file_update_counter += 1
                            process_update = f"Updating file {file_update_counter} of {files_to_update} -> {file_name}"
                            file_time = time.time()
                            print(process_update)
                            reader = pypdf.PdfReader(file)
                            nested_metadata_dict[file_name] = {}
                            nested_metadata_dict[file_name]['Pages'] = {}
                            for page in reader.pages:
                                page_num = str(page.page_number + 1)
                                if not image_included or not page.images:
                                    page_text = page.extract_text()
                                elif image_included and page.images:
                                    page_text = self.get_image_text(page)
                                nested_metadata_dict[file_name]['Pages'][page_num] = page_text
                            print(f"Time taken for file {file_name}: {time.time() - file_time}")
                    except Exception as e:
                        print(f"{file_name} could not be updated. Error: {e}")

        print(f"Time to finish processing files: {time.time() - startTime}")

        #saving a file just in case
        with open('processed.json', 'w') as json_file:
            json.dump(nested_metadata_dict, json_file, indent=4)


        #Get info from the URL info
        nested_metadata_dict = self.add_file_info_to_JSON(nested_metadata_dict, URL_info)

        print(time.time() - startTime)

        #again just in case
        #saving a file just in case
        with open('processed.json', 'w') as json_file:
            json.dump(nested_metadata_dict, json_file, indent=4)

        #Add the AI titles using gemini
        # gemAI = GeminiAPI()
        # nested_metadata_dict = gemAI.find_title(URL_info, nested_metadata_dict)

        return nested_metadata_dict

    def count_total_files(self, URL_info):
        files_to_update = 0
        for root, dirs, files in os.walk(self.folder_path):
            for file_name in files:
                try:
                    file_updated = URL_info[file_name[:-4]]['file_updated']
                except KeyError:
                    file_updated = False
                if file_name.lower().endswith('.pdf') and not file_updated:
                    files_to_update += 1

        return files_to_update

    def add_file_info_to_JSON(self, nested_metadata_dict, URL_info):

        print(f"Adding URL info to JSON")

        for key in nested_metadata_dict.keys():
            dict_info = URL_info
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

    def adjust_URL_info(self, URL_info):

        print(f"num of files in doc_type is {len(URL_info)}")
        #remove the list
        new_URL_info = {}
        for item in URL_info:
            new_URL_info.update(item)
        return new_URL_info

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

        page_text = f"{page.extract_text()} {image_info}"
        return page_text


if __name__ == '__main__':
    # folder_path = 'test_pdfs'
    folder_path = 'downloaded_pdfs'

    # Search for PDFs containing search term
    processor = ProcessToJSON(folder_path)
    with open('doc_type.json') as json_file:
        data = json.load(json_file)


    start = time.time()
    dict_info = processor.read_PDFs(image_included=True, URL_info=data)
    print(time.time() - start)


    # # part Below only if AI title didn't run
    # with open("processed.json", "r") as processed_file:
    #     processed_data = json.load(processed_file)
    #
    # data = processor.adjust_URL_info(data)
    #
    # gemAI = GeminiAPI()
    # dict_info = gemAI.find_title(data, processed_data)
    # # end of AI title only

    with open('processed_final.json', 'w') as json_file:
        json.dump(dict_info, json_file, indent=4)
