import customtkinter as ctk
from tkinter import messagebox
from tkcalendar import DateEntry

from database.db_manager import save_exam
from ui.import_screen import ImportScreen
from ui.open_exam_screen import OpenExamScreen


class StartScreen(ctk.CTkFrame):

    def __init__(self, master):

        super().__init__(master)

        self.pack(fill="both", expand=True, padx=20, pady=20)

        # ⭐ IMPORTANT (shared state)
        self.exam_id = None

        ctk.CTkLabel(
            self,
            text="EXAMEVAL PRO",
            font=("Arial", 24, "bold")
        ).pack(pady=10)

        self.fields = {}

        # -------- EXAM NAME --------
        self.add_entry("Examination Name")

        # -------- DATE --------
        ctk.CTkLabel(self, text="Date of Examination").pack()

        self.date_picker = DateEntry(self, date_pattern="dd.mm.yyyy")
        self.date_picker.pack(pady=4)

        # -------- VENUE --------
        self.add_entry("Venue")

        # -------- TIME --------
        times = self.build_time_slots()

        ctk.CTkLabel(self, text="Start Time").pack()
        self.start_time_menu = ctk.CTkOptionMenu(
            self,
            values=times,
            command=lambda x: self.calculate_duration()
        )
        self.start_time_menu.pack(pady=4)

        ctk.CTkLabel(self, text="End Time").pack()
        self.end_time_menu = ctk.CTkOptionMenu(
            self,
            values=times,
            command=lambda x: self.calculate_duration()
        )
        self.end_time_menu.pack(pady=4)

        # -------- DURATION --------
        ctk.CTkLabel(self, text="Duration (Minutes)").pack()
        self.duration_entry = ctk.CTkEntry(self, width=350)
        self.duration_entry.pack(pady=4)
        self.duration_entry.insert(0, "0")

        # -------- OTHER FIELDS --------
        self.add_entry("Conducting Authority")
        self.add_entry("Advertisement No")
        self.add_entry("Number of Questions")
        self.add_entry("Vacancies")

        # -------- BUTTONS --------
        ctk.CTkButton(
            self,
            text="Create Examination",
            command=self.create_exam
        ).pack(pady=15)

        ctk.CTkButton(
            self,
            text="Open Existing Examination",
            command=self.open_exam
        ).pack(pady=5)

    # ---------------- ENTRY BUILDER ----------------

    def add_entry(self, label):

        ctk.CTkLabel(self, text=label).pack()

        entry = ctk.CTkEntry(self, width=350)
        entry.pack(pady=4)

        self.fields[label] = entry

    # ---------------- TIME ----------------

    def build_time_slots(self):

        slots = []
        for hour in range(8, 21):
            for minute in [0, 15, 30, 45]:
                slots.append(f"{hour:02d}:{minute:02d}")

        return slots

    def time_to_minutes(self, time_str):

        h, m = map(int, time_str.split(":"))
        return h * 60 + m

    def calculate_duration(self):

        try:
            start = self.time_to_minutes(self.start_time_menu.get())
            end = self.time_to_minutes(self.end_time_menu.get())

            if end <= start:
                self.duration_entry.delete(0, "end")
                self.duration_entry.insert(0, "INVALID")
                return

            duration = end - start

            self.duration_entry.delete(0, "end")
            self.duration_entry.insert(0, str(duration))

        except:
            pass

    # ---------------- OPEN EXISTING ----------------

    def open_exam(self):

        screen = OpenExamScreen(self)

        screen.grab_set()
        self.wait_window(screen)

    # ---------------- CREATE EXAM ----------------

    def create_exam(self):

        try:

            # -------- VALIDATION --------

            if not self.fields["Number of Questions"].get().isdigit():
                messagebox.showerror("Validation Error", "Number of Questions must be numeric.")
                return

            if not self.fields["Vacancies"].get().isdigit():
                messagebox.showerror("Validation Error", "Vacancies must be numeric.")
                return

            start = self.time_to_minutes(self.start_time_menu.get())
            end = self.time_to_minutes(self.end_time_menu.get())

            if end <= start:
                messagebox.showerror("Validation Error", "End Time must be later than Start Time.")
                return

            # -------- PROFILE --------

            profile = {
                "exam_name": self.fields["Examination Name"].get(),
                "exam_date": self.date_picker.get(),
                "venue": self.fields["Venue"].get(),
                "start_time": self.start_time_menu.get(),
                "end_time": self.end_time_menu.get(),
                "duration_minutes": int(self.duration_entry.get()),
                "conducting_authority": self.fields["Conducting Authority"].get(),
                "advertisement_no": self.fields["Advertisement No"].get(),
                "question_count": int(self.fields["Number of Questions"].get()),
                "vacancies": int(self.fields["Vacancies"].get())
            }

            # -------- SAVE --------

            exam_id, exists = save_exam(profile)

            # ⭐ CRITICAL FIX
            self.exam_id = exam_id

            if exists:
                choice = messagebox.askyesno(
                    "Exam Exists",
                    "This exam already exists.\nDo you want to resume it?"
                )

                if choice:
                    OpenExamScreen(self)

                return

            # -------- SUCCESS --------

            messagebox.showinfo("Success", "Examination created successfully.")

            # ⭐ PASS CONTROL TO IMPORT SCREEN
            import_screen = ImportScreen(self)
            import_screen.exam_id = self.exam_id

        except Exception as e:
            messagebox.showerror("Error", str(e))