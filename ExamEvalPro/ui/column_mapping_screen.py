import customtkinter as ctk


class ColumnMappingScreen(ctk.CTkToplevel):

    def __init__(self, master, columns):

        super().__init__(master)

        self.transient(master)
        self.lift()
        self.focus_force()

        self.title("Map Master Sheet Columns")
        self.geometry("900x450+500+250")

        self.columns = columns

        # 🔥 initialize mapping early
        self.mapping = None

        # 🔥 GRID CONFIG (THIS WAS MISSING)
        self.grid_columnconfigure(0, weight=3)   # LEFT EMPTY SPACE
        self.grid_columnconfigure(1, weight=1)   # RIGHT FORM

        # ---------------- TITLE ----------------
        ctk.CTkLabel(
            self,
            text="Map Master Sheet Columns",
            font=("Arial", 20, "bold")
        ).grid(row=0, column=0, columnspan=2, pady=20)

        # ---------------- FORM ----------------
        self.form_frame = ctk.CTkFrame(self)
        self.form_frame.grid(
            row=1,
            column=1,              # 🔥 RIGHT SIDE
            padx=(0, 40),
            pady=10,
            sticky="e"
        )

        # FORM GRID
        self.form_frame.grid_columnconfigure(0, weight=1)
        self.form_frame.grid_columnconfigure(1, weight=2)

        # ---------------- DROPDOWNS ----------------
        self.roll_menu = self.make_row("Serial Number Column", 0)
        self.app_menu = self.make_row("Application Number Column", 1)
        self.name_menu = self.make_row("Candidate Name Column", 2)
        self.cat_menu = self.make_row("Category Column", 3)

        # ---------------- BUTTON ----------------
        self.save_btn = ctk.CTkButton(
            self,
            text="Confirm Mapping",
            command=self.save_mapping,
            width=200
        )

        self.save_btn.grid(
            row=2,
            column=0,
            columnspan=2,
            pady=20
        )

    # -------------------------

    def make_row(self, label_text, row):

        label = ctk.CTkLabel(
            self.form_frame,
            text=label_text,
            width=220,
            anchor="w"   # 🔥 LEFT aligned for better look
        )
        label.grid(row=row, column=0, padx=(10, 10), pady=10)

        menu = ctk.CTkOptionMenu(
            self.form_frame,
            values=self.columns,
            width=260
        )
        menu.grid(row=row, column=1, padx=(10, 10), pady=10)

        return menu

    # -------------------------

    def save_mapping(self):

        self.mapping = {
            "roll_no": self.roll_menu.get(),
            "app_no": self.app_menu.get(),
            "name": self.name_menu.get(),
            "category": self.cat_menu.get()
        }

        print("Mapping:", self.mapping)

        self.save_btn.configure(
            text="Saved ✓",
            state="disabled"
        )

        self.destroy()