import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd

class GiftFinderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gift Finder 🎁")
        self.root.geometry("900x600")
        self.df = None
        self.filename = None
        self.num_columns = 1
        self.card_width = 270
        self.cards = []
        self.loading_label = None  # For loading indicator

        self.create_widgets()
        
        self.canvas.bind_all("<MouseWheel>", self.on_mouse_wheel)
        self.canvas.bind_all("<Button-4>", self.on_mouse_wheel)
        self.canvas.bind_all("<Button-5>", self.on_mouse_wheel)

    def on_mouse_wheel(self, event):
        if event.num == 4:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self.canvas.yview_scroll(1, "units")
        elif event.delta:
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def center_popup(self, popup, width, height):
        parent_x = self.root.winfo_x()
        parent_y = self.root.winfo_y()
        parent_width = self.root.winfo_width()
        parent_height = self.root.winfo_height()

        x = parent_x + (parent_width - width) // 2
        y = parent_y + (parent_height - height) // 2

        popup.geometry(f"{width}x{height}+{x}+{y}")

    def show_loading_indicator(self, parent):
        if self.loading_label:
            self.loading_label.destroy()
        self.loading_label = ttk.Label(
            parent,
            text="טוען...",
            font=("Helvetica", 12, "bold"),
            background="#f9f9f9",
            foreground="#555"
        )
        self.loading_label.place(relx=0.5, rely=0.5, anchor="center")
        parent.update()

    def hide_loading_indicator(self):
        if self.loading_label:
            self.loading_label.destroy()
            self.loading_label = None

    def update_grid_layout(self, event=None):
        canvas_width = self.canvas.winfo_width()
        if canvas_width <= 1:
            canvas_width = self.root.winfo_width() - 20
        self.num_columns = max(1, canvas_width // self.card_width)

        for col in range(self.num_columns):
            self.results_frame.grid_columnconfigure(col, weight=1, minsize=self.card_width)
        for col in range(self.num_columns, 10):
            self.results_frame.grid_columnconfigure(col, weight=0, minsize=0)

        for widget in self.results_frame.winfo_children():
            widget.grid_forget()
        for idx, (card, row_data) in enumerate(self.cards):
            row_num = idx // self.num_columns
            col_num = (self.num_columns - 1) - (idx % self.num_columns)
            card.grid(row=row_num, column=col_num, padx=10, pady=8, sticky="e")
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def create_widgets(self):
        self.root.configure(bg="#f9f9f9")

        tk.Label(self.root, text="Gift Finder", font=("Helvetica", 20, "bold"), bg="#f9f9f9").pack(pady=10)

        tk.Button(self.root, text="📂 בחר קובץ Excel", command=self.load_file, bg="#4CAF50", fg="white",
                  font=("Helvetica", 11), padx=10, pady=5).pack(pady=5)

        self.file_label = tk.Label(self.root, text="לא נבחר קובץ", fg="#555", bg="#f9f9f9", font=("Helvetica", 10))
        self.file_label.pack()

        self.search_frame = tk.Frame(self.root, bg="#f9f9f9")
        self.search_frame.pack(pady=10)

        tk.Label(self.search_frame, text="🔍 חפש לפי שם:", bg="#f9f9f9", font=("Helvetica", 12)).pack(side=tk.LEFT)
        self.search_entry = tk.Entry(self.search_frame, font=("Helvetica", 12), width=30)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        tk.Button(self.search_frame, text="חפש", command=self.search_guest, bg="#2196F3", fg="white",
                  font=("Helvetica", 11), padx=8).pack(side=tk.LEFT)

        tk.Button(self.root, text="📑 הצג את תוכן הקובץ", command=self.show_full_df, bg="#FF9800", fg="white",
                  font=("Helvetica", 11), padx=10).pack(pady=5)

        self.canvas = tk.Canvas(self.root, borderwidth=0, background="#f9f9f9")
        self.results_frame = tk.Frame(self.canvas, background="#f9f9f9")
        self.vsb = tk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vsb.set)

        self.vsb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.create_window((0, 0), window=self.results_frame, anchor="nw", tags="self.results_frame")

        self.canvas.bind("<Configure>", self.update_grid_layout)
        self.results_frame.bind("<Configure>", lambda event: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

    def create_result_card(self, row, card_index):
        card = tk.Frame(self.results_frame, bd=1, relief=tk.RIDGE, padx=15, pady=10, bg="white", width=250)
        card.grid_propagate(False)

        row_num = card_index // self.num_columns
        col_num = (self.num_columns - 1) - (card_index % self.num_columns)
        card.grid(row=row_num, column=col_num, padx=10, pady=8, sticky="e")

        for i, value in enumerate(row):
            font = ("Helvetica", 11, "bold") if i == 0 else ("Helvetica", 11)  # Bold for first column
            label = tk.Label(
                card,
                text=f"{self.df.columns[i]}: {value}",
                font=font,
                bg="white",
                anchor="e",
                justify="right"
            )
            label.pack(fill="x", pady=2)

        self.cards.append((card, row))

    def clear_results(self):
        for widget in self.results_frame.winfo_children():
            widget.destroy()
        self.cards = []
        self.update_grid_layout()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def search_guest(self):
        name = self.search_entry.get().strip()
        if self.df is None:
            messagebox.showwarning("שים לב", "יש לטעון קובץ קודם")
            return
        if not name:
            messagebox.showwarning("שים לב", "יש להזין שם לחיפוש")
            return

        self.clear_results()
        matches = self.df[self.df.iloc[:, 0].astype(str).str.contains(name, na=False, case=False)]

        if matches.empty:
            tk.Label(self.results_frame, text="לא נמצאו תוצאות", fg="red", bg="#f9f9f9").pack(pady=10, anchor="e")
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
            return

        for idx, (_, row) in enumerate(matches.iterrows()):
            self.create_result_card(row, idx)
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def load_file(self):
        path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
        if not path:
            return
        try:
            self.show_loading_indicator(self.root)
            temp_df = pd.read_excel(path, engine="openpyxl", nrows=2)
            self.hide_loading_indicator()

            if temp_df.empty:
                messagebox.showerror("שגיאה", "הקובץ ריק או לא תקין")
                return

            default_headers = list(temp_df.columns)
            first_row = temp_df.iloc[0].tolist()
            num_columns = len(default_headers)

            is_first_row_valid = (
                all(isinstance(x, str) and pd.notna(x) for x in first_row) and
                len([x for x in first_row if pd.notna(x)]) == num_columns
            )

            choice_popup = tk.Toplevel(self.root)
            choice_popup.title("בחירת כותרות")
            self.center_popup(choice_popup, 600, 400)
            choice_popup.transient(self.root)
            choice_popup.grab_set()

            tk.Label(choice_popup, text="בחר את הכותרות עבור הקובץ:", font=("Helvetica", 12, "bold")).pack(pady=10)
            tk.Label(choice_popup, text="כותרות ברירת מחדל:", font=("Helvetica", 11)).pack()
            default_text = ", ".join(str(h) for h in default_headers)
            tk.Label(choice_popup, text=default_text, wraplength=500, justify="right").pack(pady=5)

            if is_first_row_valid:
                tk.Label(choice_popup, text="או, השורה הראשונה ככותרות:", font=("Helvetica", 11)).pack()
                first_row_text = ", ".join(str(h) for h in first_row)
                tk.Label(choice_popup, text=first_row_text, wraplength=500, justify="right").pack(pady=5)
            else:
                tk.Label(choice_popup, text="השורה הראשונה אינה תקינה ככותרות (חסרים ערכים או לא טקסט)", 
                         fg="red", font=("Helvetica", 10)).pack(pady=5)

            header_choice = tk.StringVar(value="default")
            tk.Radiobutton(choice_popup, text="השתמש בכותרות ברירת המחדל", variable=header_choice, value="default").pack(anchor="e", pady=5)
            if is_first_row_valid:
                tk.Radiobutton(choice_popup, text="השתמש בשורה הראשונה ככותרות", variable=header_choice, value="first_row").pack(anchor="e", pady=5)
            tk.Radiobutton(choice_popup, text="אף אחת מהכותרות לא נכונה (השתמש בשמות עמודות ברירת מחדל)", 
                           variable=header_choice, value="no_headers").pack(anchor="e", pady=5)

            def confirm_choice():
                try:
                    self.show_loading_indicator(self.root)
                    choice = header_choice.get()
                    if choice == "first_row":
                        self.df = pd.read_excel(path, header=1, engine="openpyxl")
                        extra_cols = len(self.df.columns) - len(first_row)
                        if extra_cols > 0:
                            new_columns = first_row + [f"עמודה {i+1}" for i in range(len(first_row), len(self.df.columns))]
                        else:
                            new_columns = first_row
                        self.df.columns = new_columns
                    elif choice == "no_headers":
                        self.df = pd.read_excel(path, header=None, engine="openpyxl")
                        self.df.columns = [f"עמודה {i+1}" for i in range(len(self.df.columns))]
                    else:
                        self.df = pd.read_excel(path, header=0, engine="openpyxl")
                    self.filename = path.split("/")[-1]
                    self.file_label.config(text=f"קובץ נבחר: {self.filename}")
                    self.clear_results()
                    self.df.dropna(how='all', inplace=True)
                    self.df.dropna(how='all', inplace=True, axis=1)
                    self.df.replace({pd.nan: ""}, inplace=True)
                    print(f"num of rows: {len(self.df)}")
                    self.hide_loading_indicator()
                    choice_popup.destroy()
                except Exception as e:
                    self.hide_loading_indicator()
                    messagebox.showerror("שגיאה", f"שגיאה בהגדרת הכותרות:\n{e}")
                    choice_popup.destroy()

            tk.Button(choice_popup, text="אשר", command=confirm_choice, bg="#4CAF50", fg="white").pack(pady=20)
            choice_popup.wait_window()

        except Exception as e:
            self.hide_loading_indicator()
            messagebox.showerror("שגיאה", f"שגיאה בקריאת הקובץ:\n{e}")

    def show_full_df(self):
        if self.df is None:
            messagebox.showwarning("שים לב", "יש לטעון קובץ קודם")
            return

        popup = tk.Toplevel(self.root)
        popup.title(f"תוכן הקובץ: {self.filename}")
        self.center_popup(popup, 1000, 500)

        self.show_loading_indicator(popup)

        container = tk.Frame(popup)
        container.pack(fill="both", expand=True)

        vsb = tk.Scrollbar(container, orient="vertical")
        hsb = tk.Scrollbar(container, orient="horizontal")

        tree = ttk.Treeview(
            container,
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set
        )
        vsb.config(command=tree.yview)
        hsb.config(command=tree.xview)

        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")
        tree.pack(side="left", fill="both", expand=True)

        tree["columns"] = list(self.df.columns)
        tree["show"] = "headings"


        for col in self.df.columns:
            tree.heading(col, text=col)
            tree.column(col, anchor="center", width=150)
            if col == self.df.columns[0]:  # Bold first column heading
                tree.heading(col, text=col, command=lambda c=col: tree.heading(c, text=c))

        for _, row in self.df.iterrows():
            values = list(row)
            tags = ("bold",) if values else ()  # Apply bold tag to first column
            tree.insert("", "end", values=values, tags=tags)

        self.hide_loading_indicator()

if __name__ == "__main__":
    root = tk.Tk()
    app = GiftFinderApp(root)
    root.mainloop()