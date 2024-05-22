import ast
import json
import time
import re

import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import os

GOOGLE_API_KEY = os.environ['GOOGLE_API_KEY']

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
        system_definition = ('You are receiving some pieces of information in dictionary format'
                             'The format is {<reference number>: <content>}.'
                             'You will also receive a prompt'
                             'Based on the prompt you will return an amendment and rationale for each content.'
                             'Follow the instructions of the prompt, for example'
                             '"Change mentions of window shape and size to "see window-by-law"". '
                             '-> Means change only if there is mention of shape and size of window.'
                             'If no amendment is necessary, return "no amendment" in both fields.'
                             'Return is in dictionary format: '
                             '{"Amendment<reference number>": "Amendement suggestion", "Rationale<reference number>": "Rationale Suggestion"}.'
                             'Ensure that every key and value end with a double quote and no other double quotes exist in the dictionary.'
                             'Indicate removal by surrounding it with <remove></remove> symbol.'
                             'Example: This is a text that contains <remove> part to be removed</remove>'
                             'Indicate replaced text by surrounding it with <add></add> symbol'
                             'Example: This is a text that contains <remove> part to be removed</remove> <add> part corrected </add>'
                             'Ensure that the resulting amendment text is still coherent after removing and adding parts'
                             )
        genai.configure(api_key=GOOGLE_API_KEY)
        model = genai.GenerativeModel(self.model,
                                      system_instruction=system_definition
                                      )

        data = search_results
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
            for instance in instance_group:
                query = f"Prompt: {prompt}\n References :{instance}"

                response = model.generate_content(
                    contents=query
                )
                response = self.clear_json_response(response.text)
                print("\n\n")
                print(response)
                print(key)
                data = self.add_response_to_search_results(data, response, key)
                instance_count += 1
                if instance_count % 10 == 0:
                    print(f"time out number: {instance_count/10}")
                    time.sleep(timeout)

        return data

    def add_response_to_search_results(self, search_results,response, file_name):
        #turn the response into an actual dictionary
        # response = json.loads(response)
        for key, value in response.items():
            if key.startswith("Amendment"):
                index = int(key.split('ment')[1])
                search_results[file_name][index]['Amendment'] = value
                rationale_key = f"Rationale{index}"
                search_results[file_name][index][rationale_key] = response.get(rationale_key)

        return search_results


    def clear_json_response(self, json_response):
        print(json_response)
        if json_response[3:7] == "json":
            json_response = json_response[7:-3]
        print("\n")
        print(json_response)
        json_response = json.dumps(json_response)
        # actual_dict = json_response
        # pattern = r'(".*?\'\s*[,}])|(\s*[,{]\s*\'[^"\'{}]+"\s*[,}])'
        # pattern = r'(".*?\'[,}])|(\'.*?"[,}])'
        pattern = r',\s*\"(Amendment\d+|Rationale\d+)\":'
        corrected_dict_str = re.sub(pattern, GeminiAPI.correct_quotes, json_response)
        actual_dict = ast.literal_eval(corrected_dict_str)
        print(actual_dict)
        print(type(actual_dict))
        if not isinstance(actual_dict, dict):
            actual_dict = json.loads(actual_dict)
            # actual_dict = json.loads(actual_dict)
        print(type(actual_dict))

        return actual_dict

    @staticmethod
    def correct_quotes(match):
        # text = match.group(0)
        # if text.startswith('"') and text.endswith("'") and (text[-2] in ',}'):
        #     return text[:-1] + '"'
        # elif text.startswith("'") and text.endswith('"') and (text[0] in ',{'):
        #     return '"' + text[1:]
        # return text
        return '", "' + match.group(1) + '":'



if __name__ == "__main__":
    gemini = GeminiAPI()
    with open("reduced_output.json", "r") as file:
        data = json.load(file)
    prompt = "If there is any mention to parking space on parking spots only, replace with 'See parking by-law'"
    test = gemini.get_amendment_and_rationale(data, prompt)
    with open("instances.json", "w") as file:
        json.dump(test, file)
