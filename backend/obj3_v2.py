"""
version 1, works for multiple files to excel
version 2, add error handling and improve AI accuracy
"""

import datetime
import json
import time
import os
import PyPDF2
import re
from hugchat import hugchat
from hugchat.login import Login
import pandas as pd
from openpyxl import Workbook
from pandas import ExcelWriter
from config import EMAIL, PASSWD

SECTION1_2 = '1.2 Overview'
SECTION2 = ''
SECTION3 = 'DENSITY, FORM AND PLACEMENT REGULATIONS'
SECTION3_1 = ''
SECTION3_2 = ''
SECTION4 = 'GENERAL REGULATIONS'


def is_contain_keyword(keyword, text):
    if keyword.isupper():
        return re.search(keyword, text)
    else:
        return re.search(keyword, text, re.IGNORECASE)


def api_connect():
    cookie_path_dir = "./cookies/"  # NOTE: trailing slash (/) is required to avoid errors
    sign = Login(EMAIL, PASSWD)
    cookies = sign.login(cookie_dir_path=cookie_path_dir, save_cookies=True)
    # Create ChatBot
    return hugchat.ChatBot(cookies=cookies.get_dict())  # or cookie_path="usercookies/<email>.json"


def AI_process(input, use_context,chatbot,building_keywords,FSR_keywords):
    max_retry = 3
    retry_count = 0
    while retry_count < max_retry:
        try:
            # get use
            use_prompt = ("There may be several 'Use' in the input content Overview part, "
                          "list all the 'Use'(no other explanation, one 'Use' per line) only based on the following context:") + use_context
            use_case = chatbot.chat(use_prompt)

            # building_prompt = (
            #         "Extract the 'Height Max(m)','maximum building height' and 'Height Max(Storeys)' from the entire passage: '" + input +
            #         "' for all the 'Use' in: '" + use_case +
            #         "'. Note: 1)If there are more than one possibility for one Use output the maximum one."
            #         "2)If the result is not available, output None."
            #         "Please output format as: 'Use\n Height Max(m):xxx \nHeight Max(Storeys):xxx\n',"
            #         "where 'Height Max(m)' is the the max value of 'Height Max(m)' and 'maximum building height' ")
            building_prompt = ("Extract all the 'Height Max(m)','maximum building height' and 'Height Max(Storeys)' value from the entire passage: '" + input +
                    "' for all the 'Use' in: '" + use_case +
                    "'. Note: 1)Each term,if there are more than one possibility for one Use choose the maximum one."
                    "2)If the result is not available, output None."
                    "Please output format as: 'Use: xxx\n Height Max(m):xxx \nmaximum building height: xxx\nHeight Max(Storeys):xxx\n',")
                    # "where 'Height Max(m)' is the the max value of 'Height Max(m)' and 'maximum building height' ")
            building_result = chatbot.chat(building_prompt)
            format_prompt = ("for all the 'Use' format the following context:'" + str(building_result)
                             + "' as: 'Use: xxx\n Height Max(m):xxx \nHeight Max(Storeys):xxx\n',"
                             "where 'Height Max(m)' is the the max value of 'Height Max(m)' and 'maximum building height'")
            building_result = chatbot.chat(format_prompt)
            print(building_result)

            # get FSR
            # prompt = (("Extract the value of those terms for each 'Use'."
            #            "Note: 0) FSR is short for 'floor space ratio';"
            #            # "1)"
            #            # "1)'Total FSR Max' same as 'Residential FSR Max',so the value for those two should be the same in the same scenario;"
            #            " 1) There may be several scenarios for one FSR, list them all;"
            #            " 2) For one scenario, there may have other FSR with several scenarios, then expand this scenario to several scenarios."
            #             " 3) For one scenario, there may be several other FSRs, list them all even if they are not in the terms I provided ;"
            #            "4)'Total FSR Max' is the default FSR; "
            #            "5) Output format like :'scenario: 1;Total FSR Max:xxx;term1:yyy;.....;termn:iii\n"
            #            "scenario: 2;Total FSR Max: zzz;term2:kkk;.....;termn:iii\n....\n"
            #            "scenario: n;Total FSR Max: zzz;term2:kkk;.....;termn:iii';"
            #            "6)If the value is not available in the provided context no need to list it. "
            #            "Here is the terms to look for: ") + str(FSR_keywords) +
            #           ".The Use cases are: " + str(use_case) + ";The input context is:" + input)
            prompt = (("Extract the value of those terms for each 'Use'."
                       "Note: 0) FSR is short for 'floor space ratio';"
                       "1) start with one FSR,there are may be several scenarios for this FSR, list them all;"
                       "2) search for the second FSR, there may also have several scenarios for this FSR,"
                       " combine all the scenarios of the current and previous FSR, be careful about there maybe some scenarios belongs to one of the first FSR scenario; keep searching for all terms"
                       # " 2) For one scenario, there may have other FSR with several scenarios, then expand this scenario to several scenarios."
                        " 3) For one scenario, there may be several other FSRs, list them all even if they are not in the terms I provided ;"
                       "4)'Total FSR Max' is the default FSR; "
                       "5) Output format like :'scenario: 1;Total FSR Max:xxx;term1:yyy;.....;termn:iii\n"
                       "scenario: 2;Total FSR Max: zzz;term2:kkk;.....;termn:iii\n....\n"
                       "scenario: n;Total FSR Max: zzz;term2:kkk;.....;termn:iii';"
                       "6)If the value is not available in the provided context no need to list it. "
                       "Here is the terms to look for: ") + str(FSR_keywords) +
                      ".The Use cases are: " + str(use_case) + ";The input context is:" + input)
            fsr_result = chatbot.chat(prompt)
            print(fsr_result)

            format_prompt = ("combine " + str(building_result) + "and" + str(fsr_result)
                             + "together based on 'Use'. "
                               "when combing, if one 'Use' has more than one scenario, set terms in building_result for each scenario."
                               # "'Total FSR Max' is same as 'Residential FSR Max',so the value for those two should be the same in the same scenario and 'Use';"
                               "Output only one array of dictionary format like :"
                               "[{'Use':'xxx','Scenario': 1,'Total FSR Max':xxx,'term1':yyy,.....,'termn':iii},"
                               "{'Use':'xxx','Scenario': 2,'Total FSR Max': zzz,'term2':kkk,.....,'termn':iii},....,"
                               "{'Use':'xxx','Scenario': n,'Total FSR Max': zzz,'term2':kkk,.....,'termn':iii'}]")
            output_str = str(chatbot.chat(format_prompt))

            start_index = output_str.find("[")
            end_index = output_str.rfind("]") + 1
            array_of_dicts_str = output_str[start_index:end_index]
            print(array_of_dicts_str)
            array_of_dicts = eval(array_of_dicts_str)
            return array_of_dicts
        except Exception as e:
            print(f"An error occurred: {e}")
            retry_count += 1
            time.sleep(2)
    return None


