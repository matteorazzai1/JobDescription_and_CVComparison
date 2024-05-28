from io import BytesIO

import pandas as pd

from Utils.scraper import scrape_csv

def buildPromptSummarization(dataframe, section, actualJob, returnSection, isString):
    if isString == False:
        dataframe = pd.DataFrame(dataframe).reset_index(drop=True).astype(str)
        prompt = ""
        iterator = dataframe.iterrows()
        for i in range (0, len(dataframe)):
            val = next(iterator)[1]
            if (section == "skills"):
                prompt = prompt + val['Importance'] + " - " + val['Skill'] + " - " + val['Skill Description'] + "\n"
            elif (section == "tasks"):
                prompt = prompt + val["Importance"] + " - " + val["Task"] + "\n"
            elif (section == "work activities"):
                prompt = prompt + val["Importance"] + " - " + val["Work Activity"] + " - " + val["Work Activity Description"] + "\n"
    else:
        prompt = dataframe

    if (returnSection):
        return prompt

    prompt = prompt + "Can you summarize the " + section + " required for this job? This is about an open position for a " + actualJob  + ".\n" \
             + "The number before each " + section + " is the importance of the"

    if (section == "skills"):
        prompt = prompt + " skill for this position. The textual description is divided into Skill name and skill description. Those sections are divided by \"-\" symbol.\n"
    elif (section == "tasks"):
        prompt = prompt + "task for this position.\n"
    elif (section == "workactivities"):
        prompt = prompt + "work activity for this position. The textual description is divided into work activity name and work activity description. Those sections are divided by \"-\" symbol.\n"

    prompt = prompt + "Be clear and precise. This should be read by a worker looking for a job, so you have to be clear.\n" \
                      "Avoid answering with a bullet point list, and be discoursive. Use no more than 15 lines."

    return prompt




def summarizeSection(section, jobCode, jobName, returnSection, isString):
    url = "https://www.onetonline.org/link/table/details/"
    if (section == "skills"):
        url = url + "sk/" + jobCode + "/Skills"
    elif (section == "tasks"):
        url = url + "tk/" + jobCode + "/Tasks"
    elif (section == "work activities"):
        url = url + "wa/" + jobCode + "/Work_activities"

    jobCode = jobCode.replace(".", "-")
    url = url + "_" + jobCode + ".csv?fmt=csv&s=IM&t=-10"
    data = pd.read_csv(BytesIO(scrape_csv(url, jobCode, toReturn=True))).head(10)
    return buildPromptSummarization(data, section, jobName, returnSection, isString)



