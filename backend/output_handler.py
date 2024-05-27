import pandas as pd
from openpyxl import Workbook
import json
import re
import ast

class OutputHandler:

    @staticmethod
    def output_for_objective3(data, headers_df, process_status, excel_file_name):
        """
        Outputs data to an Excel file.

        Parameters:
        data (list): List of data to be written to the Excel file.
        headers_df (pd.DataFrame): DataFrame containing the headers.
        process_status (list): List containing the process status information.
        excel_file_name (str): Name of the Excel file to be created or appended to.

        Returns:
        None
        """
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
            df_process_status = pd.DataFrame(process_status)
            df_process_status.to_excel(writer, sheet_name="Process Status", index=False)

    @staticmethod
    def create_excel_file(json_obj, output_file="output.xlsx"):
        """
        Creates an Excel file from a JSON object.

        Parameters:
        json_obj (dict or str): JSON object or string to be converted to an Excel file.
        output_file (str): Name of the output Excel file. Defaults to "output.xlsx".

        Returns:
        None
        """
        json_dict = OutputHandler.adjust_json_dict_from_indexed(json_obj)

        OutputHandler.prettify_excel(json_dict, output_file)


    @staticmethod
    def adjust_json_dict_from_indexed(json_obj):

        """
        Adjusts a JSON dictionary from an indexed format.

        Parameters:
        json_obj (dict or str): JSON object or string to be adjusted.

        Returns:
        list: List of dictionaries with adjusted JSON data.
        """

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
    def prettify_excel(json_dict, output_file):
        """
        Prettifies the Excel output by formatting search terms in bold.

        Parameters:
        json_dict (list): List of dictionaries to be written to the Excel file.
        output_file (str): Name of the output Excel file.

        Returns:
        None
        """
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
                string_creator = OutputHandler.bold_search_terms(search_terms, result, bold_format)
                worksheet.write_rich_string(index+1, col_idx, *string_creator)

    @staticmethod
    def bold_search_terms(search_terms, result, bold_format):
        """
        Bolds search terms in the reference text.

        Parameters:
        search_terms (list): List of search terms to be bolded.
        result (list): List of text segments from the reference.
        bold_format: Excel bold format object.

        Returns:
        list: List of text segments with search terms in bold.
        """
        string_creator = []
        for term in result:
            if term.lower() in search_terms:
                string_creator.append(bold_format)
            string_creator.append(term)
        return string_creator


if __name__ == "__main__":
    test_data = "instances.json"
    output_file = 'test5.xlsx'
    with open(test_data, 'r') as f:
        data = json.load(f)

    OutputHandler.create_excel_file(data, output_file)