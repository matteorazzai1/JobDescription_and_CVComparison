import tkinter as tk
from tkinter import ttk

class JobDescriptionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Job Description and CV Matching")

        self.style = ttk.Style()
        self.setup_styles()

        self.create_home_page()

    def setup_styles(self):
        soft_blue = "#8FAADC"
        dark_blue = "#1C3F94"
        white = "#FFFFFF"

        self.style.configure('TFrame', background=soft_blue)
        self.style.configure('TLabel', background=soft_blue, foreground=white, font=('Helvetica', 14))
        self.style.configure('TButton', background=dark_blue, foreground=white, font=('Helvetica', 12), padding=10, relief="flat")
        self.style.map('TButton', background=[('active', dark_blue)], foreground=[('active', white)])

        self.root.configure(background=soft_blue)

    def create_home_page(self):
        self.clear_frame()

        job_descriptions = [f"Job Description {i+1}" for i in range(10)]

        frame = ttk.Frame(self.root, padding="20")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        for i, job_desc in enumerate(job_descriptions):
            column = i % 2
            row = i // 2
            button = ttk.Button(frame, text=job_desc, command=lambda jd=job_desc: self.open_cv_page(jd))
            button.grid(row=row, column=column, padx=10, pady=10, sticky=(tk.W, tk.E))

        for i in range(2):
            frame.columnconfigure(i, weight=1)
        for i in range((len(job_descriptions) + 1) // 2):
            frame.rowconfigure(i, weight=1)

        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

    def open_cv_page(self, job_description):
        self.clear_frame()

        cvs = [f"CV {i+1} for {job_description}" for i in range(5)]

        label = ttk.Label(self.root, text=f"Matching CVs for {job_description}", font=("Helvetica", 18, 'bold'))
        label.pack(pady=10)

        for cv in cvs:
            cv_label = ttk.Label(self.root, text=cv)
            cv_label.pack(pady=5)

        back_button = ttk.Button(self.root, text="Back", command=self.create_home_page)
        back_button.pack(pady=20)

    def clear_frame(self):
        for widget in self.root.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = JobDescriptionApp(root)
    root.mainloop()
