import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd

class GiftFinderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("חיפוש מתנות לפי שם אורח")
        self.df = None

        # יצירת ממשק
        self.load_button = tk.Button(root, text="טען קובץ אקסל", command=self.load_excel)
        self.load_button.pack(pady=10)

        self.name_label = tk.Label(root, text="הכנס שם אורח:")
        self.name_label.pack()

        self.name_entry = tk.Entry(root, justify='right', width=40)
        self.name_entry.pack(pady=5)

        self.search_button = tk.Button(root, text="חפש מתנה", command=self.search_gift)
        self.search_button.pack(pady=10)

        self.result_text = tk.Text(root, height=10, width=60, wrap='word', font=("Arial", 12), padx=10, pady=10)
        self.result_text.pack()

    def load_excel(self):
        file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
        if file_path:
            try:
                self.df = pd.read_excel(file_path, engine="openpyxl", header=1)
                self.df.columns = ["שם", "מספר אורחים", "שיוך", "קבוצה", "מתנה", "הערה"]
                messagebox.showinfo("הצלחה", "הקובץ נטען בהצלחה!")
            except Exception as e:
                messagebox.showerror("שגיאה", f"שגיאה בטעינת הקובץ:\n{e}")

    def search_gift(self):
        guest_name = self.name_entry.get().strip()
        self.result_text.delete(1.0, tk.END)

        if self.df is None:
            messagebox.showwarning("לא נטען קובץ", "יש לטעון קובץ אקסל תחילה.")
            return

        if not guest_name:
            messagebox.showwarning("שם חסר", "אנא הזן שם לחיפוש.")
            return

        # חיפוש לפי השם
        matches = self.df[self.df["שם"].astype(str).str.contains(guest_name, case=False, na=False)]

        if matches.empty:
            self.result_text.insert(tk.END, "לא נמצאו תוצאות לאורח/ת.\n")
        else:
            for idx, row in matches.iterrows():
                result = f"שם: {row['שם']}\n"
                if pd.notna(row['מתנה']):
                    result += f"מתנה: {row['מתנה']}\n"
                if pd.notna(row['שיוך']):
                    result += f"שייכות: {row['שיוך']}\n"
                if pd.notna(row['קבוצה']):
                    result += f"קבוצה: {row['קבוצה']}\n"
                result += "-" * 40 + "\n"
                self.result_text.insert(tk.END, result)

# הרצת האפליקציה
if __name__ == "__main__":
    root = tk.Tk()
    app = GiftFinderApp(root)
    root.mainloop()
