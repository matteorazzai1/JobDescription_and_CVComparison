from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import PyPDF2
from docx import Document
import os
from groq import Groq

from AppLogic.sectionsSummary import summarizeSection
from Utils.dbManager import retrieveKMostSimilar
from Utils.scraper import performRequest


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
            "Be clear and precise. This should be read by a worker looking for a job, "
            "so you have to be clear. Avoid answering with a bullet point list, and be discoursive. "
            "Use no more than 20 lines."
    )
    print(prompt)
    job_description = performRequest(prompt)
    return job_description, work_activities, skills, tasks


def compareCVJobDescription(file_path, file_type, job_description):
    if file_type == 'pdf':
        file_content = extract_text_from_pdf(file_path)
    elif file_type == 'docx':
        file_content = extract_text_from_docx(file_path)
    else:
        raise ValueError("Unsupported file type. Use 'pdf' or 'docx'.")

    CV_description = performRequest(f"Can you take this content related to the text extracted from a curriculum "
                                    f"vitae and resume it trying to focus on the working skills, working experiences and background in a detailed "
                                    f"manner and avoiding section that do not regard those sections? please avoid answering with a bullet point list, be precise, clear "
                                    f"and discoursive. Put only the Curriculum resume in the answer. The text to resume is the following: {file_content}")
    #print(CV_description)

    # derive embeddings and compute cosine similarity
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

    print("starting description of job")
    print(job_description)
    print("ending description of job")

    print(CV_description)

    job_embedding = model.encode([job_description])
    cv_embedding = model.encode([CV_description])

    similarity = cosine_similarity(job_embedding, cv_embedding)

    print("Cosine Similarity:", similarity[0][0])
    return similarity[0][0]


