import pypdf
import json
import os
import time
import easyocr
from Obj2AI import Obj2AI
import configparser

config = configparser.ConfigParser()
config.read('development.ini')

process_update = ""


class ProcessToJSON:
    def __init__(self, folder_path):
        """
        Initialize the ProcessToJSON class with the folder path.

        Args:
            folder_path (str): Path to the folder containing PDF files.
        """
        self.folder_path = folder_path
        # Load current JSON data
        self.current_data = self.load_processed_data()

    def load_processed_data(self):
        """
        Load the processed JSON data from the server configuration.

        Returns:
            dict: The current data from the processed JSON file.
        """
        try:
            with open(config.get('server', 'processed_json_file'), "r") as processed_file:
                return json.load(processed_file)
        except FileNotFoundError:
            return {}

    def read_PDFs(self, URL_info, image_included=False):
        """
        Read PDF files, process their content, and update the metadata dictionary.

        Args:
            URL_info (list): List of dictionaries containing URL information.
            image_included (bool): Flag to include image text extraction. Default is False.

        Returns:
            dict: Updated metadata dictionary after processing all PDF files.
        """
        URL_info = self.adjust_URL_info(URL_info)
        global process_update
        nested_metadata_dict = self.current_data
        files_to_update = self.count_total_files(URL_info)

        startTime = time.time()
        file_update_counter = 0

        # Traverse the folder path to find PDF files
        for root, dirs, files in os.walk(self.folder_path):
            for file_name in files:
                if file_name.lower().endswith('.pdf') and self.is_file_updated(URL_info, file_name):

                    file_update_counter += 1
                    process_update = f"Updating file {file_update_counter} of {files_to_update} -> {file_name}"
                    file_path = os.path.join(root, file_name)

                    nested_metadata_dict = self.process_file(file_name, file_path, nested_metadata_dict, image_included)

        process_update = f"Time to finish processing files: {time.time() - startTime}"
        print(process_update)

        nested_metadata_dict = self.finalize_processing(nested_metadata_dict, URL_info)

        print(time.time() - startTime)

        return nested_metadata_dict

    def finalize_processing(self, nested_metadata_dict, URL_info):
        """
        Finalize the processing by saving intermediate results and updating the JSON data.

        Args:
            nested_metadata_dict (dict): The current metadata dictionary.
            URL_info (list): List of dictionaries containing URL information.

        Returns:
            dict: The updated metadata dictionary with file information and AI titles.
        """
        # Save intermediate results
        self.save_to_json("processed.json", nested_metadata_dict)

        # Update the JSON data with URL info
        nested_metadata_dict = self.add_file_info_to_JSON(nested_metadata_dict, URL_info)

        # Save intermediate results again
        self.save_to_json("processed.json", nested_metadata_dict)

        # Add AI titles using an external AI module (gemini)
        gemAI = Obj2AI()
        nested_metadata_dict = gemAI.find_title(URL_info, nested_metadata_dict)

        # Save the final processed data
        self.save_to_json(config.get('server', 'processed_json_file'), nested_metadata_dict)

        return nested_metadata_dict

    def is_file_updated(self, URL_info, file_name):

        """
        Check if the file has been updated based on URL information.

        Args:
            URL_info (list): List of dictionaries containing URL information.
            file_name (str): Name of the file to check.

        Returns:
            bool: True if the file is updated, False otherwise.
        """
        try:
            return URL_info[file_name[:-4]]['file_updated']
        except KeyError:
            return True

    def process_file(self, file_name, file_path, nested_metadata_dict, image_included):
        """
        Process a single PDF file and extract its text content.

        Args:
            file_name (str): Name of the file to process.
            file_path (str): Path to the file.
            nested_metadata_dict (dict): The current metadata dictionary.
            image_included (bool): Flag to include image text extraction. Default is False.

        Returns:
            dict: The updated metadata dictionary with the processed file content.
        """
        try:
            with open(file_path, mode='rb') as file:
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

        return nested_metadata_dict

    def count_total_files(self, URL_info):
        """
        Count the total number of PDF files that need to be updated.

        Args:
            URL_info (list): List of dictionaries containing URL information.

        Returns:
            int: Total number of files to update.
        """
        files_to_update = 0
        for root, dirs, files in os.walk(self.folder_path):
            for file_name in files:
                if file_name.lower().endswith('.pdf') and self.is_file_updated(URL_info, file_name):
                    files_to_update += 1

        return files_to_update

    def add_file_info_to_JSON(self, nested_metadata_dict, URL_info):
        """
        Add additional file information to the JSON data based on URL info.

        Args:
            nested_metadata_dict (dict): The current metadata dictionary.
            URL_info (list): List of dictionaries containing URL information.

        Returns:
            dict: The updated metadata dictionary with additional file information.
        """
        print(f"Adding URL info to JSON")

        for key in nested_metadata_dict.keys():
            dict_info = URL_info
            try:
                nested_metadata_dict[key]['Title'] = dict_info[key[:-4]]['title']
                nested_metadata_dict[key]['Link'] = dict_info[key[:-4]]['url']
                nested_metadata_dict[key]['Land Use Document Type'] = dict_info[key[:-4]]['type']
            except KeyError as e:
                nested_metadata_dict[key]['Title'] = "No title"
                nested_metadata_dict[key]['Link'] = "No link"
                nested_metadata_dict[key]['Land Use Document Type'] = "No type"
                print(f"Error adding doc_info to dictionary {key}: {e}")

        return nested_metadata_dict

    def save_to_json(self, file_path, data):
        """
        Save the data to a JSON file.

        Args:
            file_path (str): Path to the JSON file.
            data (dict): Data to save.
        """
        with open(file_path, 'w') as json_file:
            json.dump(data, json_file, indent=4)

    def adjust_URL_info(self, URL_info):
        """
        Adjust the URL information by merging the list of dictionaries into a single dictionary.

        Args:
            URL_info (list): List of dictionaries containing URL information.

        Returns:
            dict: Merged URL information dictionary.
        """
        new_URL_info = {}
        for item in URL_info:
            new_URL_info.update(item)
        return new_URL_info

    def get_image_text(self, page):
        """
        Extract text from images within a PDF page using OCR.

        Args:
            page (pypdf.PageObject): Page object from which to extract text.

        Returns:
            str: Extracted text from the page and images.
        """
        image_reader = easyocr.Reader(['en'])
        image_info = ""
        try:
            for image in page.images:
                result = image_reader.readtext(image.data, detail=0)
                image_text = ' '.join(result)
                image_info += f"IMAGE: {image_text}"
        except Exception as e:
            print(f"Could not read image. Error: {e}")

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
    dict_info = processor.read_PDFs(image_included=False, URL_info=data)
    print(time.time() - start)

    with open('processed_test.json', 'w') as json_file:
        json.dump(dict_info, json_file, indent=4)
