from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import PyPDF2
from docx import Document
import os
from groq import Groq

from AppLogic.sectionsSummary import summarizeSection


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


def main(file_path, file_type='pdf'):
    if file_type == 'pdf':
        file_content = extract_text_from_pdf(file_path)
    elif file_type == 'docx':
        file_content = extract_text_from_docx(file_path)
    else:
        raise ValueError("Unsupported file type. Use 'pdf' or 'docx'.")

    CV_description = performRequest(f"Can you try to take this content related to the text extracted from a curriculum vitae and describe it trying to concentrate on the working skills in a detailed manner and avoiding section that not regards working skills? please avoid pointed list and try to summarize{file_content}")
    print(CV_description)

    # derive embeddings and compute cosine similarity
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

    work_activities = summarizeSection("work activities", "29-1129.01", "Art Therapist", True)
    skills = summarizeSection("skills", "29-1129.01", "Art Therapist", True)
    tasks = summarizeSection("tasks", "29-1129.01", "Art Therapist", True)

    prompt = ""
    prompt = "Can you take the following work activities with a value of importance, the name of the activities " \
                "and a brief description " + work_activities + " the skills with the same component: " + skills + " and the tasks" + tasks + " and make me a detailed" \
                " description" \
                                                                                                             ""


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

    file_path = '../misc_files/CV_-_Matteo_Razzai.pdf'  # or 'cv.docx'

    main(file_path)