def get_date_and_title(text):
    footer = text.split('\n')[0]
    title_line = text.split('\n')[2]
    title = title_line[:len(title_line) // 2]
    last_amended = footer.replace("City of Vancouver ", "")
    return title, last_amended


def search_pdf(filename,chatbot,building_keywords,FSR_keywords):
    with open(filename, 'rb') as pdf_file:
        print('=' * 60)
        print('filename:', filename)
        pdf_reader = PyPDF2.PdfReader(pdf_file)

        total_page_number = len(pdf_reader.pages)
        start_page = total_page_number + 1
        end_page = total_page_number
        content = ''
        use_context = ''
        for page_num in range(total_page_number):
            page = pdf_reader.pages[page_num]
            page_text = page.extract_text()
            if page_num == 0:
                zoning_district, last_amended = get_date_and_title(page_text)
                print(zoning_district, last_amended)

            if is_contain_keyword(SECTION1_2, page_text):
                index = page_text.index(SECTION1_2)
                use_context = page_text[index:]
                # print(use_context)
            if is_contain_keyword(SECTION3, page_text):
                start_page = page_num
            if is_contain_keyword(SECTION4, page_text):
                end_page = page_num
                index = page_text.index(SECTION4)
                page_text = page_text[:index]

            if page_num >= start_page and page_num <= end_page:
                content += page_text

        AI_result = AI_process(content, use_context,chatbot,building_keywords,FSR_keywords)
        file_info_dicts = {'Zoning District': zoning_district, 'Last Amended': last_amended}
        if AI_result:
            # Iterate through each dictionary in the array
            for d in AI_result:
                # Add new key-value pairs to each dictionary
                d.update(file_info_dicts)

            # Print the updated array of dictionaries
            print(AI_result)
        else:
            print('No valid AI output for file: ',filename)
    return AI_result

def save_to_json(temp_json_file,data):
    with open(temp_json_file, 'a') as json_file:
        for row_data in data:
            json.dump(row_data, json_file)
            json_file.write('\n')


def get_file_url(file_name, data_dict):
    # filename_key = file_name[:-4]
    filename_key = file_name
    if filename_key in data_dict:
        details = data_dict[filename_key]
        doc_url = details["url"]
    else:
        doc_url = ''
        print(f"Filename '{filename_key}.pdf' not found in the JSON data.")
    return doc_url

def enter_obj3(file_list):
    folder_path = 'test_pdfs'
    chatbot = api_connect()

    keywords_list = ['Height Max(m)', 'Height Max(Storeys)', 'Total FSR Max', 'Residential FSR Max',
                     'Secured Market Rental FSR Max', 'Secured Market Rental',
                     'Employment Required', 'Employment FSR Min', 'Employment FSR Max', 'Office Required',
                     'Office FSR Max', 'Commercial Retail Required', 'Commercial Retail FSR Min',
                     'Commercial Retail FSR Max',
                     'Hotel Required', 'Hotel FSR Min', 'Hotel FSR Max', 'Industrial Required', 'Industrial FSR Min',
                     'Industrial FSR Max']
    FSR_keywords = ['Total FSR Max', 'Residential FSR Max',
                    'Secured Market Rental FSR Max', 'Secured Market Rental',
                    'Employment Required', 'Employment FSR Min', 'Employment FSR Max', 'Office Required',
                    'Office FSR Max', 'Commercial Retail Required', 'Commercial Retail FSR Min',
                    'Commercial Retail FSR Max',
                    'Hotel Required', 'Hotel FSR Min', 'Hotel FSR Max', 'Industrial Required', 'Industrial FSR Min',
                    'Industrial FSR Max']
    # building_keywords = ['Minimum Site Area (m2)', 'Min Frontage (m)', 'Max Frontage (m)', 'Height Max(m)',
    #                      'Height Max(Storeys)', 'Front Setback Min', 'Side Setback Min',
    #                      'Rear Setback Min', 'Site coverage Max']
    building_keywords = ['Height Max(m)', 'Height Max(Storeys)']

    # Write the column headers
    all_terms = ['Fields', 'Zoning District', 'Last Amended', 'Use', 'Scenario', 'Minimum Site Area (m2)',
                 'Min Frontage (m)', 'Max Frontage (m)',
                 'Height Max(m)', 'Height Max(Storeys)', 'Front Setback Min', 'Side Setback Min', 'Rear Setback Min',
                 'Site coverage Max',
                 'Total FSR Min', 'Total FSR Max', 'Residential FSR Min', 'Residential FSR Max',
                 'Secured Market Rental FSR Min',
                 'Secured Market Rental FSR Max', 'Secured Market Rental %', 'Social Housing FSR Min',
                 'Social Housing FSR Max',
                 'Below Market Housing FSR Min', 'Below Market Housing FSR Max', 'Below Market Housing Percentage',
                 'Employment  Required', 'Employment FSR Min', 'Employment FSR Max', 'Office Required',
                 'Office FSR Min', 'Office FSR Max',
                 'Commercial Retail Required', 'Commercial Retail FSR Min', 'Commercial Retail FSR Max',
                 'Hotel Required', 'Hotel FSR Min', 'Hotel FSR Max', 'Industrial Required', 'Industrial FSR Min',
                 'Industrial FSR Max', 'URL', 'Date of Extraction']

    df = pd.DataFrame(columns=all_terms)

    output_obj3 = []

    with open("doc_type.json", "r") as file:
        data = json.load(file)
    data_dict = {list(item.keys())[0]: list(item.values())[0] for item in data}

    current_date = datetime.datetime.now()
    formatted_date = current_date.strftime('%Y-%m-%d')
    temp_json_file = 'output_obj3.json'
    with open(temp_json_file, 'w') as json_file:
        pass

    for file_name in file_list:
        full_file_name = os.path.join('../downloaded_pdfs', file_name + '.pdf')
        url = get_file_url(file_name, data_dict)

        result = search_pdf(full_file_name, chatbot, building_keywords, FSR_keywords)
        all_result = []
        for row_dict in result:
            # Fill in the rows of the DataFrame
            row_data = {}
            for term in all_terms:
                if term in row_dict:
                    row_data[term] = row_dict[term]
                elif term == 'URL':
                    row_data[term] = url
                elif term == 'Date of Extraction':
                    row_data[term] = formatted_date
                else:
                    row_data[term] = ''
            all_result.append(row_data)
            # output_obj3.append(row_data)
        save_to_json(temp_json_file, all_result)

    excel_file_name = 'output_obj3.xlsx'
    with open(temp_json_file, 'r') as json_file:
        data = [json.loads(line) for line in json_file]
    # Create a new Excel file if it doesn't exist
    try:
        wb = Workbook()
        wb.save(excel_file_name)
    except Exception as e:
        print(f"An error occurred while creating the Excel file: {e}")
    with ExcelWriter(excel_file_name, mode="a", engine="openpyxl", if_sheet_exists="overlay", ) as writer:
        df.to_excel(writer, sheet_name="Sheet", index=False)
        df = pd.DataFrame(data)
        df.to_excel(writer, sheet_name="Sheet", index=False)

    with open(excel_file_name, 'rb') as file:
        file_content = file.read()
    return file_content


if __name__ == '__main__':
    file_list = ["zoning-by-law-district-schedule-fc-1", "zoning-by-law-district-schedule-r1-1"]
    output = enter_obj3(file_list)
    print("end!")


