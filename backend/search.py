import json
import time
import configparser
# from search_term import api_connect
from obj3_v2 import api_connect

# config file for information management
config = configparser.ConfigParser()
config.read('development.ini')


def load_json(json_path):
    try:
        with open(json_path, 'r') as json_file:
            data = json.load(json_file)
    except Exception as e:
        print(f"Error reading JSON file '{json_path}': {e}")
        data = None
    return data


def write_to_json(data, output_file):
    try:
        with open(output_file, 'w') as json_file:
            json.dump(data, json_file, indent=4)
        print(f"Data written to '{output_file}' successfully.")
    except Exception as e:
        print(f"Error writing to JSON file '{output_file}': {e}")


def search_files(files, json_path, search_terms=None):
    nested_metadata_dict = {}
    json_data = load_json(json_path)

    if json_data:
        if search_terms is not None:
            for file_name, file_data in json_data.items():
                if 'Pages' in file_data and file_name[:-4] in files:
                    # print(f"Searching in file '{file_name}'")
                    for page_num, page_content in file_data['Pages'].items():
                        # Split the entire page content into paragraphs
                        paragraphs = page_content.split('\n \n')
                        for paragraph in paragraphs:
                            found_terms = []
                            for term in search_terms:
                                # Check for the presence of the term in the paragraph
                                if term.lower() in paragraph.lower():
                                    found_terms.append(term)

                            if found_terms:
                                # If any search term is found, prepare the context
                                context = paragraph.replace('\n', '')
                                if file_name not in nested_metadata_dict:
                                    nested_metadata_dict[file_name] = []
                                nested_metadata_dict[file_name].append({
                                    'Title': file_data['Title'],
                                    'AI Title': file_data['AI Title'],
                                    'Search terms': found_terms,
                                    'Page': page_num,
                                    'Reference': context.strip(),
                                    'Link': file_data['Link'],
                                    'Land Use Document Type': file_data['Land Use Document Type']
                                })

    else:
        print("No data loaded from JSON file.")

    return nested_metadata_dict


if __name__ == '__main__':
    json_file_path = config.get('server', 'processed_json_file')
    search_terms = ['parking', 'lane']
    files = ['4837c', 'bulletin-floor-area-calculation-tracing-overlay', 'bulletin-ra-1-perimeter-landscaping', 'F001',
             'guidelines-cd-1-little-mountain', 'guidelines-fc-1-east-false-creek', 'odp-false-creek',
             'Part9_Schedule9A', 'policy-plan-vancouver', 'zoning-by-law-district-schedule-rm-1']

    dictionary = search_files(files=files, json_path=json_file_path, search_terms=search_terms)
    output_file = 'output_test.json'
    write_to_json(dictionary, output_file)
