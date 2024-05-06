import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


def download_pdf(url, save_dir):
    # Create directory if it doesn't exist
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all links on the page
    links = soup.find_all('a')

    # Filter out links that point to PDF files
    pdf_links = [link.get('href') for link in links if link.get('href') and link.get('href').endswith('.pdf')]

    for pdf_link in pdf_links:
        # Construct absolute URL if the link is relative
        if not pdf_link.startswith('http'):
            pdf_link = urljoin(url, pdf_link)

        # Get the PDF filename from the URL
        pdf_filename = pdf_link.split('/')[-1]

        # Download the PDF
        with open(os.path.join(save_dir, pdf_filename), 'wb') as f:
            print("Downloading", pdf_filename)
            pdf_response = requests.get(pdf_link)
            f.write(pdf_response.content)

if __name__ == "__main__":
    # URL of the website to scrape
    website_url = "https://vancouver.ca/home-property-development/zoning-and-land-use-policies-document-library.aspx"

    # Directory to save the downloaded PDFs
    save_directory = "downloaded_pdfs"

    download_pdf(website_url, save_directory)