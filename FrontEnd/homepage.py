import threading
import tkinter as tk
from tkinter import ttk, filedialog
import pandas as pd


from AppLogic.parsingCV import compareCVJobDescription, jobDescriptionGeneration, extract_text_from_pdf

from AppLogic.sectionsSummary import summarizeSection, buildPromptSummarization
from Utils.scraper import performRequest


class JobDescriptionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Job Description and CV Matching")
        self.root.state('zoomed')


        self.style = ttk.Style()
        self.setup_styles()

        self.create_home_page()

        self.current_jobDescription = ""

    def create_scrollable_frame(self):
        container = ttk.Frame(self.root)
        container.grid(row=0, column=0, sticky="nsew")

        canvas = tk.Canvas(container)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

    def setup_styles(self):
        soft_blue = "#8FAADC"
        dark_blue = "#1C3F94"
        white = "#FFFFFF"
        black = "#000000"

        self.style.configure('TFrame', background=soft_blue)
        self.style.configure('TLabel', background=soft_blue, foreground=white, font=('Helvetica', 14))
        self.style.configure('TButton', background=dark_blue, foreground=black, font=('Helvetica', 12), padding=10, relief="flat")
        self.style.map('TButton', background=[('active', dark_blue)], foreground=[('active', white)])

        self.root.configure(background=soft_blue)

    def create_home_page(self):
        self.clear_frame()

        job_categories = ["Industrial Machinery and Equipment Operators", "Service and Maintenance", "Administration and Support",
                          "Science and Research", "Manual Operators and Technicians", "Health and Wellness",
                          "Communication, Entertainment, and Creative Professions", "Engineering and Technology",
                          "Management and Supervision", "Education and Teaching"]


        job_cat = [f"{job_categories[i]}" for i in range(10)]

        frame = ttk.Frame(self.root, padding="20")
        frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))

        title_label = ttk.Label(frame, text="Job Categories", font=("Helvetica", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(20, 10))

        for i, job_desc in enumerate(job_cat):
            column = i % 2
            row = i // 2
            button = ttk.Button(frame, text=job_desc, command=lambda jd=job_desc: self.open_jobs_list(jd))
            button.grid(row=row+1, column=column, padx=10, pady=10, sticky=(tk.W, tk.E))

        for i in range(2):
            frame.columnconfigure(i, weight=1, uniform='column')
        for i in range((len(job_cat) + 1) // 2):
            print(i)
            frame.rowconfigure(i+1, weight=1, uniform='row')

        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

    def open_jobs_list(self, job_category):
        self.clear_frame()
        self.create_scrollable_frame()


        csvreader = pd.read_csv("../misc_files/jobList.csv")
        data = csvreader[["Code", "Occupation", "Category"]]


        data = pd.DataFrame(data)
        data["Code"] = data["Code"].astype(str)
        data["Occupation"] = data["Occupation"].astype(str)
        data["Category"] = data["Category"].astype(str)


        jobs = data[data["Category"] == job_category]

        max_width = self.root.winfo_width() - 40  # Adjust width as needed
        wraplength = max_width

        label = ttk.Label(self.scrollable_frame, text=f"Matching jobs for {job_category}", font=("Helvetica", 18, 'bold'), wraplength=wraplength,width=116,anchor="center")
        label.grid(pady=10, columnspan=2, sticky=(tk.N), row=0)

        back_button = ttk.Button(self.scrollable_frame, text="Back", width=25, command=self.create_home_page)
        back_button.grid(pady=10, sticky=(tk.W, tk.N), row=0)

        search_var = tk.StringVar()
        search_entry = ttk.Entry(self.scrollable_frame, textvariable=search_var, width=30)
        search_entry.grid(row=1, pady=10, sticky=(tk.N))

        search_button = ttk.Button(self.scrollable_frame, text="Search", command=lambda: self.update_job_buttons(search_var.get(), jobs))
        search_button.grid(row=2, pady=5, sticky=(tk.N))

        # Create a progress bar
        self.progress_bar = ttk.Progressbar(self.scrollable_frame, orient="horizontal", length=600, mode="determinate")
        self.progress_bar.grid(row=3, pady=20, sticky=(tk.N))


        self.job_buttons_frame = ttk.Frame(self.scrollable_frame)
        self.job_buttons_frame.grid(row=4, column=0, columnspan=4, sticky=(tk.W, tk.E))
        self.job_buttons_frame.grid_columnconfigure(0, weight=1)

        self.display_jobs(jobs)


        self.scrollable_frame.grid_rowconfigure(len(jobs) + 1, weight=1)
        self.scrollable_frame.grid_columnconfigure(0, weight=1)

    def display_jobs(self, jobs):
        for widget in self.job_buttons_frame.winfo_children():
            widget.destroy()

        for i, job in jobs.iterrows():
            button = ttk.Button(self.job_buttons_frame, text=job['Occupation'],
                                command=lambda j=job: self.start_open_job_page(j))
            button.grid(row=i, column=0, pady=5, sticky=(tk.W, tk.E))



    def start_open_job_page(self, job):
        # Run the long-running task in a separate thread to avoid blocking the GUI
        threading.Thread(target=self.open_job_page, args=(job,)).start()

    def start_open_CV(self,path):
        threading.Thread(target=self.handle_file, args=(path,)).start()

    def update_progress_bar(self, value):
        self.progress_bar['value'] = value
        self.root.update_idletasks()

    def update_job_buttons(self, search_query, jobs):
        filtered_jobs = jobs[jobs['Occupation'].str.contains(search_query, case=False, na=False)]
        self.display_jobs(filtered_jobs)

    def clear_frame(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def open_job_page(self, j):
        self.update_progress_bar(10)


        # Summarize the sections
        overall_description, workAct, skillsRetrieved, taskRetrieved = jobDescriptionGeneration(j["Code"], j["Occupation"])
        self.update_progress_bar(25)
        work_activities = performRequest(buildPromptSummarization(workAct, "work activities", j["Occupation"], False, True))
        self.update_progress_bar(50)
        skills = performRequest(buildPromptSummarization(skillsRetrieved, "skills", j["Occupation"],  False, True))
        self.update_progress_bar(75)
        tasks = performRequest(buildPromptSummarization(taskRetrieved, "tasks", j["Occupation"], False, True))
        self.update_progress_bar(100)


        self.clear_frame()
        self.create_scrollable_frame()

        self.current_jobDescription = overall_description

        notebook = ttk.Notebook(self.scrollable_frame)
        notebook.grid(row=0, column=0, padx=10, pady=10, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Create frames for each tab
        overall_description_frame = ttk.Frame(notebook)
        work_activities_frame = ttk.Frame(notebook)
        skills_frame = ttk.Frame(notebook)
        tasks_frame = ttk.Frame(notebook)

        # Add frames to notebook as tabs
        notebook.add(overall_description_frame, text="Overall Description")
        notebook.add(work_activities_frame, text="Work Activities")
        notebook.add(skills_frame, text="Skills")
        notebook.add(tasks_frame, text="Tasks")

        # Set wraplength to ensure text wraps within the window
        max_width = self.root.winfo_width() - 40  # Adjust width as needed
        wraplength = max_width

        # Populate the frames with content
        ttk.Label(overall_description_frame, text=overall_description, wraplength=wraplength).grid(row=0, column=0, padx=10, pady=10, sticky=(tk.W, tk.E, tk.N, tk.S))
        ttk.Label(work_activities_frame, text=work_activities, wraplength=wraplength).grid(row=0, column=0, padx=10, pady=10, sticky=(tk.W, tk.E, tk.N, tk.S))
        ttk.Label(skills_frame, text=skills, wraplength=wraplength).grid(row=0, column=0, padx=10, pady=10, sticky=(tk.W, tk.E, tk.N, tk.S))
        ttk.Label(tasks_frame, text=tasks, wraplength=wraplength).grid(row=0, column=0, padx=10, pady=10, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Add a back button
        back_button = ttk.Button(self.scrollable_frame, text="Back", command=lambda cat=j["Category"]: self.open_jobs_list(cat))
        back_button.grid(row=2, column=0, pady=20, sticky=(tk.W, tk.E))

        # Create a progress bar
        self.progress_bar = ttk.Progressbar(self.scrollable_frame, orient="horizontal", length=600, mode="determinate")
        self.progress_bar.grid(row=1, pady=20, sticky=(tk.N))

        upload_button = ttk.Button(self.scrollable_frame, text="Upload CV", command=self.upload_file)
        upload_button.grid(row=3, column=0, pady=10, sticky=(tk.W, tk.E))

        self.scrollable_frame.grid_rowconfigure(1, weight=1)
        self.scrollable_frame.grid_columnconfigure(0, weight=1)

        # Configure notebook resizing
        notebook.grid_rowconfigure(0, weight=1)
        notebook.grid_columnconfigure(0, weight=1)

        # Configure each tab frame resizing
        overall_description_frame.grid_rowconfigure(0, weight=1)
        overall_description_frame.grid_columnconfigure(0, weight=1)
        work_activities_frame.grid_rowconfigure(0, weight=1)
        work_activities_frame.grid_columnconfigure(0, weight=1)
        skills_frame.grid_rowconfigure(0, weight=1)
        skills_frame.grid_columnconfigure(0, weight=1)
        tasks_frame.grid_rowconfigure(0, weight=1)
        tasks_frame.grid_columnconfigure(0, weight=1)

    def upload_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.update_progress_bar(10)
            self.start_open_CV(file_path)
            #self.handle_file(file_path)

    def handle_file(self, file_path):
        similarity = compareCVJobDescription(file_path, "pdf", self.current_jobDescription)
        self.update_progress_bar(75)
        output = f"The similarity between your CV and the job offer is: " + "{:.2f}".format(similarity)
        if similarity >= 0.3:
            output += "\nWe suggest you to apply for this job, you're' a good candidate, in line with the job offer"
        elif 0.25 <= similarity < 0.3:
            output += "\nYou could apply for this job, you probably are a good candidate"
        elif 0.2 <= similarity < 0.25:
            output += "\nYou could apply for this job but you're not quite in line with the offer requests"
        elif similarity < 0.2:
            output += "\nWe suggest you to not apply for this job, this is quite different from your background, experience and skills"
        self.update_progress_bar(100)
        self.show_popup(output)

    def show_popup(self, text):
        popup = tk.Toplevel(self.root)
        popup.title("File Content")

        # Set the size of the popup window explicitly
        popup.geometry("400x300")

        # Create a frame to hold the label and button
        frame = ttk.Frame(popup)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        label = ttk.Label(frame, text=text, wraplength=350)
        label.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        ok_button = ttk.Button(frame, text="OK", command=popup.destroy)
        ok_button.pack(pady=10)




if __name__ == "__main__":
    root = tk.Tk()
    app = JobDescriptionApp(root)
    root.mainloop()
