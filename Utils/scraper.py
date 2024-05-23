import requests
import os



def scrape_csv(base_url, filename):
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
            with open(filepath, 'wb') as handler:
                handler.write(response.content)
            print(f"File saved successfully to {filepath}")
        else:
            print(f"Failed to retrieve the file. Status code: {response.status_code}")
    except requests.RequestException as e:
        print(f"An error occurred: {e}")