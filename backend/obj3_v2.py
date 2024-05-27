"""
This script is part of the COV PDS project, specifically for Objective 3:
Digitizing land use policies and regulations into table format for the LZR database.

Usage:
- You can run the enter_obj3(file_list) function by providing a list of filenames (excluding the .pdf extension).
- Alternatively, you can run the script directly by setting the filename in the main function.
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
SECTION3 = 'DENSITY, FORM AND PLACEMENT REGULATIONS'
SECTION4 = 'GENERAL REGULATIONS'

o3_message = ""
WAITING_TIME = 0

def is_contain_keyword(keyword, text):
    """
    Check if a keyword is present in the given text.

    Parameters:
    keyword (str): The keyword to search for.
    text (str): The text to search within.

    Returns:
    bool: True if the keyword is found, False otherwise.
    """
    if keyword.isupper():
        return re.search(keyword, text)
    else:
        return re.search(keyword, text, re.IGNORECASE)


def api_connect():
    """
    Establish a connection to the hugging chat API.

    Returns:
    Connection object: The connection to the API.
    """
    cookie_path_dir = "cookies/"  # NOTE: trailing slash (/) is required to avoid errors
    sign = Login(EMAIL, PASSWD)
    cookies = sign.login(cookie_dir_path=cookie_path_dir, save_cookies=True)
    # Create ChatBot
    return hugchat.ChatBot(cookies=cookies.get_dict())  # or cookie_path="usercookies/<email>.json"


def AI_process(input, use_context, chatbot, FSR_keywords):
    """
    Process input using AI to get the required information.

    Parameters:
    input (str): The input text to process.
    use_context(str): The input text for retrieving the context for 'Use'.
    chatbot (object): The chatbot instance used for AI processing.
    FSR_keywords (list): List of keywords to search for.

    Returns:
    an array of dictionaries: The result of the AI processing.
    """
    global o3_message
    max_retry = 3
    retry_count = 0
    while retry_count < max_retry:
        try:
            # get use
            use_prompt = ("Identify and list all the 'Use' categories and their corresponding section numbers from the "
                          "'Use' column and 'Density, Form and Placement Regulations' column in the input context. "
                          "Format each entry as 'Use name: section number'. Provide one 'Use' per line. Use the "
                          "following context:") + use_context
            use_case = chatbot.chat(use_prompt)
            time.sleep(WAITING_TIME)
            building_prompt = (
                    "Extract the 'Height Max(m)', 'maximum building height', and 'Height Max(Storeys)' values"
                    " from the entire passage for all the 'Use' categories listed in :" + use_case +
                    "Follow these guidelines: "
                    "1)For each 'Use', only search within the section that follows the 'Use' name."
                    "2)For each term, if there are multiple values, choose the maximum one."
                    "3)If a term value is not available, output 'None'."
                    "Output format:Use: [Use name]\n Height Max(m): [value] \nmaximum building height: [value]\n Height Max(Storeys): [value]\n"
                    "Use the following input context:" + input)

            building_result = chatbot.chat(building_prompt)
            time.sleep(WAITING_TIME)
            format_prompt = ("for all the 'Use' format the following context:'" + str(building_result)
                             + "' as: 'Use: xxx\n Height Max(m):xxx \nHeight Max(Storeys):xxx\n...\n',"
                               "where 'Height Max(m)' is the the max value of 'Height Max(m)' and 'maximum building height'")
            building_result = chatbot.chat(format_prompt)
            time.sleep(WAITING_TIME)
            # print(building_result)
            o3_message = f"Retrieved basic building information (step 2 of 4)"
            prompt = (("Extract the value of those terms and all FSR related values for each 'Use'."
                       "Note: 1)For each 'Use', only search within the section that follows the 'Use' name."
                       "2) FSR is short for 'floor space ratio';"
                       "3) start with one FSR,there are may be several scenarios for this FSR, list them all;"
                       "4) search for the second FSR, there may also have several scenarios for this FSR,"
                       " combine all the scenarios of the current and previous FSR, "
                       "be careful about there maybe some scenarios belongs to one of the first FSR scenario; keep searching for all terms"
                       " 5) For one scenario, there may be several other FSRs, list them all even if they are not in the terms I provided ;"
                       "6)'Total FSR Max' is the default FSR; "
                       "7) 'Residential FSR' is the floor space ratio for dwelling uses; "
                       "8)Output format like :"
                       "scenario: 1;Total FSR Max:xxx;term1:yyy;.....;termn:iii\n"
                       "scenario: 2;Total FSR Max: zzz;term2:kkk;.....;termn:iii\n....\n"
                       "scenario: n;Total FSR Max: zzz;term2:kkk;.....;termn:iii';"
                       "9)If the value is not available in the provided context do not list it. "
                       "Here is the terms to look for: ") + str(FSR_keywords) +
                      ".The Use cases are: " + str(use_case) + ";The input context is:" + input)
            fsr_result = chatbot.chat(prompt)
            time.sleep(WAITING_TIME)
            print(fsr_result)
            o3_message = f"Retrieved FSR information (step 3 of 4)"
            format_prompt = ("combine " + str(building_result) + "and" + str(fsr_result)
                             + "together based on 'Use'. "
                               "when combing, if one 'Use' has more than one scenario, "
                               "set terms in building_result for each scenario."
                               "Note: Output only one array of dictionary format like :"
                               "[{'Use':'xxx','Scenario': 1,'Total FSR Max':xxx,'term1':yyy,.....,'termn':iii},"
                               "{'Use':'xxx','Scenario': 2,'Total FSR Max': zzz,'term2':kkk,.....,'termn':iii},....,"
                               "{'Use':'xxx','Scenario': n,'Total FSR Max': zzz,'term2':kkk,.....,'termn':iii'}]")
            output_str = str(chatbot.chat(format_prompt))
            time.sleep(WAITING_TIME)

            start_index = output_str.find("[")
            end_index = output_str.find("]") + 1
            array_of_dicts_str = output_str[start_index:end_index]
            print(array_of_dicts_str)
            o3_message = f"Aggregate information for output (step 4 of 4)"

            modified_string = array_of_dicts_str.replace('null', 'None')
            array_of_dicts = eval(modified_string)
            return array_of_dicts
        except Exception as e:
            print(f"An error occurred: {e}")
            retry_count += 1
            time.sleep(2)
    return None


def get_date_and_title(text):
    """
    Get the title, last_amended information of the file.
    This is based on the format of file.

    Parameters:
    text (str): The input text to search.

    Returns:
    title(str): The title of the file,
    last_amended(str): The last amended date for the file.
    """
    footer = text.split('\n')[0]
    title_line = text.split('\n')[2]
    title = title_line[:len(title_line) // 2]
    parts = footer.split("City of Vancouver ", 1)  # Split the string at the first occurrence of 'city'
    title = parts[0].strip() if parts[0].strip() else title
    if len(parts) > 1:
        last_amended = parts[1].strip()
    else:
        last_amended = footer.replace("City of Vancouver ", "")
    return title, last_amended


def search_pdf(filename, chatbot, FSR_keywords):
    """
    Extract relevant context from a PDF and format the AI output.

    Parameters:
    filename (str): The name of the PDF file to search.
    chatbot (object): The chatbot instance used for AI processing.
    FSR_keywords (list): List of keywords to search for.

    Returns:
    boolean: True for AI successfully processed the file, False otherwise.
    array of dictionaries: with all the relevant information
    """
    global o3_message
    with open(filename, 'rb') as pdf_file:
        print('=' * 60)
        print('filename:', filename)
        o3_message = f"Starting with fie {filename}"
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
                o3_message = f"Retrieved document date and title (step 1 of 4)"

            if is_contain_keyword(SECTION1_2, page_text):
                index = page_text.index(SECTION1_2)
                use_context = page_text[index:]
            if is_contain_keyword(SECTION3, page_text):
                start_page = page_num
            if is_contain_keyword(SECTION4, page_text):
                end_page = page_num
                index = page_text.index(SECTION4)
                page_text = page_text[:index]

            if start_page <= page_num <= end_page:
                content += page_text

        AI_result = AI_process(content, use_context, chatbot, FSR_keywords)
        file_info_dicts = {'Zoning District': zoning_district, 'Last Amended': last_amended}
        if AI_result:
            # Iterate through each dictionary in the array
            for d in AI_result:
                # Add new key-value pairs to each dictionary
                d.update(file_info_dicts)

            # Print the updated array of dictionaries
            print(AI_result)
            return True, AI_result
        else:
            print('No valid AI output for file: ', filename)
            o3_message = f"Error: AI output is invalid for {filename}."
            return False, [file_info_dicts]


def save_to_json(temp_json_file, data):
    """
    Save intermediate results to a JSON file.

    Parameters:
    temp_json_file (str): The path to the JSON file.
    data (dict): The data to save.

    Returns:
    None
    """
    with open(temp_json_file, 'a') as json_file:
        for row_data in data:
            json.dump(row_data, json_file)
            json_file.write('\n')


def get_file_url(file_name, data_dict):
    """
    Get the URL of the input file.

    Parameters:
    file_name (str): The name of the file.
    data_dict (dict): The dictionary will all the files' information.

    Returns:
    str: The url of the file
    """
    global o3_message
    filename_key = file_name
    if filename_key in data_dict:
        details = data_dict[filename_key]
        doc_url = details["url"]
    else:
        doc_url = ''
        o3_message = f"Error: {filename_key}.pdf' is not found from local drive."
        print(f"Filename '{filename_key}.pdf' not found in the JSON data.")
    return doc_url


def enter_obj3(file_list):
    """
    Entry point for COV PDS project objective 3.
    Save the result excel to the backend folder.

    Parameters:
    file_list (list): List of filenames (without .pdf extension).

    Returns:
    file_content: the content of the file
    """

    global o3_message
    chatbot = api_connect()

    FSR_keywords = ['Total FSR Max', 'Residential FSR Max',
                    'Secured Market Rental FSR Max', 'Secured Market Rental%',
                    'Employment Required', 'Employment FSR Min', 'Employment FSR Max', 'Office Required',
                    'Office FSR Max', 'Commercial Retail Required', 'Commercial Retail FSR Min',
                    'Commercial Retail FSR Max',
                    'Hotel Required', 'Hotel FSR Min', 'Hotel FSR Max', 'Industrial Required', 'Industrial FSR Min',
                    'Industrial FSR Max']

    # Write the column headers
    all_terms = ['Fields', 'Zoning District', 'Last Amended', 'Use', 'Scenario', 'Minimum Site Area (m2)',
                 'Min Frontage (m)', 'Max Frontage (m)',
                 'Height Max(m)', 'Height Max(Storeys)', 'Front Setback Min', 'Side Setback Min', 'Rear Setback Min',
                 'Site coverage Max',
                 'Total FSR Min', 'Total FSR Max', 'Residential FSR Min', 'Residential FSR Max',
                 'Secured Market Rental FSR Min',
                 'Secured Market Rental FSR Max', 'Secured Market Rental%', 'Social Housing FSR Min',
                 'Social Housing FSR Max',
                 'Below Market Housing FSR Min', 'Below Market Housing FSR Max', 'Below Market Housing Percentage',
                 'Employment Required', 'Employment FSR Min', 'Employment FSR Max', 'Office Required',
                 'Office FSR Min', 'Office FSR Max',
                 'Commercial Retail Required', 'Commercial Retail FSR Min', 'Commercial Retail FSR Max',
                 'Hotel Required', 'Hotel FSR Min', 'Hotel FSR Max', 'Industrial Required', 'Industrial FSR Min',
                 'Industrial FSR Max', 'URL', 'Date of Extraction']

    df = pd.DataFrame(columns=all_terms)

    with open("doc_type.json", "r") as file:
        data = json.load(file)
    data_dict = {list(item.keys())[0]: list(item.values())[0] for item in data}

    current_date = datetime.datetime.now()
    formatted_date = current_date.strftime('%Y-%m-%d')
    temp_json_file = 'output_obj3.json'
    with open(temp_json_file, 'w') as json_file:
        pass

    process_status = []
    for file_name in file_list:
        full_file_name = os.path.join('downloaded_pdfs', file_name + '.pdf')
        url = get_file_url(file_name, data_dict)

        is_AI_works, result = search_pdf(full_file_name, chatbot, FSR_keywords)

        process_status.append({'File name': file_name + '.pdf', 'AI processed': is_AI_works})
        all_result = []

        for row_dict in result:
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
            keys_not_in_all_terms = [key for key in row_dict if key not in all_terms]
            if 'Scenarios' not in keys_not_in_all_terms:

                if 'Non-Dwelling FSR Max' in keys_not_in_all_terms:
                    row_data['Employment FSR Max'] = row_dict['Non-Dwelling FSR Max']
                    row_data['Employment Required'] = 'y'
                elif 'Non-Dwelling FSR Min' in keys_not_in_all_terms:
                    row_data['Employment FSR Min'] = row_dict['Non-Dwelling FSR Min']
                    row_data['Employment Required'] = 'y'
                all_result.append(row_data)
            else:
                if row_dict['Scenarios'] is not None:
                    for sc_row_dict in row_dict['Scenarios']:
                        sc_row_data = row_data.copy()
                        for term in all_terms:
                            if term in sc_row_dict:
                                sc_row_data[term] = sc_row_dict[term]
                        sc_keys_not_in_all_terms = [key for key in sc_row_dict if key not in all_terms]
                        if 'Non-Dwelling FSR Max' in keys_not_in_all_terms or 'Non-Dwelling FSR max' in sc_keys_not_in_all_terms:
                            sc_row_data['Employment FSR Max'] = sc_row_dict['Non-Dwelling FSR Max']
                            sc_row_data['Employment Required'] = 'y'
                        elif 'Non-Dwelling FSR Min' in keys_not_in_all_terms:
                            sc_row_data['Employment FSR Min'] = sc_row_dict['Non-Dwelling FSR Min']
                            sc_row_data['Employment Required'] = 'y'

                        all_result.append(sc_row_data)
        save_to_json(temp_json_file, all_result)
    output_filename = "output_obj3"
    formatted_time = current_date.strftime("%Y-%m-%d-%H%M")
    excel_file_name = f"{output_filename}_{formatted_time}.xlsx"

    with open(temp_json_file, 'r') as json_file:
        data = [json.loads(line) for line in json_file]
    # Create a new Excel file if it doesn't exist
    try:
        wb = Workbook()
        wb.save(excel_file_name)
    except Exception as e:
        print(f"An error occurred while creating the Excel file: {e}")
        o3_message = f"Error: There is a problem when creating the Excel output file."

    with ExcelWriter(excel_file_name, mode="a", engine="openpyxl", if_sheet_exists="overlay", ) as writer:
        df.to_excel(writer, sheet_name="Sheet", index=False)
        df = pd.DataFrame(data)
        df.to_excel(writer, sheet_name="Sheet", index=False)
        df_process_status = pd.DataFrame(process_status)
        df_process_status.to_excel(writer, sheet_name="Process Status", index=False)

    with open(excel_file_name, 'rb') as file:
        file_content = file.read()
    return file_content


def main():
    """
    Main function only for testing purposes.
    """
    # file_list = ['zoning-by-law-district-schedule-c-2', 'zoning-by-law-district-schedule-rm-9-9n-9bn']
    file_list = ['zoning-by-law-district-schedule-c-1']

    output = enter_obj3(file_list)
    print("end!")


if __name__ == '__main__':
    main()
