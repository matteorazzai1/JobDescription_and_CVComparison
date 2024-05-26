import csv

import numpy as np
import sklearn
from matplotlib import pyplot as plt
from pandas import Series
from sentence_transformers import SentenceTransformer
import pandas as pd
from sklearn import cluster
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA


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

        pca = PCA(n_components = 50)
        reduced_embeddings = pca.fit_transform(embeddings)

        clustering = KMeans(n_clusters=10).fit(reduced_embeddings)
        data['Label'] = clustering.labels_
        print(data)
        print(clustering.inertia_)
        data = data.sort_values(by='Label', ascending=True)
        data.to_csv("../misc_files/clustering_prova.csv", index=False)




    except FileNotFoundError:
        print(f"The file does not exist.")
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")

def main():
    embeddingsClustering()

if __name__ == '__main__':
    main()
