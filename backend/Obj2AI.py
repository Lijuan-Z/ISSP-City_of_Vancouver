import json
import time
import re

from APIConnect import APIConnect

gemini_update = ""


class Obj2AI():

    def find_title(self, URL_info, processed_data):
        global gemini_update
        system_definition = ("You are going to receive the first 2 pages of a document in form of a dictionary,"
                             "The format is {<page_number>: <content>}."
                             "The title of the document is included in those 2 pages"
                             "Return just the title of the document"
                             "The title might refer to codes"
                             "Example: 'M-1 District Schedule' or 'R1-1 District Schedule'"
                             "But it might have different structure"
                             "Example: 'Guidelines for Larger Zero Emission Buildings' or 'Burrard Landing (201 Burrard Stret) CD-1 Guidelines'"
                             "Also could be zoning by-law section documents:"
                             "Example: 'Section 11: Use Specific Regulations' or 'Schedule E: Building Lines'"
                             )
        model = APIConnect.gemini_connect(system_definition)

        doc_count = 0

        for key, value in processed_data.items():
            if not Obj2AI.is_file_updated(key, URL_info):
                doc_count += 1
                first_two_pages = {pg_num: value['Pages'][pg_num] for pg_num in ['1', '2'] if pg_num in value['Pages']}

                if not first_two_pages:
                    print(f"No valid pages found for document {key}")
                    continue

                processed_data[key]['AI Title'] = self.get_title_from_model(model, first_two_pages)

                self.handle_timeout(doc_count)

        return processed_data

    def get_title_from_model(self, model, first_two_pages):
        prompt = json.dumps(first_two_pages)

        response = model.generate_content(
            contents=prompt
        )
        try:
            print(response.text)
            return response.text
        except:
            print(f"Failed to get response from model")
            return "No response"

    @staticmethod
    def is_file_updated(file_name, URL_info):
        try:
            return URL_info[file_name]['file_updated']
        except KeyError:
            return False

    def handle_timeout(self, doc_count, timout_trigger=10):
        timeout = 60
        if doc_count % timout_trigger == 0:
            global gemini_update
            gemini_update = "Timeout due to free model limitation reached - 60 seconds wait"
            print(f"Timeout number {doc_count / timout_trigger}")
            time.sleep(timeout)
        else:
            time.sleep(2)

    def get_amendment_and_rationale(self, search_results, prompt):
        global gemini_update
        system_definition = ('You are receiving some pieces of information in dictionary format'
                             'The format is {<reference number>: <content>}.'
                             'You will also receive a prompt'
                             'Based on the prompt you will return an amendment and rationale for each content.'
                             'Follow the instructions of the prompt, for example'
                             '"Change mentions of window shape and size to "see window-by-law"". '
                             '-> Means change only if there is mention of shape and size of window.'
                             'Return is in String: '
                             'Amendment<reference number>: Amendement suggestion, Rationale<reference number>: Rationale Suggestion.'
                             'If no amendment is required return both suggestions as "No Change"'
                             'Only provide one amendment and one rationale per reference number'
                             'Indicate removal by saying "Strike out <reference to be removed>'
                             'Example: Strike out: This is a reference to be struck out'
                             'Indicate substitution by saying "and substitute <reference to be included>"'
                             'Example prompt:'
                             '"Change mentions of window shape and size to "see window-by-law"'
                             'Example reference content:'
                             '{"0": "The windows can be up to 2 meters tall and the doors can be up to 3 meters tall"}'
                             'Expected output:'
                             'Amendment0: Strike out The windows can be up to 2 meters tall and substitute "See window by-law" '
                             'Rationale0: Remove mentions of window shape and size and ensure alignment to window by-law'
                             )
        model = APIConnect.gemini_connect(system_definition)

        search_results = self.get_sections_using_hugface(search_results)
        max_reference_input = 3

        instances_search, total_count = self.prepare_instances(search_results, max_reference_input)

        print(f"Total instances found: {total_count}")

        data = self.process_instances(instances_search, prompt, model, search_results)

        gemini_update = f"Finished searching for amendments"
        return data

    def process_instances(self, instances_search, prompt, model, search_results):
        global gemini_update
        instance_count = 0
        for key, instance_group in instances_search.items():
            gemini_update = f"Searching for amendments for {key}"
            print(gemini_update)
            print(f"filename {key}")
            print(f"instance_group: {instance_group}")
            for instance in instance_group:
                print(f"instance: {instance}")
                instance_count += 1
                query = f"Prompt: {prompt}\n References :{instance}"
                response_success, response = self.get_response_from_model(model, query, instance_count)
                self.handle_timeout(instance_count)

                if response_success:
                    print(response.text)
                    actual_dict = self.convert_to_dict(response.text)
                    print(actual_dict)
                    search_results = self.add_response_to_search_results(search_results, actual_dict, key)

        return search_results

    def get_response_from_model(self, model, query, instance_count):
        retries = 0
        response_success = True
        response = ""

        while retries <= 6:
            try:
                response = model.generate_content(contents=query)
                break
            except:
                retries += 1
                print(f"Error getting response from API call - trial {retries}")
                if retries == 6:
                    response_success = False
                    global gemini_update
                    gemini_update = f"Could not get amendment for instance"
                    break
                self.handle_timeout(instance_count + retries)

        return response_success, response

    def prepare_instances(self, data, max_reference_input):
        instances_search = {}
        total_count = 0

        for key, value in data.items():
            instances_search[key] = []
            reference_num = 0
            for i in range(0, len(value), max_reference_input):
                combined_dict = {}
                for j in range(max_reference_input):
                    if i + j < len(value):
                        total_count += 1
                        combined_dict[reference_num] = value[i + j]['Reference']
                        reference_num += 1
                instances_search[key].append(combined_dict)

        return instances_search, total_count

    def convert_to_dict(self, input_str):
        result = {}
        lines = input_str.strip().split('\n')

        for line in lines:
            line = line.strip()
            if not line:  # Skip empty lines
                continue

            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip().replace('"', "'")

            match = re.match(r'(Amendment|Rationale)(\d+)', key)
            if match:
                kind = match.group(1)
                num = match.group(2)
                if num not in result:
                    result[num] = {}
                result[num][kind] = value

        return result

    def add_response_to_search_results(self, search_results, response, file_name):
        # turn the response into an actual dictionary

        for key, value in response.items():
            for key2, value2 in value.items():
                index = int(key)
                print(key)
                print(f"Search results for {file_name}: {search_results[file_name]}")
                print(index)
                try:
                    search_results[file_name][index][key2] = value2
                except IndexError:
                    print(f"No index {index} found for {file_name}")

        return search_results

    def get_sections_using_hugface(self, search_results, processed_file="processed_final.json"):

        global gemini_update

        processed_data = self.load_processed_data(processed_file)

        file_count = 1
        start_section = time.time()
        result_count = 1

        for key, value in search_results.items():
            gemini_update = f"Finding section titles and numbers. file: {file_count} of {len(search_results)}"
            print(gemini_update)
            for result in value:
                index = value.index(result)
                reference = result["Reference"]
                page_number = int(result["Page"])
                page_content = processed_data[key]['Pages'][str(page_number)]
                pre_page = processed_data[key]['Pages'].get(str(page_number - 1), "") if page_number > 1 else ""
                print(f"Constructing prompt")
                # Adjusted from Lisa's code
                prompt = self.construct_prompt(reference, page_content, pre_page)
                print(f"Finished constructing prompt")
                section_number, section_title = self.get_section_info(prompt)
                self.handle_timeout(result_count, 5)
                search_results[key][index]['Section Number'] = section_number
                search_results[key][index]['Section Title'] = section_title
                result_count += 1
            file_count += 1

        gemini_update = "Section finding finished!"
        print(gemini_update)
        print(f"{time.time() - start_section}")
        return search_results

    def load_processed_data(self, processed_file):
        try:
            with open(processed_file, "r") as f:
                return json.load(f)
        except FileNotFoundError as e:
            print(f"Processed file not found: {e}")
            raise
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from processed file: {e}")
            raise

    def construct_prompt(self, reference, page_content, pre_page):
        return (f"Can you get the section number and section title of the following text?\n{reference}\n"
                f"Please provide the section number and title in the format: "
                f"Section Number: xxx.\nSection Title: xxx. If you can't return 'Not Found'.\n"
                f"Here is the current page context: {page_content}.\n"
                f"And here is the pre page context: {pre_page}")

    def get_section_info(self, prompt, max_retry = 3):
        chatbot = APIConnect.hugchat_connect_section()
        retry_count = 0
        timeout = 45
        section_number = "Unknown - Error from huggingchat AI platform."
        section_title = "Unknown - Error from huggingchat AI platform."

        while retry_count < max_retry and chatbot is not None:

            try:
                query_result = chatbot.chat(prompt)
                print(f"Result before parsing the response: {query_result}")
                if query_result:
                    section_number, section_title = self.parse_query_result(query_result)
                    break
            except Exception as e:
                print(f"Error querying the chatbot: {e}")
                if "too many" in str(e).lower():
                    print("Too many requests error, waiting 15 seconds...")
                    time.sleep(15)
                retry_count += 1
            time.sleep(2)  # Always wait after each query attempt

        return section_number, section_title

    def parse_query_result(self, query_result):
        section_number = "Unknown"
        section_title = "Unknown"
        query_text = str(query_result)
        lines = query_text.split('\n')
        print(f"parsing result")
        print(query_text)
        for line in lines:
            if line.startswith("Section Number: "):
                section_number = line.split(":")[1].strip()
            elif line.startswith("Section Title: "):
                section_title = line.split(":")[1].strip()

        return section_number, section_title

if __name__ == "__main__":
    gemini = Obj2AI()
    with open("output_test.json", "r") as file:
        data = json.load(file)
    prompt = ("If there is any mention to parking space size or number parking spots only."
              "Replace with 'See parking by-law'"
              "Do not replace mentions of parking access or location."
              "Do not replace if parking by-law is already mentioned")
    # search_results = gemini.get_sections_using_hugface(data)

    # print(search_results)
    with open("processed.json", "r") as f:
        processed_data = json.load(f)

    with open("doc_type.json", "r") as f:
        URL_info = json.load(f)

    # test = gemini.get_amendment_and_rationale(data, prompt)
    # with open("instances2.json", "w") as file:
    #     json.dump(test, file)
