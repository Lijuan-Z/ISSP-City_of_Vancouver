import httpx
import os
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import json
import pytz, datetime
import hashlib

file_counter = 0
total_files = 0

def download_source_html(url):
    # response = requests.get(url)
    response = httpx.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup


def download_pdf(html, url, save_dir):
    global file_counter
    global total_files
    # Create directory if it doesn't exist
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    # Find all links on the page
    links = html.find_all('a')

    # Filter out links that point to PDF files
    pdf_links = [link.get('href') for link in links if link.get('href') and "pdf" in link.get('href').lower()]

    file_counter = 1
    total_files = len(pdf_links)
    for pdf_link in pdf_links:
        # Construct absolute URL if the link is relative
        if not pdf_link.startswith('http'):
            pdf_link = urljoin(url, pdf_link)

        # Get the PDF filename from the URL
        pdf_filename = pdf_link.split('/')[-1]

        try:
            # Download the PDF
            pdf_response = httpx.get(pdf_link)

            if pdf_response.status_code == 301:
                new_url = str(pdf_response.next_request.url)
                print(f"Redirected to {new_url}")
                # pdf_filename = new_url.split('/')[-1]
                pdf_response = httpx.get(new_url)

            print(f"Downloading {file_counter} pdf_file from {url}: {pdf_filename}")
            with open(os.path.join(save_dir, pdf_filename), 'wb') as f:

                f.write(pdf_response.content)
                file_counter += 1
        except Exception as e:
            print(f"{e}")
            print(f"There is error on downloading and creating {pdf_filename}, file skipped")
            file_counter += 1
            continue

    return total_files

def download_pdf_voc_bylaws(html, save_dir, previous_total=0):
    # Create directory if it doesn't exist
    global file_counter
    global total_files
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    # Find all links on the page
    sub_pages = html.find("div", {"id": "simpleList1117"}).findAll("a")

    file_counter = previous_total
    total_files = previous_total
    for page in sub_pages:
        subpage_url = "https://vancouver.ca/" + page["href"]
        res = httpx.get(subpage_url)
        subpage_html = BeautifulSoup(res.text, 'html.parser')

        # Filter out links that point to PDF files
        links = list(filter(lambda t: t.get('href') is not None and 'pdf' in t.get('href').lower(), subpage_html.find_all('a')))
        for link in links:


            link = link.get('href')
            # Construct absolute URL if the link is relative
            if not link.startswith('http'):
                link = urljoin(subpage_url, link)

            # Get the PDF filename from the URL
            pdf_filename = link.split('/')[-1].split("#")[0]
            try:
                # Download the PDF
                pdf_response = httpx.get(link)
                print(f"Downloading {file_counter} pdf_file from {page.get('href')}: {pdf_filename}")
                if pdf_response.status_code == 301:
                    new_url = str(pdf_response.next_request.url)
                    print(f"Redirected to {new_url}")
                    # pdf_filename = new_url.split('/')[-1].split("#")[0]
                    pdf_response = httpx.get(new_url)

                with open(os.path.join(save_dir, pdf_filename), 'wb') as f:
                    f.write(pdf_response.content)
                    file_counter += 1
                    total_files += 1
            except Exception as e:
                print(f"{e}")
                print(f"There is error on downloading and creating {pdf_filename}, file skipped")
                total_files += 1
                continue



    return file_counter
