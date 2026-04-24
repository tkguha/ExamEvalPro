import pandas as pd
import customtkinter as ctk
from tkinter import filedialog, messagebox

from ui.candidate_dashboard import CandidateDashboard
from database.db_manager import save_exam_config


class ImportScreen(ctk.CTkToplevel):

    def __init__(self, master):
        super().__init__(master)

        self.exam_id = getattr(master, "exam_id", None)

        self.title("Import Examination Files")
        self.geometry("520x350+630+20")

        self.transient(master)
        self.grab_set()

        self.master_df = None
        self.answer_key_map = None

        self.master_loaded = False
        self.answer_loaded = False

        ctk.CTkLabel(
            self,
            text="Import Examination Files",
            font=("Arial", 20, "bold")
        ).pack(pady=20)

        self.master_btn = ctk.CTkButton(
            self,
            text="Upload Master Sheet",
            command=self.upload_master
        )
        self.master_btn.pack(pady=10)

        self.answer_btn = ctk.CTkButton(
            self,
            text="Upload Answer Key",
            command=self.upload_answer
        )
        self.answer_btn.pack(pady=10)

        self.continue_btn = ctk.CTkButton(
            self,
            text="Continue to Candidate Dashboard",
            command=self.continue_next,
            state="disabled"
        )
        self.continue_btn.pack(pady=30)

    # ---------------- MASTER ----------------
    def upload_master(self):

        file_path = filedialog.askopenfilename(
            filetypes=[("Excel files", "*.xlsx")]
        )

        if not file_path:
            return

        try:
            df = pd.read_excel(file_path)

            # 🔥 NORMALIZE HEADERS
            df.columns = [c.strip().upper() for c in df.columns]

            required = ["SLNO", "APPLICATION_NO", "NAME", "CATEGORY"]

            if not all(col in df.columns for col in required):
                messagebox.showerror(
                    "Invalid Format",
                    f"Master sheet must contain:\n{required}"
                )
                return

            self.master_df = df
            self.master_loaded = True
            self.master_btn.configure(text="Master Sheet Loaded ✔")

            self.check_ready()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ---------------- ANSWER KEY ----------------
    def upload_answer(self):

        file_path = filedialog.askopenfilename(
            filetypes=[("Excel files", "*.xlsx")]
        )

        if not file_path:
            return

        try:
            df = pd.read_excel(file_path)

            df.columns = [c.strip().upper() for c in df.columns]

            required = ["QUESTION_NO", "ANSWER_KEY"]

            if not all(col in df.columns for col in required):
                messagebox.showerror(
                    "Invalid Format",
                    f"Answer key must contain:\n{required}"
                )
                return

            clean_map = {}

            for q, ans in zip(df["QUESTION_NO"], df["ANSWER_KEY"]):
                clean_map[str(int(q))] = str(ans).strip().upper()

            self.answer_key_map = dict(
                sorted(clean_map.items(), key=lambda x: int(x[0]))
            )

            self.answer_loaded = True
            self.answer_btn.configure(text="Answer Key Loaded ✔")

            self.check_ready()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ---------------- READY ----------------
    def check_ready(self):
        if self.master_loaded and self.answer_loaded:
            self.continue_btn.configure(state="normal")

    # ---------------- CONTINUE ----------------
    def continue_next(self):

        save_exam_config(
            self.exam_id,
            {},  # mapping removed
            self.answer_key_map
        )

        self.master.master_df = self.master_df
        self.master.answer_key_map = self.answer_key_map

        self.destroy()

        CandidateDashboard(
            self.master,
            mapping=None,
            answer_key_map=self.answer_key_map
        )