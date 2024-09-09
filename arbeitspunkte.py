import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import os

# Datei für Standardwerte
DEFAULT_VALUES_CSV = 'default_values.csv'

# Standardwerte
default_values = {
    'speed_start': 100,
    'speed_end': 2500,
    'speed_step': 100,
    'torque_start': 5,
    'torque_end': 70,
    'torque_step': 5,
    'torque_limits': "1200=65,1300=60,1400=55,1500=50,1600=45,1700=40,1800=40,1900=35,2000=35,2100=30,2200=30,2300=25,2400=25,2500=25"
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
            # Datei ist leer, daher werden Standardwerte verwendet
            pass
    else:
        save_default_values()

def save_default_values():
    """Speichert die Standardwerte in der CSV-Datei."""
    df = pd.DataFrame(default_values, index=[0])
    df.to_csv(DEFAULT_VALUES_CSV, index=False)

def generate_and_show_table():
    global df_global
    # Eingabewerte aus der GUI holen
    speed_start = int(speed_start_var.get())
    speed_end = int(speed_end_var.get())
    speed_step = int(speed_step_var.get())
    
    torque_start = int(torque_start_var.get())
    torque_end = int(torque_end_var.get())
    torque_step = int(torque_step_var.get())

    # Drehzahlbereich und Drehmomentbereich erstellen
    speeds = range(speed_start, speed_end + speed_step, speed_step)
    torques = range(torque_start, torque_end + torque_step, torque_step)

    # Begrenzung der Maximalwerte des Drehmoments bei hohen Drehzahlen
    torque_limitations = {}
    for entry in torque_limits_var.get().split(','):
        speed, limit = map(int, entry.split('='))
        torque_limitations[speed] = limit

    # Erstelle eine leere Liste für die Tabelle
    table_data = []

    # Generiere die Tabelle
    for torque in torques:
        row = [torque]
        for n in speeds:
            # Begrenze das Drehmoment, wenn eine Begrenzung für die Drehzahl existiert
            limited_torque = min(torque, torque_limitations.get(n, torque))
            row.append((n, limited_torque))
        table_data.append(row)

    # Erstelle ein DataFrame
    columns = ["n/M"] + list(speeds)
    df_global = pd.DataFrame(table_data, columns=columns)

    # Tabelle in neuem Fenster anzeigen
    show_table()

def show_table():
    if df_global is not None:
        # Neues Fenster erstellen
        table_window = tk.Toplevel(root)
        table_window.title("Erzeugte Tabelle")

        # Erstelle ein Treeview-Widget
        tree = ttk.Treeview(table_window, columns=list(df_global.columns), show='headings')

        # Spaltenüberschriften hinzufügen
        for col in df_global.columns:
            tree.heading(col, text=col)
            tree.column(col, width=100, anchor='center')

        # Daten hinzufügen
        for index, row in df_global.iterrows():
            tree.insert('', 'end', values=list(row))

        # Scrollbars hinzufügen
        vsb = ttk.Scrollbar(table_window, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(table_window, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        # Packen der Widgets
        tree.pack(side='left', fill='both', expand=True)
        vsb.pack(side='right', fill='y')
        hsb.pack(side='bottom', fill='x')

def save_csv():
    if df_global is not None:
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")], title="Tabelle speichern")
        if file_path:
            df_global.to_csv(file_path, index=False)

def save_list_as_csv():
    if df_global is not None:
        # Wähle die Sortierreihenfolge
        sort_order = sort_order_var.get()
        
        # Erstelle eine leere Liste für die Daten
        list_data = set()  # Verwende ein Set, um doppelte Punkte zu vermeiden
        removed_duplicates_count = 0  # Zähler für entfernte Duplikate

        # Fülle die Liste mit den Werten aus der Tabelle
        for _, row in df_global.iterrows():
            torque = row["n/M"]
            for n, torque_value in zip(df_global.columns[1:], row[1:]):
                new_point = (torque_value[1], n)
                if new_point in list_data:
                    removed_duplicates_count += 1
                else:
                    list_data.add(new_point)  # Verwende ein Tuple (Drehmoment, Drehzahl)

        # Erstelle ein DataFrame für die Liste
        list_df = pd.DataFrame(list(list_data), columns=["Drehmoment", "Drehzahl"])

        # Sortiere die Liste basierend auf der Auswahl
        if sort_order == "torque_first":
            list_df = list_df.sort_values(by=["Drehmoment", "Drehzahl"])
        else:
            list_df = list_df.sort_values(by=["Drehzahl", "Drehmoment"])

        # Füge eine fortlaufende Index-Spalte hinzu, beginnend bei 0
        list_df.reset_index(drop=True, inplace=True)
        list_df.index.name = 'Index'

        # Speichere die Liste als CSV-Datei
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")], title="Liste speichern")
        if file_path:
            list_df.to_csv(file_path, index=True)
            # Zeige die Anzahl der entfernten doppelten Punkte an
            messagebox.showinfo("Info", f"CSV-Datei gespeichert. {removed_duplicates_count} doppelte Arbeitspunkte entfernt.")

            # Zeige die gespeicherte Liste in einem neuen Fenster an
            show_saved_list(file_path)

def show_saved_list(file_path):
    # Neues Fenster erstellen
    list_window = tk.Toplevel(root)
    list_window.title("Gespeicherte Liste")

    # Lese die CSV-Datei
    df_list = pd.read_csv(file_path)

    # Erstelle ein Treeview-Widget
    tree = ttk.Treeview(list_window, columns=list(df_list.columns), show='headings')

    # Spaltenüberschriften hinzufügen
    for col in df_list.columns:
        tree.heading(col, text=col)
        tree.column(col, width=100, anchor='center')

    # Daten hinzufügen
    for _, row in df_list.iterrows():
        tree.insert('', 'end', values=list(row))

    # Scrollbars hinzufügen
    vsb = ttk.Scrollbar(list_window, orient="vertical", command=tree.yview)
    hsb = ttk.Scrollbar(list_window, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

    # Packen der Widgets
    tree.pack(side='left', fill='both', expand=True)
    vsb.pack(side='right', fill='y')
    hsb.pack(side='bottom', fill='x')

# Erstelle die Hauptanwendung
root = tk.Tk()
root.title("Arbeitspunkte Generator")

# Lade Standardwerte
load_default_values()

# GUI Layout
frame = tk.Frame(root)
frame.pack(fill='both', expand=True, padx=10, pady=10)

# Drehzahlbereich-Einstellungen
tk.Label(frame, text="Drehzahlbereich (min^-1)", font=('Arial', 12, 'bold')).grid(row=0, column=0, columnspan=2, pady=5, sticky='w')
tk.Label(frame, text="Start:").grid(row=1, column=0, sticky=tk.E)
tk.Label(frame, text="Ende:").grid(row=2, column=0, sticky=tk.E)
tk.Label(frame, text="Schrittweite:").grid(row=3, column=0, sticky=tk.E)

speed_start_var = tk.StringVar(value=str(default_values['speed_start']))
speed_end_var = tk.StringVar(value=str(default_values['speed_end']))
speed_step_var = tk.StringVar(value=str(default_values['speed_step']))

tk.Entry(frame, textvariable=speed_start_var).grid(row=1, column=1, padx=5, pady=5, sticky='ew')
tk.Entry(frame, textvariable=speed_end_var).grid(row=2, column=1, padx=5, pady=5, sticky='ew')
tk.Entry(frame, textvariable=speed_step_var).grid(row=3, column=1, padx=5, pady=5, sticky='ew')

# Drehmomentbereich-Einstellungen
tk.Label(frame, text="Drehmomentbereich (Nm)", font=('Arial', 12, 'bold')).grid(row=4, column=0, columnspan=2, pady=5, sticky='w')
tk.Label(frame, text="Start:").grid(row=5, column=0, sticky=tk.E)
tk.Label(frame, text="Ende:").grid(row=6, column=0, sticky=tk.E)
tk.Label(frame, text="Schrittweite:").grid(row=7, column=0, sticky=tk.E)

torque_start_var = tk.StringVar(value=str(default_values['torque_start']))
torque_end_var = tk.StringVar(value=str(default_values['torque_end']))
torque_step_var = tk.StringVar(value=str(default_values['torque_step']))

tk.Entry(frame, textvariable=torque_start_var).grid(row=5, column=1, padx=5, pady=5, sticky='ew')
tk.Entry(frame, textvariable=torque_end_var).grid(row=6, column=1, padx=5, pady=5, sticky='ew')
tk.Entry(frame, textvariable=torque_step_var).grid(row=7, column=1, padx=5, pady=5, sticky='ew')

# Feldschwächebereich-Einstellungen
tk.Label(frame, text="Feldschwächebereich (Drehmomentbegrenzung)", font=('Arial', 12, 'bold')).grid(row=8, column=0, columnspan=2, pady=5, sticky='w')
tk.Label(frame, text="Drehzahlen=Begrenzung (z.B. 1200=65,1300=60)").grid(row=9, column=0, columnspan=2)

torque_limits_var = tk.StringVar(value=default_values['torque_limits'])
tk.Entry(frame, textvariable=torque_limits_var, width=50).grid(row=10, column=0, columnspan=2, padx=5, pady=5)

# Buttons
generate_and_show_button = tk.Button(frame, text="Tabelle generieren und anzeigen", command=generate_and_show_table)
generate_and_show_button.grid(row=11, column=0, columnspan=2, pady=5)

save_button = tk.Button(frame, text="Tabelle als CSV speichern", command=save_csv)
save_button.grid(row=12, column=0, columnspan=2, pady=5)

sort_order_var = tk.StringVar(value="torque_first")
tk.Label(frame, text="Sortierreihenfolge für CSV:", font=('Arial', 12, 'bold')).grid(row=13, column=0, columnspan=2, pady=10, sticky='w')
tk.Radiobutton(frame, text="Drehmoment > Drehzahl", variable=sort_order_var, value="torque_first").grid(row=14, column=0, columnspan=2, sticky='w')
tk.Radiobutton(frame, text="Drehzahl > Drehmoment", variable=sort_order_var, value="speed_first").grid(row=15, column=0, columnspan=2, sticky='w')

save_list_button = tk.Button(frame, text="Liste als CSV speichern", command=save_list_as_csv)
save_list_button.grid(row=16, column=0, columnspan=2, pady=5)

# Funktion zum Speichern der Standardwerte bei Programmende
def on_closing():
    save_default_values()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)

# Starte die Hauptanwendung
root.mainloop()
