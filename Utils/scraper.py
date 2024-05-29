import requests
import os

from groq import Groq


def scrape_csv(base_url, filename, toReturn):
    directory = "misc_files"
    filepath = os.path.join(directory, filename)

    # Ensure the directory exists
    os.makedirs(directory, exist_ok=True)

    try:
        # Fetch the data from the URL
        response = requests.get(base_url)

        # Check if the request was successful
        if response.status_code == 200:
            # Save the content to a file
            if toReturn:
                return response.content
            else:
                with open(filepath, 'wb') as handler:
                    handler.write(response.content)
                print(f"File saved successfully to {filepath}")
        else:
            print(f"Failed to retrieve the file. Status code: {response.status_code}")
    except requests.RequestException as e:
        print(f"An error occurred: {e}")

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

