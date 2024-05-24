import json
import time
import re

import google.generativeai as genai
import os
from obj3_v2 import api_connect
from config import GOOGLE_API_KEY
# GOOGLE_API_KEY = os.environ['GOOGLE_API_KEY']

gemini_update = ""

class GeminiAPI():

    def __init__(self):
        self.model = "gemini-1.5-flash-latest"

    def find_title(self, URL_info, processed_data):
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
        genai.configure(api_key=GOOGLE_API_KEY)
        model = genai.GenerativeModel(self.model,
                                      system_instruction=system_definition
                                      )

        # generation_config = genai.types.GenerationConfig(
        #     candidate_count=1,  # Number of response versions to return
        # )

        data = processed_data

        doc_count = 0

        for key, value in data.items():
            try:
                file_updated = URL_info[key]['file_updated']
            except KeyError:
                file_updated = False
            if not file_updated:
                doc_count += 1
                new_dict = {}
                new_dict[key] = {}
                new_dict[key]["1"] = data[key]['Pages']['1']
                try:
                    new_dict[key]["2"] = data[key]['Pages']['2']
                except KeyError as e:
                    print(f"only one page on document {key}")
                dict_str = json.dumps(new_dict[key])
                prompt = dict_str

                print(new_dict)
                print("\n\n")


                response = model.generate_content(
                    contents=prompt
                )
                try:
                    print(response.text)
                    data[key]['AI Title'] = response.text
                except:
                    data[key]['AI Title'] = "No response"

                if doc_count % 10 == 0:
                    print(f"timeout number {doc_count/10}")
                    time.sleep(60)
                else:
                    time.sleep(2)

        return data

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
        genai.configure(api_key=GOOGLE_API_KEY)
        model = genai.GenerativeModel(self.model,
                                      system_instruction=system_definition
                                      )


        data = self.get_sections_using_hugface(search_results)
        max_reference_input = 3

        instances_search = {}
        total_count = 0

        for key,value in data.items():
            instances_search[key] = []
            reference_num = 0
            for i in range(0, len(value), max_reference_input):
                combined_dict = {}

                for j in range(max_reference_input):
                    if i + j < len(value):  # Check if the index exists
                        total_count +=1
                        combined_dict[reference_num] = value[i+j]['Reference']
                        reference_num += 1

                instances_search[key].append(combined_dict)

        print(f"Total instances found: {total_count}")

        # return instances_search
        timeout = 60
        instance_count = 0
        for key, instance_group in instances_search.items():
            gemini_update = f"Searching for amendments for {key}"
            print(f"filename {key}")
            print(f"instance_group: {instance_group}")
            for instance in instance_group:
                print(f"instance: {instance}")
                instance_count += 1
                query = f"Prompt: {prompt}\n References :{instance}"
                retries = 0
                response = ""
                response_failed = False
                while retries < 6:
                    try:
                        response = model.generate_content(
                            contents=query
                        )
                        break
                    except:
                        retries += 1
                        print(f"Error getting response from api call - trial {retries}")
                        if retries == 6:
                            response_failed = True
                            gemini_update = f"Could not get amendment for {key}"
                            if (instance_count + retries) % 15 == 0:
                                gemini_update = f"Timeout due to AI input limit"
                                time.sleep(timeout)
                            break
                        time.sleep(2)
                if instance_count % 10 == 0:
                    print(f"time out number: {instance_count/10}")
                    gemini_update = f"Timeout due to AI input limit"
                    time.sleep(timeout)

                if not response_failed:
                    print(response.text)

                    actual_dict = self.convert_to_dict(response.text)

                    print(actual_dict)

                    data = self.add_response_to_search_results(search_results, actual_dict, key)

        gemini_update = f"Finished searching for amendments"
        return data

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

    def add_response_to_search_results(self, search_results,response, file_name):
        #turn the response into an actual dictionary

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

        with open(processed_file, "r") as f:
            processed_data = json.load(f)

        file_count = 1

        for key, value in search_results.items():
            gemini_update = f"Finding section titles and numbers. file: {file_count} of {len(search_results)}"
            for result in value:
                index = value.index(result)
                reference = result["Reference"]
                page_number = int(result["Page"])
                page_content = processed_data[key]['Pages'][str(page_number)]
                if page_number > 1:
                    pre_page = processed_data[key]['Pages'][str(page_number-1)]
                else:
                    pre_page = ""

                #Adjusted from Lisa's code
                prompt = (f"Can you get the section number and section title of the following text?\n {reference} \n"
                          f"Please provide the section number and title in the format: "
                          f"Section Number: xxx. \n Section Title: xxx. If you can't return 'Not Found'. "
                          f"here is the current page context: {page_content} . "
                          f"And here is the pre page context: {pre_page}")
                max_retry = 3
                retry_count = 0
                query_result = None
                chatbot = api_connect()
                section_number = "Unknown"
                section_title = "Unknown"
                should_continue = True
                while retry_count < max_retry and query_result is None and should_continue:
                    try:
                        query_result = chatbot.chat(prompt)
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
                        if "too many" in str(e).lower():
                            print("Too many requests error reached, waiting 15 seconds...")
                            time.sleep(15)
                        retry_count += 1
                    time.sleep(2)  # always wait after each query attempt
                search_results[key][index]['Section Number'] = section_number
                search_results[key][index]['Section Title'] = section_title

            file_count += 1

        gemini_update = "Section finding finished!"
        return search_results


if __name__ == "__main__":
    gemini = GeminiAPI()
    with open("output_test.json", "r") as file:
        data = json.load(file)
    prompt = ("If there is any mention to parking space size or number parking spots only."
              "Replace with 'See parking by-law'"
              "Do not replace mentions of parking access or location."
              "Do not replace if parking by-law is already mentioned")
    # search_results = gemini.get_sections_using_hugface(data)

    # print(search_results)

    test = gemini.get_amendment_and_rationale(data, prompt)
    with open("instances.json", "w") as file:
        json.dump(test, file)
