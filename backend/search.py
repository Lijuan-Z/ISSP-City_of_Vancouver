import json
import time
import configparser

# config file for information management
config = configparser.ConfigParser()
config.read('development.ini')


def load_json(json_path):
    """
    Load JSON data from a file.

    Args:
        json_path (str): Path to the JSON file.

    Returns:
        dict: Loaded JSON data, or None if an error occurred.
    """
    try:
        with open(json_path, 'r') as json_file:
            data = json.load(json_file)
    except Exception as e:
        print(f"Error reading JSON file '{json_path}': {e}")
        data = None
    return data


def write_to_json(data, output_file):
    """
    Write data to a JSON file.

    Args:
        data (dict): Data to write to the JSON file.
        output_file (str): Path to the output JSON file.
    """
    try:
        with open(output_file, 'w') as json_file:
            json.dump(data, json_file, indent=4)
        print(f"Data written to '{output_file}' successfully.")
    except Exception as e:
        print(f"Error writing to JSON file '{output_file}': {e}")


def search_files(files, json_path, search_terms=None):
    """
    Search for terms in files based on JSON metadata.

    Args:
        files (list): List of file names to search within.
        json_path (str): Path to the JSON file containing file metadata.
        search_terms (list): List of terms to search for.

    Returns:
        dict: Nested dictionary containing search results.
    """
    nested_metadata_dict = {}
    json_data = load_json(json_path)
    found_file = False

    if json_data:
        if search_terms is not None:
            nested_metadata_dict, found_file = search_in_json_data(json_data, files, search_terms)
    else:
        print("No data loaded from JSON file.")

    return check_files_and_search_results(nested_metadata_dict, found_file)


def check_files_and_search_results(search_results, found_file):
    if found_file and search_results:
        return search_results, found_file
    elif found_file and not search_results:
        return "No search terms found in the files", False
    else:
        return "Files not found", False


def search_in_json_data(json_data, files, search_terms):
    """
    Search for terms within JSON data.

    Args:
        json_data (dict): JSON data to search within.
        files (list): List of file names to search within.
        search_terms (list): List of terms to search for.

    Returns:
        dict: Nested dictionary containing search results.
    """
    nested_metadata_dict = {}
    found_file = False

    for file_name, file_data in json_data.items():
        if 'Pages' in file_data and file_name[:-4] in files:
            found_file = True
            search_terms_in_file(file_name, file_data, search_terms, nested_metadata_dict)

    return nested_metadata_dict, found_file


def search_terms_in_file(file_name, file_data, search_terms, nested_metadata_dict):
    """
    Search for terms within a specific file's data.

    Args:
        file_name (str): Name of the file being searched.
        file_data (dict): Data of the file being searched.
        search_terms (list): List of terms to search for.
        nested_metadata_dict (dict): Dictionary to store search results.
    Returns:
        dict: Nested dictionary containing search results
    """

    for page_num, page_content in file_data['Pages'].items():
        paragraphs = page_content.split('\n \n')
        for paragraph in paragraphs:
            found_terms = [term for term in search_terms if term.lower() in paragraph.lower()]
            if found_terms:
                context = paragraph.replace('\n', '')
                nested_metadata_dict = add_search_result(file_name, file_data, page_num, found_terms,
                                                         context, nested_metadata_dict)

    return nested_metadata_dict


def add_search_result(file_name, file_data, page_num, found_terms, context, nested_metadata_dict):
    """
    Add search result to the nested metadata dictionary.

    Args:
        file_name (str): Name of the file being searched.
        file_data (dict): Data of the file being searched.
        page_num (str): Page number where the terms were found.
        found_terms (list): List of terms found in the file.
        context (str): Context in which the terms were found.
        nested_metadata_dict (dict): Dictionary to store search results.
    Returns:
        dict: The nested metadata dictionary
    """

    if file_name not in nested_metadata_dict:
        nested_metadata_dict[file_name] = []

    nested_metadata_dict[file_name].append({
        'Title': file_data.get('Title', ''),
        'AI Title': file_data.get('AI Title', ''),
        'Search terms': found_terms,
        'Page': page_num,
        'Reference': context,
        'Link': file_data.get('Link', ''),
        'Land Use Document Type': file_data.get('Land Use Document Type', '')
    })
    return nested_metadata_dict


if __name__ == '__main__':
    json_file_path = config.get('server', 'processed_json_file')
    search_terms = ['parking', 'lane']
    files = ['4837c', 'bulletin-floor-area-calculation-tracing-overlay', 'bulletin-ra-1-perimeter-landscaping', 'F001',
             'guidelines-cd-1-little-mountain', 'guidelines-fc-1-east-false-creek', 'odp-false-creek',
             'Part9_Schedule9A', 'policy-plan-vancouver', 'zoning-by-law-district-schedule-rm-1', 'blablabla']
    only_wrong_files = ['wrong1', 'wrong2']

    dictionary = search_files(files=only_wrong_files, json_path=json_file_path, search_terms=search_terms)

    output_file = 'output_test3.json'
    write_to_json(dictionary, output_file)
