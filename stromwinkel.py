import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import os

# Datei für Standardwerte
DEFAULT_VALUES_CSV = 'default_values_stromwinkel.csv'

# Standardwerte
default_values = {
    'speed': 500,  # konstante Drehzahl
    'current_start': 1,
    'current_end': 20,
    'current_step': 1,
    'angle_values': "0,40,42,44,46,48,50,52,54,56,58,60,62,64,66,68,70,72,74,76,78,80,82,84,86,88,90"
}

df_global = None

def load_default_values():
    """Lädt die Standardwerte aus der CSV-Datei oder verwendet Standardwerte."""
    if os.path.exists(DEFAULT_VALUES_CSV):
        try:
            df = pd.read_csv(DEFAULT_VALUES_CSV)
            for key in default_values.keys():
                if key in df.columns:
                    default_values[key] = df[key].iloc[0]
        except pd.errors.EmptyDataError:
            pass
    else:
        save_default_values()

def save_default_values():
    """Speichert die Standardwerte in der CSV-Datei."""
    df = pd.DataFrame(default_values, index=[0])
    df.to_csv(DEFAULT_VALUES_CSV, index=False)

def generate_and_show_table():
    global df_global
    try:
        # Eingabewerte aus der GUI holen
        speed = int(speed_var.get())
        current_start = int(current_start_var.get())
        current_end = int(current_end_var.get())
        current_step = int(current_step_var.get())
        angle_values = list(map(int, angle_values_var.get().split(',')))

        # Erstelle die Messpunkte
        currents = range(current_start, current_end + current_step, current_step)

        # Erstelle eine leere Liste für die Tabelle
        table_data = []
        index = 1

        # Generiere die Tabelle
        for current in currents:
            for angle in angle_values:
                table_data.append([index, speed, current, angle])
                index += 1

        # DataFrame erstellen
        df_global = pd.DataFrame(table_data, columns=["index", "drehzahl", "strom_effektiv", "stromwinkel"])

        show_table()
    except ValueError:
        messagebox.showerror("Ungültige Eingabe", "Bitte stellen Sie sicher, dass alle Werte gültige Zahlen sind.")
        return

def show_table():
    if df_global is not None:
        table_window = tk.Toplevel(root)
        table_window.title("Erzeugte Tabelle")

        tree = ttk.Treeview(table_window, columns=list(df_global.columns), show='headings')

        for col in df_global.columns:
            tree.heading(col, text=col)
            tree.column(col, width=100, anchor='center')

        for index, row in df_global.iterrows():
            tree.insert('', 'end', values=list(row))

        vsb = ttk.Scrollbar(table_window, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(table_window, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        tree.pack(side='left', fill='both', expand=True)
        vsb.pack(side='right', fill='y')
        hsb.pack(side='bottom', fill='x')

def save_csv():
    if df_global is not None:
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")], title="Tabelle speichern")
        if file_path:
            df_global.to_csv(file_path, index=False)

def on_closing():
    save_default_values()
    root.destroy()

def main():
    global root, speed_var, current_start_var, current_end_var, current_step_var, angle_values_var

    root = tk.Tk()
    root.title("Stromwinkel-Messung Generator")

    load_default_values()

    frame = tk.Frame(root)
    frame.pack(fill='both', expand=True, padx=10, pady=10)

    tk.Label(frame, text="Drehzahl (min^-1)", font=('Arial', 12, 'bold')).grid(row=0, column=0, pady=5, sticky='w')
    speed_var = tk.StringVar(root, value=str(default_values['speed']))
    tk.Entry(frame, textvariable=speed_var).grid(row=0, column=1, padx=5, pady=5, sticky='ew')

    tk.Label(frame, text="Strombereich (A)", font=('Arial', 12, 'bold')).grid(row=1, column=0, columnspan=2, pady=5, sticky='w')
    tk.Label(frame, text="Start:").grid(row=2, column=0, sticky=tk.E)
    tk.Label(frame, text="Ende:").grid(row=3, column=0, sticky=tk.E)
    tk.Label(frame, text="Schrittweite:").grid(row=4, column=0, sticky=tk.E)

    current_start_var = tk.StringVar(root, value=str(default_values['current_start']))
    current_end_var = tk.StringVar(root, value=str(default_values['current_end']))
    current_step_var = tk.StringVar(root, value=str(default_values['current_step']))

    tk.Entry(frame, textvariable=current_start_var).grid(row=2, column=1, padx=5, pady=5, sticky='ew')
    tk.Entry(frame, textvariable=current_end_var).grid(row=3, column=1, padx=5, pady=5, sticky='ew')
    tk.Entry(frame, textvariable=current_step_var).grid(row=4, column=1, padx=5, pady=5, sticky='ew')

    tk.Label(frame, text="Stromwinkel (Grad)", font=('Arial', 12, 'bold')).grid(row=5, column=0, columnspan=2, pady=5, sticky='w')
    angle_values_var = tk.StringVar(root, value=default_values['angle_values'])
    tk.Entry(frame, textvariable=angle_values_var, width=50).grid(row=6, column=0, columnspan=2, padx=5, pady=5)

    generate_and_show_button = tk.Button(frame, text="Tabelle generieren und anzeigen", command=generate_and_show_table)
    generate_and_show_button.grid(row=7, column=0, columnspan=2, pady=5)

    save_button = tk.Button(frame, text="Tabelle als CSV speichern", command=save_csv)
    save_button.grid(row=8, column=0, columnspan=2, pady=5)

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

# Wenn das Skript direkt ausgeführt wird, starte das Hauptprogramm
if __name__ == "__main__":
    main()
