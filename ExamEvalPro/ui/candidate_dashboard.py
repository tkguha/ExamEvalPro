import customtkinter as ctk

from ui.response_entry_screen import ResponseEntryScreen
from database.db_manager import get_status_counts
from ui.result_screen import ResultScreen


class CandidateDashboard(ctk.CTkToplevel):

    def __init__(self, master, mapping=None, answer_key_map=None):
        super().__init__(master)

        self.mapping = mapping
        self.answer_key_map = answer_key_map

        self.master_df = master.master_df
        self.exam_id = getattr(master, "exam_id", None)
        self.exam_profile = getattr(master, "exam_profile", {})

        self.candidate_count = len(self.master_df)

        self.title("Candidate Dashboard")
        self.geometry("520x700+630+20")

        self.transient(master)
        self.lift()
        self.focus_force()

        counts = get_status_counts(self.exam_id)

        completed = counts["Appeared"]
        not_appeared = counts["Not Appeared"]
        cancelled = counts["Cancelled"]

        pending = self.candidate_count - completed - not_appeared - cancelled

        profile = self.exam_profile

        ctk.CTkLabel(
            self,
            text=profile.get("exam_name", "EXAM"),
            font=("Arial", 20, "bold")
        ).pack(pady=10)

        ctk.CTkLabel(
            self,
            text=f"{profile.get('exam_date','')} | {profile.get('venue','')}"
        ).pack()

        ctk.CTkLabel(
            self,
            text=f"Duration: {profile.get('duration_minutes','')} mins"
        ).pack(pady=5)

        ctk.CTkLabel(self, text="Exam Summary", font=("Arial", 18, "bold")).pack(pady=8)

        ctk.CTkLabel(self, text=f"Questions: {len(self.answer_key_map)}").pack()
        ctk.CTkLabel(self, text=f"Candidates: {self.candidate_count}").pack()

        ctk.CTkLabel(self, text="Response Progress", font=("Arial", 18, "bold")).pack(pady=8)

        ctk.CTkLabel(self, text=f"Completed: {completed}").pack()
        ctk.CTkLabel(self, text=f"Pending: {pending}").pack()
        ctk.CTkLabel(self, text=f"Not Appeared: {not_appeared}").pack()
        ctk.CTkLabel(self, text=f"Cancelled: {cancelled}").pack(pady=20)

        ctk.CTkButton(self, text="Start Response Entry",
                      command=self.response_entry).pack(pady=10)

        ctk.CTkButton(self, text="Generate Final Results",
                      command=self.generate_results).pack(pady=5)

    def response_entry(self):
        self.withdraw()
        ResponseEntryScreen(self)

    def generate_results(self):
        ResultScreen(self)