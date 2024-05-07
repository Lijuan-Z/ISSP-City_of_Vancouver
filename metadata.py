import json
import os
import PyPDF2


def extract_metadata(pdf_path):
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            metadata = pdf_reader.metadata
    except Exception as e:
        print(f"Error reading PDF file '{pdf_path}': {e}")
        metadata = None

    return metadata


def convert_size_to_human_readable(size_in_bytes):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_in_bytes < 1024.0:
            return f"{size_in_bytes:.2f} {unit}"
        size_in_bytes /= 1024.0


def create_metadata_dictionary(folder_path):
    nested_metadata_dict = {}
    for root, dirs, files in os.walk(folder_path):
        for file_name in files:
            if file_name.endswith('.pdf'):
                file_path = os.path.join(root, file_name)
                metadata = extract_metadata(file_path)
                if metadata is not None:
                    # Convert size to human-readable format
                    size = os.path.getsize(file_path)
                    size_human_readable = convert_size_to_human_readable(size)
                    # Additional data to be added
                    additional_data = {
                        'Size': size_human_readable
                    }
                    # Merge metadata and additional data
                    metadata.update(additional_data)
                    nested_metadata_dict[file_name] = metadata
    return nested_metadata_dict


if __name__ == '__main__':
    # Example usage:
    # folder_path = 'test_pdfs'
    folder_path = 'downloaded_pdfs'
    nested_metadata_dict = create_metadata_dictionary(folder_path)
    # print(nested_metadata_dict)

    # Convert nested metadata dictionary to JSON string
    json_str = json.dumps(nested_metadata_dict, indent=4)

    # Print JSON string
    print(json_str)
