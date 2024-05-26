import pandas as pd
import os
import supabase
from sentence_transformers import SentenceTransformer
from supabase import create_client
import vecs
from vecs import IndexMethod, IndexMeasure

# create vector store client


url: str = "https://lxhspsysznpcwnpcxudi.supabase.co"
key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZ" \
           "SIsInJlZiI6Imx4aHNwc3lzem5wY3ducGN4dWRpIiwicm9sZSI6InNlcnZp" \
           "Y2Vfcm9sZSIsImlhdCI6MTcxNjcxNDkwNiwiZXhwIjoyMDMyMjkwOTA2fQ.oPhsr1eqmWCnOAgo91fSLEjR9XcYwarn3k7pF4SmQ0o"
DB_CONNECTION: str = "postgresql://postgres.lxhspsysznpcwnpcxudi:220101dommi!@aws-0-eu-central-1.pooler.supabase.com:5432/postgres"


def preprocesJobs():
    dataframe = pd.read_csv("../misc_files/job_descriptions.csv", na_values="drop")
    dataframe = dataframe.drop_duplicates(subset="Job Title")
    dataframe = dataframe[["Job Title", "Job Description"]].head(10000)
    dataframe.to_csv("../misc_files/preprocessed_job_description.csv", index=False)


def insertData():
    vx = vecs.create_client(DB_CONNECTION)
    vx.delete_collection(name="job_descriptions")
    docs = vx.get_or_create_collection(name="job_descriptions", dimension=384)

    docs.create_index(
        method=IndexMethod.auto,
        measure=IndexMeasure.cosine_distance
    )

    dataframe = pd.read_csv("../misc_files/preprocessed_job_description.csv")
    iterator = dataframe.iterrows()

    count = 0
    for index, val in iterator:
        print(count)
        model = SentenceTransformer("all-MiniLM-L6-v2")
        embedding = model.encode(val["Job Description"])
        docs.upsert([(val["Job Title"], embedding, {"description": val["Job Description"]})])
        count+=1

def retrieveKMostSimilar(embedding):
    vx = vecs.create_client(DB_CONNECTION)
    docs = vx.get_or_create_collection(name="job_descriptions", dimension=384)

    results = docs.query(
        data=embedding,
        limit=3,
        include_metadata=True
    )

    return formatResults(results)

def formatResults(results):
    promptString = ""
    for result in results:
        promptString += result[0] + ": " + result[1].get("description") + "\n"

    return promptString


def main():
    model = SentenceTransformer("all-MiniLM-L6-v2")
    embedding = model.encode("Electrical engineer")
    insertData()


if __name__ == '__main__':
    main()
