import httpx
import os
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import json
import time

def download_source_html(url):
    # response = requests.get(url)
    response = httpx.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup


def download_pdf(html, url, save_dir):
    global file_counter
    # Create directory if it doesn't exist
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    # Find all links on the page
    links = html.find_all('a')

    # Filter out links that point to PDF files
    pdf_links = [link.get('href') for link in links if link.get('href') and link.get('href').endswith('.pdf')]

    file_counter = 1
    total_files = len(pdf_links)
    for pdf_link in pdf_links:
        # Construct absolute URL if the link is relative
        if not pdf_link.startswith('http'):
            pdf_link = urljoin(url, pdf_link)

        # Get the PDF filename from the URL
        pdf_filename = pdf_link.split('/')[-1]

        # Download the PDF
        with open(os.path.join(save_dir, pdf_filename), 'wb') as f:

            print(f"Downloading pdf_file: {pdf_filename} {file_counter} of {total_files}")
            # pdf_response = requests.get(pdf_link)
            pdf_response = httpx.get(pdf_link)
            f.write(pdf_response.content)
            file_counter += 1

        # temp for testing
        if file_counter == 3:
            break


    return total_files


def retrieve_document_type(html, output_file):
    # soup = BeautifulSoup(html, 'html.parser')
    # print(soup)
    document_type = []
    # row = html.find_all(lambda tag: tag.get('class') == ['pd-blk-summary', 'border'])
    section_title = None
    contentBox = html.find_all("div", {"class": "blk-full"})
    # row = list(filter(lambda node: node.find('em') is not None or node.find('span') is not None, html.find_all('h2')))
    for row in contentBox:
        section_name = list(
            filter(lambda node: node.find('em') is not None or node.find('span') is not None, row.find_all('h2')))
        if len(section_name) > 0:
            section_title = section_name[0].text
            section_title = section_title.replace("\xa0", "")

        if section_title is not None:
            pdf_files = row.find_all('a')
            for file in pdf_files:
                if file.has_attr("href") and 'pdf' in file['href']:
                    document_type.append(
                        {
                            file['href'].split('/')[-1][:-4]: {
                                "type": section_title,
                                "title_original": file.text,
                                "title": (file.text.split("PDF file")[0]).replace("\u00a0", "").strip(),
                                # "title": file.text.split("\u00a0")[0],
                                "url": file['href'],
                                "file_updated": False,
                                "Last update": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()),
                                "checksum": "xxxxxxx"
                            }
                        }
                    )

    # [print(x) for x in document_type]
    # print(len(document_type))
    with open(output_file, 'w') as file:
        json.dump(document_type, file)


# if __name__ == "__main__":

    # # URL of the website to scrape
    # website_url = "https://vancouver.ca/home-property-development/zoning-and-land-use-policies-document-library.aspx"
    #
    # # Directory to save the downloaded PDFs
    # save_directory = "downloaded_pdfs"
    #
    # # Output file name for document_type json data
    # output_file = "doc_type_test.json"
    #
    # source_html = download_source_html(website_url)
    # # download_pdf(source_html, website_url, save_directory)
    # retrieve_document_type(source_html, output_file)

    # with open("source.html", "r", encoding="utf-8") as file:
    #     retreive_document_type(file)

