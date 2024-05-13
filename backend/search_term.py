import os
import PyPDF2
import re
import easyocr
from hugchat import hugchat
from hugchat.login import Login
import json

from config import EMAIL, PASSWD


def search_pdf(keyword, filename, chatbot, file_type, url,image_search_enabled):
    pre_page_text = ''
    results = []
    try:
        with open(filename, 'rb') as pdf_file:

            pdf_reader = PyPDF2.PdfReader(pdf_file)
            if image_search_enabled:
                image_reader = easyocr.Reader(['en'])
                
            section_search_enabled = False
            
            title = pdf_reader.metadata.title
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                page_text = page.extract_text()

                if image_search_enabled:
                    for image in page.images:
                        # print(filename,' has image')
                        result = image_reader.readtext(image.data)
                        for (bbox, text, prob) in result:
                            if is_contain_keyword(keyword, text):
                                info = [file_type, title, url, page_num+1, '', 'image', keyword, text]
                                # print(info)
                                results.append(info)

                if is_contain_keyword(keyword, page_text):
                    paragraphs = page_text.split('\n \n')  # Assuming paragraphs are separated by one newline characters
                    # Iterate over each paragraph
                    for paragraph in paragraphs:
                        # Check if the keyword is present in the paragraph
                        if is_contain_keyword(keyword, paragraph):
                            if section_search_enabled:
                                prompt = "can you get the section number, section name of the following text? " + paragraph + " Return with the format: Section Number: xxx. \n Section Name: xxx. If you can't return None. here is the current page context" + page_text + ". And here is the pre page context " + pre_page_text
                                # prompt = "can you get the section number, section name of the following text? "+ paragraph + " Return with the section Number and section name with a new line seperate character between. If you can't, then return None. here is the current page context" + page_text + ". And here is the pre page context "+ pre_page_text
                                # prompt = "can you get the section number, section name of the following text? "+ paragraph + " Return with the section Number and section name. If you can't, then return None. here is the current page context" + page_text + ". And here is the pre page context "+ pre_page_text

                                query_result = chatbot.chat(prompt)
                                if str(query_result) != 'None':
                                    section = str(query_result).split('\n')
                                    try:
                                        section_number = section[0].split(":")[1]
                                        section_name = section[1].split(":")[1]
                                    except Exception as e:
                                        print(f"An error occurred: {e}")
                                        section_number = ''
                                        section_name = section

                                    info = [file_type, title, url, page_num+1, section_number, section_name, keyword, paragraph]
                                    print('section found!')
                                    results.append(info)
                                else:
                                    print('!!!!!result is none? section not found!!!!!!!!')
                                    info = [file_type, title, url, page_num+1, '', str(query_result), keyword, paragraph]
                                    results.append(info)
                            else:
                                info = [file_type, title, url, page_num+1, '', '', keyword, paragraph]
                                results.append(info)

                pre_page_text = page_text
    except Exception as e:
        print(f"An error occurred: filename {filename} ,error:{e}")

    return results


def is_contain_keyword(keyword, text):
    if keyword.isupper():
        return re.search(keyword, text)
    else:
        return re.search(keyword, text, re.IGNORECASE)


def get_file_info(key, data_dict):
    if key in data_dict:
        details = data_dict[key]
        doc_type = details["type"]
        doc_url = details["url"]
    else:
        doc_type = ''
        doc_url = ''
        print(f"Filename '{key}.pdf' not found in the JSON data.")
    return doc_type, doc_url


def api_connect():
    cookie_path_dir = "./cookies/"  # NOTE: trailing slash (/) is required to avoid errors
    sign = Login(EMAIL, PASSWD)
    cookies = sign.login(cookie_dir_path=cookie_path_dir, save_cookies=True)
    # Create ChatBot
    return hugchat.ChatBot(cookies=cookies.get_dict())  # or cookie_path="usercookies/<email>.json"


def searching_endpoint(keyword):
    folder_path = '../downloaded_pdfs'
    output = []
    image_search_enabled = True

    with open("doc_type.json", "r") as file:
        data = json.load(file)
    data_dict = {list(item.keys())[0]: list(item.values())[0] for item in data}

    chatbot = api_connect()
    count = 0
    for root, dirs, files in os.walk(folder_path):
        for file_name in files:
            if file_name.endswith('.pdf'):
                full_file_name = os.path.join(root, file_name)
                filename_key = file_name[:-4]
                file_type, url = get_file_info(filename_key, data_dict)
                count = count + 1
                print(f'file: {count}  name {filename_key}')
                output.extend(search_pdf(keyword, full_file_name, chatbot, file_type, url,image_search_enabled))

    return output
