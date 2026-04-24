import customtkinter as ctk
from tkinter import messagebox

from database.db_manager import (
    get_examinations,
    load_exam_config,
    get_conn
)

from ui.candidate_dashboard import CandidateDashboard
import pandas as pd


class OpenExamScreen(ctk.CTkToplevel):

    def __init__(self, master):

        super().__init__(master)

        self.title("Open Existing Examination")
        self.geometry("500x450+630+20")

        # Modal behavior
        self.transient(master)
        self.grab_set()
        self.focus_force()
        self.lift()

        ctk.CTkLabel(
            self,
            text="Select Existing Examination",
            font=("Arial", 20, "bold")
        ).pack(pady=15)

        # -------- LOAD EXAMS --------
        exams = get_examinations()

        self.exam_map = {}
        options = []

        for row in exams:
            exam_id = row[0]
            label = f"{row[1]} ({row[2]})"
            options.append(label)
            self.exam_map[label] = exam_id

        if not options:
            options = ["No saved examinations"]

        self.exam_menu = ctk.CTkOptionMenu(self, values=options)
        self.exam_menu.pack(pady=20)

        ctk.CTkButton(
            self,
            text="Resume Examination",
            command=self.resume_exam
        ).pack(pady=20)

    # ---------------- RESUME ----------------

    def resume_exam(self):

        selected = self.exam_menu.get()

        if selected == "No saved examinations":
            messagebox.showerror("Error", "No exams found")
            return

        exam_id = self.exam_map[selected]

        # -------- LOAD CONFIG --------
        mapping, answer_key = load_exam_config(exam_id)

        if not mapping or not answer_key:
            messagebox.showerror("Error", "Config missing. Please import once.")
            return

        # -------- LOAD PROFILE --------
        conn = get_conn()
        profile_df = pd.read_sql_query(
            "SELECT * FROM examination_profile WHERE exam_id=?",
            conn,
            params=(exam_id,)
        )
        conn.close()

        if profile_df.empty:
            messagebox.showerror("Error", "Exam profile not found.")
            return

        profile = profile_df.iloc[0].to_dict()

        # -------- LOAD MASTER DATA (CRITICAL FIX) --------
        conn = get_conn()
        messagebox.showinfo(
            "Re-upload Required",
            "Please re-upload master sheet for this exam."
        )
        return
        conn.close()

        # -------- PASS DATA --------
        self.master.master_df = df
        self.master.exam_id = exam_id
        self.master.exam_profile = profile

        self.destroy()

        CandidateDashboard(
            self.master,
            mapping=mapping,
            answer_key_map=answer_key
        )