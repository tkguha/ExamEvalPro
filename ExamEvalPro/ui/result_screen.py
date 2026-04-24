import customtkinter as ctk
import pandas as pd

from tkinter import messagebox, filedialog

from database.db_manager import (
    get_candidate_status,
    get_candidate_score,
    get_candidate_responses
)


class ResultScreen(ctk.CTkToplevel):

    def __init__(self, master):

        super().__init__(master)

        self.title("Final Results")
        self.geometry("800x700+50+50")

        self.master_df = master.master_df
        self.exam_id = master.exam_id
        self.mapping = master.mapping
        self.answer_key_map = master.answer_key_map
        self.exam_profile = getattr(master, "exam_profile", {})

        self.transient(master)
        self.lift()
        self.focus_force()

        ctk.CTkLabel(
            self,
            text="FINAL RESULTS",
            font=("Arial", 28, "bold")
        ).pack(pady=20)

        # -------- EXAM HEADER --------
        profile = self.exam_profile

        header_text = (
            f"{profile.get('exam_name','')}\n"
            f"{profile.get('exam_date','')} | {profile.get('venue','')}\n"
            f"Duration: {profile.get('duration_minutes','')} mins | "
            f"{profile.get('conducting_authority','')}"
        )

        ctk.CTkLabel(self, text=header_text).pack(pady=10)

        self.textbox = ctk.CTkTextbox(self, width=900, height=450)
        self.textbox.pack(pady=20)

        self.textbox.insert("1.0", self.build_report())

        ctk.CTkButton(
            self,
            text="Export Results",
            command=self.export_results
        ).pack(pady=15)

    # ---------------- REPORT ----------------

    def build_report(self):

        report = ""

        question_keys = sorted(self.answer_key_map.keys(), key=int)

        report += "SLNO  NAME                 SCORE    RESULT\n"
        report += "---------------------------------------------\n"

        for _, row in self.master_df.iterrows():

            slno = str(row["SLNO"])
            name = str(row["NAME"])

            status = get_candidate_status(self.exam_id, slno)
            score_data = get_candidate_score(self.exam_id, slno)

            score = round(score_data[4], 2) if score_data else 0

            if status == "Not Appeared":
                result = "Absent"
            elif status == "Cancelled":
                result = "Cancelled"
            elif score >= 0:
                result = "Eligible"
            else:
                result = "Not Eligible"

            report += f"{slno:<6}{name[:20]:<21}{score:<10}{result}\n"

        return report

    # ---------------- EXPORT ----------------

    def export_results(self):

        rows = []
        question_keys = sorted(self.answer_key_map.keys(), key=int)

        profile = self.exam_profile

        for _, row in self.master_df.iterrows():

            slno = str(row.get("SLNO", ""))
            name = str(row.get("NAME", ""))

            status = get_candidate_status(self.exam_id, slno)
            score_data = get_candidate_score(self.exam_id, slno)

            if score_data:
                correct, wrong, blank, multiple, score = score_data
            else:
                correct = wrong = blank = multiple = score = 0

            responses = get_candidate_responses(self.exam_id, slno) or ["BLANK"] * len(question_keys)

            result = "Eligible" if score >= 0 else "Not Eligible"

            row_data = {
                "SLNO": slno,
                "NAME": name,
                "STATUS": status,
                "SCORE": round(score, 2),
                "RESULT": result
            }

            for i, q_str in enumerate(question_keys):
                row_data[f"Q{q_str}"] = responses[i]

            rows.append(row_data)

        df = pd.DataFrame(rows)

        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx")

        if file_path:

            with pd.ExcelWriter(file_path) as writer:

                header_df = pd.DataFrame([
                    ["Exam Name", profile.get("exam_name", "")],
                    ["Date", profile.get("exam_date", "")],
                    ["Venue", profile.get("venue", "")],
                    ["Duration", profile.get("duration_minutes", "")],
                    ["Authority", profile.get("conducting_authority", "")]
                ])

                header_df.to_excel(writer, index=False, header=False)
                df.to_excel(writer, startrow=7, index=False)

            messagebox.showinfo("Export", "Results exported successfully.")