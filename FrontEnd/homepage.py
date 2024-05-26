import tkinter as tk
from tkinter import ttk
import pandas as pd

class JobDescriptionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Job Description and CV Matching")


        self.style = ttk.Style()
        self.setup_styles()

        self.create_home_page()

    def create_scrollable_frame(self):

        self.canvas = tk.Canvas(self.root)
        self.scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky="ns")


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

        job_categories=["Industrial Machinery and Equipment Operators", "Service and Maintenance","Administration and Support",
                        "Science and Research" , "Manual Operators and Technicians","Manual Operators and Technicians",
                        "Health and Wellness", "Communication, Entertainment, and Creative Professions",
                        "Engineering and Technology" , "Management and Supervision","Education and Teaching"]

        job_cat = [f"{job_categories[i]}" for i in range(10)]

        frame = ttk.Frame(self.root, padding="20")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        for i, job_desc in enumerate(job_cat):
            column = i % 2
            row = i // 2
            button = ttk.Button(frame, text=job_desc, command=lambda jd=job_desc: self.open_jobs_list(jd))
            button.grid(row=row, column=column, padx=10, pady=10, sticky=(tk.W, tk.E))

        for i in range(2):
            frame.columnconfigure(i, weight=1)
        for i in range((len(job_cat) + 1) // 2):
            frame.rowconfigure(i, weight=1)

        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

    def open_jobs_list(self, job_category):
        self.clear_frame()
        self.create_scrollable_frame()

        csvreader = pd.read_csv("..\misc_files\jobList.csv")
        data = csvreader[["Code", "Occupation","Category"]]

        data = pd.DataFrame(data)
        data["Code"] = data["Code"].astype(str)
        data["Occupation"] = data["Occupation"].astype(str)
        data["Category"] = data["Category"].astype(str)

        filtered_data = data[data["Category"] == job_category]

        jobs = [f"{i}){row['Occupation']}" for i, row in filtered_data.iterrows()]

        label = ttk.Label(self.scrollable_frame, text=f"Matching CVs for {job_category}", font=("Helvetica", 18, 'bold'))
        label.grid(pady=10)

        for i, job in enumerate(jobs, start=1):
            button = ttk.Button(self.scrollable_frame, text=job, command=lambda j=job: self.open_job_page(j))
            button.grid(row=i, column=0, pady=5, sticky=(tk.W, tk.E))

        back_button = ttk.Button(self.scrollable_frame, text="Back", command=self.create_home_page)
        back_button.grid(pady=20)

    def clear_frame(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def open_job_page(self, j):
        pass


if __name__ == "__main__":
    root = tk.Tk()
    app = JobDescriptionApp(root)
    root.mainloop()
