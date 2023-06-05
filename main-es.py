import json
import PyPDF2
import os
import re
from datetime import datetime

def read_bible_books(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        bible_books = [line.strip() for line in file.readlines() if line.strip()]
    return bible_books

def datetime_to_string(date):
    if date is None:
        return ""
    return date.strftime("%Y-%m-%d")

def transform_month_names_to_numbers(date_temp):
    month_names = [
        "enero",
        "febrero",
        "marzo",
        "abril",
        "mayo",
        "junio",
        "julio",
        "agosto",
        "septiembre",
        "octubre",
        "noviembre",
        "diciembre"
    ]
    for index, month_name in enumerate(month_names, start=1):
        date_temp = date_temp.replace(month_name, str(index))
    return date_temp

def extract_text_from_pdf(pdf_path, start_page, end_page, bible_books):
    text_records = []
    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        num_pages = len(reader.pages)
        for page_num in range(start_page, min(end_page, num_pages)):
            page = reader.pages[page_num]
            text = page.extract_text()
            date_display, _, remaining_text = text.partition("\n")  # Split text into date_display and remaining text
            # Add a space between a number and a letter
            remaining_text = re.sub(r"(\d)([A-Za-z])", r"\1 \2", remaining_text)


            # Remove text until the fourth "•" character in the date_display
            _, _, date_display = date_display.partition("•")
            _, _, date_display = date_display.partition("•")
            _, _, date_display = date_display.partition("•")
            _, _, date_display = date_display.partition("•")

            # Remove "DE" from the date_display
            date_temp = date_display.replace("DE ", "")

            # Add "de 2023" to the end of date_temp
            date_temp += " de 2023"

            # Remove consecutive spaces larger than one character from date_temp
            date_temp = re.sub(r"\s{2,}", " ", date_temp)

            # Transform month names to numbers in date_temp
            date_temp = transform_month_names_to_numbers(date_temp)

            # Remove "de " from date_temp
            date_temp = date_temp.replace("de ", "")

            # Replace all blank spaces with "/"
            date_temp = date_temp.replace(" ", "/")

            # Convert date_temp to datetime format
            try:
                date = datetime.strptime(date_temp, "%d/%m/%Y")
                print(date)
            except ValueError:
                date = None

            title, _, remaining_text = remaining_text.partition("\n")  # Split remaining text into title and remaining text
            
            


            verse_text = remaining_text
            for book in bible_books:
                if book in remaining_text:
                    verse_text, _, _ = remaining_text.partition(book)
                    break

            # Remove verse_text from the remaining text
            remaining_text = remaining_text.replace(verse_text, "")

            # Remove '\n' characters from verse_text
            verse_text = verse_text.replace("\n", "")

            # Cut the text from remaining_text until the next '\n' and assign it to verse_ref
            verse_ref, _, remaining_text = remaining_text.partition("\n")

            # Remove '\n' from remaining_text unless the next letter is uppercase or '-'
            cleaned_text = ""
            index = 0
            while index < len(remaining_text):
                if remaining_text[index] == "\n":
                    if index + 1 < len(remaining_text):
                        if remaining_text[index + 1].isupper() or remaining_text[index + 1] == "-":
                            cleaned_text += "\n"
                    index += 1
                else:
                    cleaned_text += remaining_text[index]
                    index += 1

            # Remove the specific string from cleaned_text
            cleaned_text = cleaned_text.replace(
                "46149 – Meditação Por do Sol - 2023\nDesigner Editor(a) Coor. Ped. C. Q. R. F . Marketing14 October 2022 9:50 am\nP1\nP2", ""
            )
            text_record = {
                "page_number": page_num + 1,
                "text": cleaned_text.strip(),
                "date_display": date_display.strip(),
                "date_temp": date_temp.strip(),
                "date": datetime_to_string(date),
                "title": title.strip(),
                "verse_text": verse_text.strip(),
                "verse_ref": verse_ref.strip()
            }   
            text_records.append(text_record)
    return text_records

# Provide the path to your PDF file
pdf_path = "./113687-Meditaciones_para_la_puesta_del_sol_2023.pdf"

# Specify the page range (starting from 0) to extract text from
start_page = 5  # Page 6 in zero-based index
end_page = 57  # Page 58 in zero-based index

# Specify the path to the file containing Bible books
bible_books_file_path = "./bible_books.txt"

# Read the Bible books from the file
bible_books = read_bible_books(bible_books_file_path)

# Call the function to extract text from the specified page range
extracted_text_records = extract_text_from_pdf(pdf_path, start_page, end_page, bible_books)

# Create a dictionary to store the extracted text array
data = {
    "text_records": extracted_text_records
}

# Get the directory path of the PDF file
pdf_dir = os.path.dirname(pdf_path)

# Construct the JSON file path in the same directory as the PDF file
json_file_path = os.path.join(pdf_dir, "output-es.json")

# Write the data to a JSON file with UTF-8 encoding
with open(json_file_path, "w", encoding="utf-8") as json_file:
    json.dump(data, json_file, ensure_ascii=False, default=datetime_to_string)


print("Text extracted from page", start_page, "to", end_page, "has been saved to", json_file_path)
