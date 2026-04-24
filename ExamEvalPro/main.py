import customtkinter as ctk

from database.db_manager import init_db
from ui.start_screen import StartScreen


def main():
    init_db()

    ctk.set_appearance_mode("System")

    app = ctk.CTk()
    app.title("ExamEval Pro")

    app.geometry("600x900+20+20")

    StartScreen(app)

    app.mainloop()


if __name__ == "__main__":
    main()