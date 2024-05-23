import csv

import numpy as np
import sklearn
from matplotlib import pyplot as plt
from pandas import Series
from sentence_transformers import SentenceTransformer
import pandas as pd
from sklearn import cluster
from sklearn.cluster import KMeans


def embeddingsClustering():
    try:
        csvreader = pd.read_csv("..\misc_files\occupations.csv")
        data = csvreader[["Code", "Occupation"]]
        sentences = data.values.tolist()
        data = pd.DataFrame(data)
        data["Code"] = data["Code"].astype(str)
        data["Occupation"] = data["Occupation"].astype(str)
        model = SentenceTransformer("all-MiniLM-L6-v2")

        embeddings = model.encode(sentences)

        length = np.sqrt((embeddings ** 2).sum(axis=1))[:, None]
        embeddings = embeddings / length


        clustering = KMeans(n_clusters=10).fit(embeddings)
        data['Label'] = clustering.labels_
        print(data)
        data = data.sort_values(by='Label', ascending=True)
        data.to_csv("../misc_files/clustering_with_code.csv", index=False)




    except FileNotFoundError:
        print(f"The file does not exist.")
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")

def main():
    embeddingsClustering()

if __name__ == '__main__':
    main()
