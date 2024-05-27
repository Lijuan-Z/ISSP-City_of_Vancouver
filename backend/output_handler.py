import pandas as pd
from openpyxl import Workbook
import json
import re
import ast

class OutputHandler:

    @staticmethod
    def output_for_objective3(data, headers_df, excel_file_name):
        # Create a new Excel file if it doesn't exist
        try:
            wb = Workbook()
            wb.save(excel_file_name)
        except Exception as e:
            print(f"An error occurred while creating the Excel file: {e}")
        with pd.ExcelWriter(excel_file_name, mode="a", engine="openpyxl", if_sheet_exists="overlay", ) as writer:
            headers_df.to_excel(writer, sheet_name="Sheet", index=False)
            df = pd.DataFrame(data)
            df.to_excel(writer, sheet_name="Sheet", index=False)

    @staticmethod
    def create_excel_file(json_obj, output_file="output.xlsx"):

        json_dict = OutputHandler.adjust_json_dict_from_indexed(json_obj)

        OutputHandler.prettify_excel(json_dict, output_file)


    @staticmethod
    def adjust_json_dict_from_indexed(json_obj):

        # json_obj = {}
        # with open(json_file, "r") as jf:
        #     json_obj = json.load(jf)

        if isinstance(json_obj, str):
            json_obj = json.loads(json_obj)

        dict_list = []
        for key, value in json_obj.items():
            for instance in json_obj[key]:
                new_dictionary = {}
                new_dictionary["Land Use Document Type"] = instance["Land Use Document Type"]
                new_dictionary["File name"] = key
                new_dictionary['Title'] = instance["Title"]
                try:
                    new_dictionary['AI Title'] = instance["AI Title"]
                    new_dictionary['Section #'] = instance['Section Number']
                    new_dictionary['Section Title'] = instance['Section Title']
                except:
                    new_dictionary['AI Title'] = "No AI Title"
                    new_dictionary['Section #'] = "Unknown"
                    new_dictionary['Section Title'] = "Unknown"
                new_dictionary['Search Terms'] = ','.join(instance['Search terms'])
                if instance['Link'] is not None and instance['Link'] != "No link":
                    new_dictionary['Link'] = f"{instance['Link']}#page={instance['Page']}"
                else:
                    new_dictionary['Link'] = ""
                new_dictionary['Page Number'] = instance['Page']
                new_dictionary['Reference'] = instance['Reference']
                try:
                    new_dictionary['Proposed amendment'] = instance['Amendment']
                    new_dictionary['Rationale'] = instance['Rationale']
                except:
                    new_dictionary['Proposed amendment'] = "No Amendment"
                    new_dictionary['Rationale'] = "No Rationale"
                dict_list.append(new_dictionary)

        return dict_list


    @staticmethod
    def adjust_json_dict_old(json_obj):

        if isinstance(json_obj, str):
            json_obj = json.loads(json_obj)

        # print("Adjusting json object")
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
            json_obj = ast.literal_eval(info_list)
        else:
            json_obj = info_list

        print("Adjusting json object")
        dict_list = []
        for instance in json_obj:
            new_dictionary = {}
            if instance[0] is not None:
                new_dictionary['Land Use Document type'] = instance[0]
            else:
                new_dictionary['Land Use Document type'] =""
            new_dictionary['Title'] = instance[1]
            new_dictionary['Section #'] = instance[4]
            new_dictionary['Section Title'] = instance[5]
            new_dictionary['Search Terms'] = instance[6]
            new_dictionary['Page Number'] = instance[3]
            if instance[2] is not None:
                new_dictionary['Link'] = f"{instance[2]}#page={instance[3]}"
            else:
                new_dictionary['Link'] = ""
            new_dictionary['Reference'] = instance[7]
            new_dictionary['Proposed amendment'] = "In Development"
            new_dictionary['Rationale'] = "In Development"
            dict_list.append(new_dictionary)

        return dict_list

    @staticmethod
    def prettify_excel(json_dict, output_file):
        df = pd.DataFrame(json_dict)

        with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:

            df.to_excel(writer, index=False, sheet_name='Sheet1')
            workbook = writer.book
            worksheet = writer.sheets['Sheet1']

            bold_format = workbook.add_format({'bold': True})

            col_idx = df.columns.get_loc('Reference')

            for index, row in df.iterrows():
                reference = row['Reference']
                search_terms = row['Search Terms'].split(',')

                escaped = [re.escape(term) for term in search_terms]
                pattern = '|'.join(escaped)
                regex_pattern = re.compile(f'({pattern})', re.IGNORECASE)
                result = regex_pattern.split(reference)
                result = [item for item in result if item.strip()]
                string_creator = []
                for item in result:
                    if item.lower() in search_terms:
                        string_creator.append(bold_format)
                    string_creator.append(item)

                worksheet.write_rich_string(index+1, col_idx, *string_creator)


if __name__ == "__main__":
    test_data = "instances.json"
    output_file = 'test5.xlsx'
    with open(test_data, 'r') as f:
        data = json.load(f)

    OutputHandler.create_excel_file(data, output_file)