def retrieve_document_type(html, html2, previous_record, output_file):
    # soup = BeautifulSoup(html, 'html.parser')
    # print(soup)

    document_type = []

    # handling zoning-and-land-use-policies-document-library website
    section_title = None
    contentBox = html.find_all("div", {"class": "blk-full"})
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

                    pdf_filename = file.get('href').split('/')[-1]
                    pdf_filename = pdf_filename.split('#')[0][:-4]

                    # update checksum, last update if a new file was downloaded
                    file_data = (list(filter(lambda obj: list(obj.keys())[0] == pdf_filename,previous_record)))

                    if len(file_data):
                        file_data = file_data[0][pdf_filename]

                        last_update = file_data["Last update"]
                        checksum = file_data["checksum"]
                        if file_data["file_updated"]:
                            with open(f"downloaded_pdfs/{pdf_filename}.pdf", "rb") as new_pdf_file_content:
                                checksum = generate_checksum(new_pdf_file_content.read())
                                # last_update = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
                                last_update = datetime.datetime.now(pytz.timezone('America/Vancouver')).strftime("%Y-%m-%d %H:%M:%S")



                        document_type.append(
                            {
                                pdf_filename: {
                                    "type": section_title,
                                    "title_original": file.text,
                                    "title": (file.text.split("PDF file")[0]).replace("\u00a0", "").strip(),
                                    # "title": file.text.split("\u00a0")[0],
                                    "url": file['href'],
                                    "file_updated": False,
                                    "Last update": last_update,
                                    "checksum": checksum
                                }
                            }
                        )
                    else:
                        print(f"file not find with the name: {pdf_filename}")


    # handling vancouvers-most-referenced-bylaws
    sub_pages = html2.find("div", {"id": "simpleList1117"}).findAll("a")

    for page in sub_pages:
        section_title = page["href"].replace("/your-government/", "").replace(".aspx", "")
        subpage_url = "https://vancouver.ca/" + page["href"]
        res = httpx.get(subpage_url)
        subpage_html = BeautifulSoup(res.text, 'html.parser')

        # Filter out links that point to PDF files
        links = list(
            filter(lambda t: t.get('href') is not None and 'pdf' in t.get('href').lower(),
                   subpage_html.find_all('a')))
        for link in links:

            url = link.get('href')
            # # Construct absolute URL if the link is relative
            if not url.startswith('http'):
                url = urljoin(subpage_url, url)

            # Get the PDF filename from the URL
            pdf_filename = link.get('href').split('/')[-1]
            # if len(pdf_filename.split('#')) > 1:
            #     pdf_filename = pdf_filename.split('#')[0][:-4] + "#" + pdf_filename.split('#')[1]
            # else:
            pdf_filename = pdf_filename.split('#')[0][:-4]

            # update checksum, last update if a new file was downloaded
            file_data = (list(filter(lambda obj: list(obj.keys())[0] == pdf_filename, previous_record)))

            if len(file_data):
                file_data = file_data[0][pdf_filename]

                last_update = file_data["Last update"]
                checksum = file_data["checksum"]
                if file_data["file_updated"]:
                    with open(f"downloaded_pdfs/{pdf_filename}.pdf", "rb") as new_pdf_file_content:
                        checksum = generate_checksum(new_pdf_file_content.read())
                        last_update = datetime.datetime.now(pytz.timezone('America/Vancouver')).strftime("%Y-%m-%d %H:%M:%S")

                document_type.append(
                    {
                        pdf_filename: {
                            "type": section_title,
                            "title_original": link.text,
                            "title": (link.text.split("PDF file")[0]).replace("\u00a0", "").strip(),
                            "url": url,
                            "file_updated": False,
                            "Last update": last_update,
                            "checksum": checksum
                        }
                    }
                )
            else:
                print(f"file not find with the name: {pdf_filename}")

    # [print(x) for x in document_type]
    # print(len(document_type))
    with open(output_file, 'w') as file:
        json.dump(document_type, file)

    print("document type file is created")

def add_unpaired_file(pdf_folder, doc_type_file):
    # add the extra pdf file
    file_count = 0
    json_file = read_previous_source(doc_type_file)
    for root, dirs, files in os.walk(pdf_folder):
        for pdf_filename in files:
            found_file = (list(filter(lambda obj: list(obj.keys())[0] == pdf_filename[:-4], json_file)))
            if len(found_file) == 0:
                file_count += 1
                with open(f"downloaded_pdfs/{pdf_filename}", "rb") as new_pdf_file_content:
                    checksum = generate_checksum(new_pdf_file_content.read())
                    last_update = datetime.datetime.now(pytz.timezone('America/Vancouver')).strftime("%Y-%m-%d %H:%M:%S")
                    json_file.append(
                        {
                            pdf_filename[:-4]: {
                                "type": "Unknown",
                                "title_original": "Unknown",
                                "title": "Unknown",
                                "url": "Unknown",
                                "file_updated": False,
                                "Last update": last_update,
                                "checksum": checksum
                            }
                        }
                    )

    with open(doc_type_file, 'w') as file:
        json.dump(json_file, file)
        print(f"{file_count} is added to the {doc_type_file}")




def read_previous_source(json_file):
    with open(json_file, "r", encoding="utf-8") as source_file:
        return json.load(source_file)

def generate_checksum(bytes_file):
    hasher = hashlib.md5()
    hasher.update(bytes_file)
    return hasher.hexdigest()



if __name__ == "__main__":

    # URL of the website to scrape
    website_url = "https://vancouver.ca/home-property-development/zoning-and-land-use-policies-document-library.aspx"
    website_url2 = "https://vancouver.ca/your-government/vancouvers-most-referenced-bylaws.aspx"

    # Directory to save the downloaded PDFs
    save_directory = "downloaded_pdfs"

    # Output file name for document_type json data
    output_file = "doc_type.json"

    previous_dl_file_info = read_previous_source(output_file)

    source_html = download_source_html(website_url)
    source_html2 = download_source_html(website_url2)
    # download_pdf(source_html, website_url, save_directory)
    # download_pdf_voc_bylaws(source_html2, save_directory, 0)
    # retrieve_document_type(source_html, source_html2, previous_dl_file_info, output_file)
    # add_unpaired_file("downloaded_pdfs", "doc_type.json")


    # with open("source.html", "r", encoding="utf-8") as file:
    #     retreive_document_type(file)

