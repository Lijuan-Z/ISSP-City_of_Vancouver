import json


def search_files(files_to_search, json_path="processed.json", search_terms=None):

    output_dict = create_metadata_dictionary(files_to_search, json_path, search_terms)

    return output_dict

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


def create_metadata_dictionary(files_to_search, json_path="processed.json", search_terms=None):
    nested_metadata_dict = {}
    json_data = load_json(json_path)

    if json_data:
        if search_terms is not None:
            for file_name, file_data in json_data.items():
                if 'Pages' in file_data and file_name[:-4] in files_to_search:
                    for page_num, page_content in file_data['Pages'].items():
                        # Split the entire page content into sentences
                        sentences = page_content.split('.')
                        for sentence_index, sentence in enumerate(sentences, start=1):
                            found_terms = []
                            for term in search_terms:
                                # Split the sentence into words and check for exact matches
                                words = sentence.split()
                                if term.lower() in [word.lower() for word in words]:
                                    found_terms.append(term)
                                    # Extract three sentences before and after the sentence containing the term
                                    context_start = max(0, sentence_index - 4)  # 4 sentences before
                                    context_end = min(len(sentences), sentence_index + 4)  # 3 sentences after + 1 containing the term
                                    context = '. '.join(sentences[context_start:context_end])
                                    # Remove newline characters from the context
                                    context = context.replace('\n', '')
                                    if file_name not in nested_metadata_dict:
                                        nested_metadata_dict[file_name] = []
                                    nested_metadata_dict[file_name].append({
                                        'Title': file_data['Title'],
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
    json_file_path = 'processed.json'
    search_terms = ['parking', 'lane']

    nested_metadata_dict = search_files(json_file_path, search_terms=search_terms)
    output_file = 'output.json'
    write_to_json(nested_metadata_dict, output_file)
