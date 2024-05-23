import csv
from sentence_transformers import SentenceTransformer

def embeddings():
    try:
        with open("..\misc_files\occupations.csv", 'r', encoding='utf-8') as csvfile:
            csvreader = csv.reader(csvfile)
            print(csvreader)
        data = csvreader["Occupation"]
        model = SentenceTransformer("all-MiniLM-L6-v2")

        sentences = data.toList()
        print(sentences)
        embeddings = model.encode(sentences)

        for e in embeddings:
            print(e)


    except FileNotFoundError:
        print(f"The file does not exist.")
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")


