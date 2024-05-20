import json
import time

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
            file_updated = URL_info[key]['file_updated']
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
        system_definition = ("You are receiving some pieces of information in dictionary format"
                             "The format is {<reference number>: <content>}."
                             "You will also receive a prompt"
                             "Based on the prompt you will return an amendment and rationale for each content."
                             "If no amendment is necessary, return 'no amendment' in both fields."
                             "Return is in dictionary format: "
                             "{'Amendment<reference number>': Amendement suggestion, 'Rationale<reference number>': Rationale Suggestion}."
                             "Indicate removal by surrounding it with <remove></remove> symbol."
                             "Example: This is a text that contains <remove> part to be removed</remove>"
                             "Indicate replaced text by surrounding it with <add></add> symbol"
                             "Example: This is a text that contains <remove> part to be removed</remove> <add> part corrected </add>"
                             "Ensure that the resulting amendment text is still coherent after removing and adding parts"
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


        for key, instance_group in instances_search:
            for instance in instance_group:
                query = f"Prompt: {prompt}\n References :{instance}"

                response = model.generate_content(
                    contents=query
                )





if __name__ == "__main__":
    gemini = GeminiAPI()
    with open("reduced_output.json", "r") as file:
        data = json.load(file)
    prompt = "If there is any mention to parking space on parking spots, replace with 'See parking by-law'"
    test = gemini.get_amendment_and_rationale(data, prompt)
    with open("instances.json", "w") as file:
        json.dump(test, file)
