import pandas as pd
import json
import os

class OutputHandler:

    @staticmethod
    def create_excel_file(json_obj, output_file="output.xlsx"):

        json_dict = OutputHandler.adjust_json_dict(json_obj)

        pd.DataFrame(json_dict).to_excel(output_file, engine="xlsxwriter")

    @staticmethod
    def adjust_json_dict_old(json_obj):

        if isinstance(json_obj, str):
            json_obj = json.loads(json_obj)

        print("Adjusting json object")
        dict_list = []
        for key, value in json_obj.items():
            for instance in json_obj[key]['Instances']:
                new_dictionary = {}
                new_dictionary["File name"] = key
                new_dictionary['Title'] = json_obj[key]['Title']
                new_dictionary['Search Terms'] = ', '.join(json_obj[key]['Search terms'])
                new_dictionary['Page Number'] = instance['Page number']
                new_dictionary['Reference'] = instance['Reference']
                dict_list.append(new_dictionary)

        return dict_list

    @staticmethod
    def adjust_json_dict(info_list):

        if isinstance(info_list, str):
            json_obj = json.loads(info_list)
        else:
            json_obj = info_list

        print("Adjusting json object")
        dict_list = []
        for instance in json_obj:
            new_dictionary = {}
            new_dictionary['Land Use Document type'] = instance[0]
            new_dictionary['Title'] = instance[1]
            new_dictionary['Section #'] = instance[4]
            new_dictionary['Section Title'] = instance[5]
            new_dictionary['Search Terms'] = instance[6]
            new_dictionary['Page Number'] = instance[3]
            new_dictionary['Link'] = instance[2]
            new_dictionary['Reference'] = instance[7]
            new_dictionary['Proposed amendement'] = "In Development"
            new_dictionary['Rationale'] = "In Development"
            dict_list.append(new_dictionary)

        return dict_list


if __name__ == "__main__":
    pass

