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


def jobDescriptionGeneration(job_code, job_name):
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    work_activities = summarizeSection("work activities", job_code, job_name, True, False)
    skills = summarizeSection("skills", job_code, job_name, True, False)
    tasks = summarizeSection("tasks", job_code, job_name, True, False)

    prompt = (
            "Can you summarize a description for the job described with the following lists of work activities,"
            "skills and tasks? Each number before them is the importance of the activity, task or skill for the job\nWork activities:\n "
            + work_activities + "\nSkills:\n" + skills + "\nTasks:\n" + tasks +
            "This is about an open position for a " + job_name + ". "
            "These are some job description examples:\n" + retrieveKMostSimilar(model.encode(job_name)) +
            "Be concise and precise. This should be read by a worker looking for a job, "
            "so you have to be clear. Avoid answering with a bullet point list, and be discoursive. "
            "Use no more than 20 lines."
    )
    print(prompt)
    job_description = performRequest(prompt)
    return job_description, work_activities, skills, tasks


def compareCVJobDescription(file_path, file_type, job_code, job_name, job_description):
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

    print("starting description of job")
    print(job_description)
    print("ending description of job")

    job_embedding = model.encode([job_description])
    cv_embedding = model.encode([CV_description])

    similarity = cosine_similarity(job_embedding, cv_embedding)

    print("Cosine Similarity:", similarity[0][0])


if __name__ == '__main__':

    file_path = '../misc_files/cv_main_english(5).pdf'  # or 'cv.docx'

    job_code = "29-1129.01"

    job_name = "Art Therapist"

    compareCVJobDescription(file_path, "pdf", job_code, job_name)

    #print(extract_text_from_pdf(file_path))
