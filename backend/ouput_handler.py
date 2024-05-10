import pandas as pd
import json


class OutputHandler:

    @staticmethod
    def create_excel_file(json_obj, output_file="output.xlsx"):

        json_dict = OutputHandler.adjust_json_dict(json_obj)

        pd.DataFrame(json_dict).transpose().to_excel(output_file)

    @staticmethod
    def adjust_json_dict(json_obj):
        print(type(json_obj))

        if isinstance(json_obj, str):
            json_obj = json.loads(json_obj)

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


if __name__ == "__main__":
    pass

