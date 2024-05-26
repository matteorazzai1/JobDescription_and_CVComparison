from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import PyPDF2
from docx import Document
import os
from groq import Groq

from AppLogic.sectionsSummary import summarizeSection
from Utils.dbManager import retrieveKMostSimilar


def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfFileReader(file)
        text = ''
        for page_num in range(reader.numPages):
            page = reader.getPage(page_num)
            text += page.extract_text()
    return text


def extract_text_from_docx(docx_path):
    doc = Document(docx_path)
    text = ''
    for paragraph in doc.paragraphs:
        text += paragraph.text + '\n'
    return text


def performRequest(prompt):
    client = Groq(
        api_key='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'
    )

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content":
                    f"{prompt}",
            }
        ],
        model="llama3-70b-8192",
    )
    return chat_completion.choices[0].message.content


def main(file_path, file_type, job_code, job_name):
    if file_type == 'pdf':
        file_content = extract_text_from_pdf(file_path)
    elif file_type == 'docx':
        file_content = extract_text_from_docx(file_path)
    else:
        raise ValueError("Unsupported file type. Use 'pdf' or 'docx'.")

    CV_description = performRequest(f"Can you try to take this content related to the text extracted from a curriculum vitae and describe it trying to concentrate on the working skills in a detailed manner and avoiding section that not regards working skills? please avoid pointed list and try to summarize{file_content}")
    #print(CV_description)

    # derive embeddings and compute cosine similarity
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

    work_activities = summarizeSection("work activities", job_code, job_name, True)
    skills = summarizeSection("skills", job_code, job_name, True)
    tasks = summarizeSection("tasks", job_code, job_name, True)

    prompt = (
            "Can you summarize a description for the job described with the following fields: "
            + work_activities + ", " + skills + ", and " + tasks + "? "
            "This is about an open position for a " + job_name + ". "
            "These are some job description examples:\n" + retrieveKMostSimilar(job_name) +
            "Be concise and precise. This should be read by a worker looking for a job, "
            "so you have to be clear. Avoid answering with a bullet point list, and be discoursive. "
            "Use no more than 20 lines."
    )

    job_description = performRequest(prompt)

    print("starting description of job")
    print(job_description)
    print("ending description of job")

    '''
    job_description = """
    We are looking for a student with experience in Python, C/C++, and Java. 
    The candidate should have a good knowledge on programming language and working with databases. 
    Experience with English and a guide license is a plus.
    """
    '''


    job_embedding = model.encode([job_description])
    cv_embedding = model.encode([CV_description])

    # print(job_embedding)
    # print(cv_embedding)

    similarity = cosine_similarity(job_embedding, cv_embedding)

    print("Cosine Similarity:", similarity[0][0])


if __name__ == '__main__':

    file_path = '../misc_files/cv_main_english(5).pdf'  # or 'cv.docx'

    job_code = "29-1129.01"

    job_name = "Art Therapist"

    main(file_path,"pdf",job_code,job_name)

    #print(extract_text_from_pdf(file_path))
