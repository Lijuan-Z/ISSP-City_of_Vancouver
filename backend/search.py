import json
import time
from search_term import api_connect


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


def search_files(file_to_search, json_path, search_terms=None):
    nested_metadata_dict = {}
    json_data = load_json(json_path)
    chatbot = api_connect()
    pre_page_text = ''

    if json_data:
        if search_terms is not None:
            for file_name, file_data in json_data.items():
                if 'Pages' in file_data and file_name[:-4] in file_to_search:
                    print(f"Searching in file '{file_name}'")
                    for page_num, page_content in file_data['Pages'].items():
                        # Split the entire page content into paragraphs
                        paragraphs = page_content.split('\n \n')
                        for paragraph in paragraphs:
                            # Split each paragraph into sentences
                            sentences = paragraph.split('.')
                            for sentence_index, sentence in enumerate(sentences, start=1):
                                found_terms = []
                                for term in search_terms:
                                    # Split the sentence into words and check for exact matches
                                    words = sentence.split()
                                    if term.lower() in [word.lower() for word in words]:
                                        found_terms.append(term)
                                        # Extract three sentences before and after the sentence containing the term
                                        context_start = max(0, sentence_index - 4)  # 4 sentences before
                                        context_end = min(len(sentences),
                                                          sentence_index + 4)  # 3 sentences after + 1 containing the term
                                        context = '. '.join(sentences[context_start:context_end])
                                        # Remove newline characters from the context
                                        context = context.replace('\n', '')
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

                                        # Ask the chatbot for section number and title
                                        prompt = "Can you get the section number and section title of the following text?\n" + paragraph + "\nPlease provide the section number and title in the format: Section Number: xxx. \n Section Title: xxx. If you can't return None. here is the current page context" + page_content + ". And here is the pre page context " + pre_page_text
                                        max_retry = 3
                                        retry_count = 0
                                        query_result = None
                                        while retry_count < max_retry and query_result is None:
                                            try:
                                                query_result = chatbot.chat(prompt)
                                                section_number = ""
                                                section_title = ""
                                                if query_result is not None:
                                                    query_text = str(
                                                        query_result)  # Extract text content from the Message object
                                                    lines = query_text.split('\n')
                                                    for line in lines:
                                                        if line.startswith("Section Number: "):
                                                            section_number = line.split(":")[1].strip()
                                                        elif line.startswith("Section Title: "):
                                                            section_title = line.split(":")[1].strip()
                                            except Exception as e:
                                                print(f"An error occurred while querying the chatbot: {e}")
                                                section_number = "Unknown"
                                                section_title = "Unknown"
                                                retry_count += 1
                                                time.sleep(2)  # Wait for a few seconds before retrying

                                        nested_metadata_dict[file_name][-1]['Section Number'] = section_number
                                        nested_metadata_dict[file_name][-1]['Section Title'] = section_title

    else:
        print("No data loaded from JSON file.")

    return nested_metadata_dict


if __name__ == '__main__':
    json_file_path = 'processed_final.json'
    search_terms = ['parking', 'lane']
    files = ['4837c', 'bulletin-floor-area-calculation-tracing-overlay', 'bulletin-ra-1-perimeter-landscaping', 'F001',
             'guidelines-cd-1-little-mountain', 'guidelines-fc-1-east-false-creek', 'odp-false-creek',
             'Part9_Schedule9A', 'policy-plan-vancouver', 'zoning-by-law-district-schedule-rm-1']

    dictionary = search(file_to_search=files, json_path=json_file_path, search_terms=search_terms)
    output_file = 'output_test.json'
    write_to_json(dictionary, output_file)
