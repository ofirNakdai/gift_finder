import pandas as pd

def load_gift_data(filename):
    df = pd.read_excel(filename, engine='openpyxl', header=1)
    print(df.head())  # הדפסת 5 השורות הראשונות כדי לוודא שהנתונים נטענו כראוי
    return df

def find_guest_gift(df, guest_name):
    # חיפוש לא רגיש לאותיות קטנות/גדולות
    df['הזמנה לכבוד'] = df['הזמנה לכבוד'].astype(str)
    matches = df[df['הזמנה לכבוד'].str.contains(guest_name, case=False, na=False)]
    return matches

def print_results_hebrew(df):
    # הדפסת התוצאות בצורה מסודרת מימין לשמאל
    for index, row in df.iterrows():
        print(f"אורח/ת: {row['הזמנה לכבוד']}")
        if 'מתנה' in row and pd.notna(row['מתנה']):
            print(f"מתנה: {row['מתנה']}")
        if 'סכום' in row and pd.notna(row['סכום']):
            print(f"סכום: {row['סכום']}")
        print("-" * 30)

def main():
    file_path = "gifts_file.xlsx"
    # guest_name = input("הכנס שם אורח לחיפוש: ").strip()
    guest_name = "תמיר"

    try:
        df = load_gift_data(file_path)
        results = find_guest_gift(df, guest_name)

        if not results.empty:
            print("\nנמצאו תוצאות:\n")
            print_results_hebrew(results)
        else:
            print("\nלא נמצאו מתנות על שם האורח/ת.")
    except Exception as e:
        print(f"שגיאה: {e}")

if __name__ == "__main__":
    main()
