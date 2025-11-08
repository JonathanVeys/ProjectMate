import pypdf

# creating a pdf reader object
reader = pypdf.PdfReader( "/Users/jonathancrocker/Downloads/MLP2025_26_CW1_Spec.pdf")

# print the number of pages in pdf file
print(len(reader.pages))

# print the text of the first page
print(reader.pages[2].extract_text())
