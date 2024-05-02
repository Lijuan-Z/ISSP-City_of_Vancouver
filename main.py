# Test for reading/searching pdf with text in the image.
import pypdf
import re
import easyocr


def main():
    keyword = 'R1-1'
    pages_with_keyword, images_with_keyword = search_pdf(keyword)

    print("Pages containing the keyword:", pages_with_keyword)
    print("Images containing the keyword:", images_with_keyword)


def search_pdf(keyword):
    pages_num = []
    images_page_num = []
    with open('example_doc.pdf', 'rb') as pdf_file:
        rdf_reader = pypdf.PdfReader(pdf_file)
        image_reader = easyocr.Reader(['en'])

        for page_num in range(len(rdf_reader.pages)):
            page = rdf_reader.pages[page_num]
            page_text = page.extract_text()
            for image in page.images:
                # images_page_num.append(page_num + 1)
                result = image_reader.readtext(image.data)
                for (bbox, text, prob) in result:
                    if re.search(keyword, text, re.IGNORECASE):
                        images_page_num.append(page_num + 1)
                        # print(f'Page: {page_num + 1},Text: {text}, Probability: {prob}')

            if re.search(keyword, page_text, re.IGNORECASE):
                # +1 because the page num starting from 1
                pages_num.append(page_num + 1)
    return pages_num, images_page_num


if __name__ == '__main__':
    main()
