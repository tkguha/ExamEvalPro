import customtkinter as ctk
from tkinter import messagebox

from database.db_manager import (
    save_candidate_status,
    get_candidate_status,
    save_candidate_score,
    save_candidate_responses,
    get_candidate_responses
)


class ResponseEntryScreen(ctk.CTkToplevel):

    def __init__(self, master):
        super().__init__(master)

        self.title("Candidate Response Entry")
        self.geometry("850x800+600+20")

        self.transient(master)
        self.lift()

        self.total_candidates = master.candidate_count
        self.current_candidate = 0
        self.current_status = "Appeared"

        self.question_keys = sorted(
            master.answer_key_map.keys(),
            key=int
        )

        # -------- HEADER --------
        ctk.CTkLabel(
            self,
            text="CANDIDATE RESPONSE ENTRY",
            font=("Arial", 24, "bold")
        ).pack(pady=10)

        # -------- INFO --------
        self.info_label = ctk.CTkLabel(self, text="")
        self.info_label.pack(pady=5)

        # -------- STATUS --------
        status_frame = ctk.CTkFrame(self, fg_color="transparent")
        status_frame.pack(pady=10)

        self.appeared_btn = ctk.CTkButton(
            status_frame, text="Appeared",
            command=lambda: self.set_status("Appeared")
        )
        self.appeared_btn.pack(side="left", padx=10)

        self.na_btn = ctk.CTkButton(
            status_frame, text="Not Appeared",
            command=lambda: self.set_status("Not Appeared")
        )
        self.na_btn.pack(side="left", padx=10)

        self.cancel_btn = ctk.CTkButton(
            status_frame, text="Cancelled",
            command=lambda: self.set_status("Cancelled")
        )
        self.cancel_btn.pack(side="left", padx=10)

        # -------- QUESTIONS --------
        self.scroll = ctk.CTkScrollableFrame(self, width=700, height=400)
        self.scroll.pack(pady=10)

        self.vars = []
        self.widgets = []

        for q in self.question_keys:
            row = ctk.CTkFrame(self.scroll)
            row.pack(fill="x", pady=2)

            ctk.CTkLabel(row, text=f"Q{q}", width=50).pack(side="left")

            var = ctk.StringVar(value="BLANK")

            dd = ctk.CTkOptionMenu(
                row,
                values=["A", "B", "C", "D", "BLANK", "MULTIPLE"],
                variable=var
            )
            dd.pack(side="left")

            self.vars.append(var)
            self.widgets.append(dd)

        # -------- BUTTON --------
        ctk.CTkButton(
            self,
            text="Next Candidate",
            command=self.next_candidate
        ).pack(pady=20)

        self.load_candidate()

    # --------------------------
    def set_status(self, status):
        self.current_status = status

        if status in ["Not Appeared", "Cancelled"]:
            for w in self.widgets:
                w.configure(state="disabled")
        else:
            for w in self.widgets:
                w.configure(state="normal")

    # --------------------------
    def load_candidate(self):
        df = self.master.master_df
        row = df.iloc[self.current_candidate]
    
        slno = str(row["SLNO"])
        name = str(row["NAME"])
        app_no = str(row["APPLICATION_NO"])

        self.info_label.configure(
            text=f"{slno} | {name} | {app_no}"
        )

        self.current_status = get_candidate_status(
            self.master.exam_id,
            slno
        )   
    # --------------------------
    def next_candidate(self):

        df = self.master.master_df
        row = df.iloc[self.current_candidate]

        slno = str(row["SLNO"])
        name = str(row["NAME"])

        responses = [v.get() for v in self.vars]

        save_candidate_status(
            self.master.exam_id,
            slno,
            name,
            self.current_status
        )

        save_candidate_responses(
            self.master.exam_id,
            slno,
            responses
        )

        correct = wrong = 0

        for i, q in enumerate(self.question_keys):
            key = self.master.answer_key_map[q]
            ans = responses[i]

            if ans == key:
                correct += 1
            elif ans not in ["BLANK", "MULTIPLE"]:
                wrong += 1

        score = correct - (wrong * 0.33)

        save_candidate_score(
            self.master.exam_id,
            slno,
            correct, wrong, 0, 0, score
        )

        if self.current_candidate < self.total_candidates - 1:
            self.current_candidate += 1
            self.load_candidate()
        else:
            self.destroy()