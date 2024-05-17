import os
import PyPDF2
import re
from hugchat import hugchat
from hugchat.login import Login


from config import EMAIL, PASSWD


def gen_output(input,use_context):

    if input != '':
        prompt = "There may be several 'Use' in the input content Overview part and list all the 'Use'. The input context is:" + use_context
        use_case = chatbot.chat(prompt)
        prompt = "There may be several 'Use' in the input content Overview part and can you get value of those terms for each 'Use'. Note: FSR is short for 'floor space ratio';'Height Max(m)' is same as 'Maximum building height'. If the value is not available in the provided context no need to list it. Here is the terms to look for: " + str(keywords_list) + "The Use cases are: " + str(use_case) + ";The input context is:" + input
        query_result = chatbot.chat(prompt)
        print(query_result)
    else:
        print("The input is empty")


def search_pdf(filename):

    with open(filename, 'rb') as pdf_file:
        print('='*60)
        print('filename:',filename)
        pdf_reader = PyPDF2.PdfReader(pdf_file)

        total_page_number = len(pdf_reader.pages)
        start_page = total_page_number + 1
        end_page = total_page_number
        content = ''
        use_context = ''
        for page_num in range(total_page_number):
            page = pdf_reader.pages[page_num]
            page_text = page.extract_text()
            if is_contain_keyword('1.2 Overview', page_text):
                use_context = page_text
            if is_contain_keyword('DENSITY, FORM AND PLACEMENT REGULATIONS', page_text):
                start_page = page_num
            if is_contain_keyword('GENERAL REGULATIONS', page_text):
                end_page = page_num

            if page_num >= start_page and page_num <= end_page:
                content += page_text

        gen_output(content,use_context,)



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


if __name__ == '__main__':

    folder_path = 'temp_pdfs_obj3'
    output = []
    image_search_enabled = False

    chatbot = api_connect()
    keywords_list = ['Height Max(m)', 'Height Max(Storeys)', 'Total FSR Max', 'Residential FSR Max',
                     'Secured Market Rental FSR Max', 'Secured Market Rental',
                     'Employment Required', 'Employment FSR Min', 'Employment FSR Max', 'Office Required',
                     'Office FSR Max', 'Commercial Retail Required', 'Commercial Retail FSR Min',
                     'Commercial Retail FSR Max',
                     'Hotel Required', 'Hotel FSR Min', 'Hotel FSR Max', 'Industrial Required', 'Industrial FSR Min',
                     'Industrial FSR Max']

    for root, dirs, files in os.walk(folder_path):
        for file_name in files:
            if file_name.endswith('.pdf'):
                full_file_name = os.path.join(root, file_name)
                search_pdf(full_file_name)

    print("end!")
