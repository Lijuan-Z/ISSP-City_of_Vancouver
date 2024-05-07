import pandas as pd


class OutputHandler:

    @staticmethod
    def create_excel_file(json_obj, output_file="output.xlsx"):
        json_for_dataframe = {}
        for key, value in json_obj.items():
            json_for_dataframe[key] = json_obj[key]
            json_for_dataframe[key]["File name"] = key

        pd.DataFrame(json_for_dataframe).transpose().to_excel(output_file)

if __name__ == "__main__":
    output_handler = OutputHandler()
    test_json = {}
    test_json["file1.pdf"] = {"Title": "title1",
                              "Section #": "String with section header",
                              "Section Title": "section_title1",
                              "Search term identified": "search terms here",
                              "Reference": "String with the defined reference"
                              }

    test_json["file2.pdf"] = {"Title": "title2",
                              "Section #": "another_String with section header",
                              "Section Title": "section_title2",
                              "Search term identified": "search terms here",
                              "Reference": "another_String with the defined reference"
                              }

    OutputHandler.create_excel_file(test_json)
