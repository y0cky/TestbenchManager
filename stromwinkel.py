import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os

# Datei für Standardwerte
DEFAULT_VALUES_CSV = 'default_values_stromwinkel.csv'

# Standardwerte
default_values = {
    'speed': 500,  # konstante Drehzahl
    'current_start': 1,
    'current_end': 20,
    'current_step': 1,
    'angle_start': 0,
    'angle_end': 90,
    'grid_fineness': 1.0  # Variable für die Feinheit des Gitters
}

df_global = None
canvas = None
fig = None

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

def generate_dynamic_angle_grid(current_start, current_end, current_step, angle_start, angle_end, grid_fineness):
    # Anzahl der Strompunkte basierend auf Schrittweite
    current_values = np.arange(current_start, current_end + current_step, current_step)
    
    # Erzeuge leeres Array für Winkelpunkte (dynamisch angepasst)
    dynamic_angle_values = []

    # Dynamische Winkelverteilung basierend auf Stromstärke
    max_points = 30 * grid_fineness  # Maximal erlaubte Winkelpunkte bei höherem Strom, skaliert mit der Feinheit
    min_points = 5 * grid_fineness   # Minimal erlaubte Winkelpunkte bei niedrigerem Strom, skaliert mit der Feinheit

    for current in current_values:
        # Lineare Skalierung der Anzahl der Winkelpunkte basierend auf dem Stromwert
        angle_count = int(np.interp(current, [current_start, current_end], [min_points, max_points]))
        angle_values = np.linspace(angle_start, angle_end, angle_count)
        dynamic_angle_values.append(angle_values)

    return current_values, dynamic_angle_values

def update_plot(current_values, angle_grid):
    global canvas, fig
    id_values = []
    iq_values = []

    # Berechnung von id und iq basierend auf dem Effektivstrom und dem Stromwinkel
    for current, angles in zip(current_values, angle_grid):
        for angle in angles:
            angle_rad = np.deg2rad(angle)  # Umrechnung von Grad in Radianten
            id = current * np.cos(angle_rad)  # id-Komponente
            iq = current * np.sin(angle_rad)  # iq-Komponente
            id_values.append(id)
            iq_values.append(iq)

    # Falls bereits eine Figur existiert, löschen und neu zeichnen
    if fig:
        fig.clear()

    # Neue Figur erstellen
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(id_values, iq_values, c='red', marker='x')
    ax.set_title('id/iq Plot mit Messpunkten')
    ax.set_xlabel('id (Strom in D-Richtung)')
    ax.set_ylabel('iq (Strom in Q-Richtung)')
    ax.grid(True)
    ax.axhline(0, color='black', linewidth=0.5)
    ax.axvline(0, color='black', linewidth=0.5)

    # Canvas updaten
    if canvas:
        canvas.get_tk_widget().pack_forget()
    canvas = FigureCanvasTkAgg(fig, master=plot_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

def update_table():
    if df_global is not None:
        for row in tree.get_children():
            tree.delete(row)

        for index, row in df_global.iterrows():
            tree.insert('', 'end', values=list(row))

def generate_and_show_table():
    global df_global
    try:
        # Eingabewerte aus der GUI holen
        speed = int(speed_var.get())
        current_start = int(current_start_var.get())
        current_end = int(current_end_var.get())
        current_step = int(current_step_var.get())
        angle_start = int(angle_start_var.get())
        angle_end = int(angle_end_var.get())
        grid_fineness = float(grid_fineness_var.get())

        # Dynamisches Gitter erzeugen
        currents, angles_grid = generate_dynamic_angle_grid(current_start, current_end, current_step, angle_start, angle_end, grid_fineness)

        # Erstelle eine leere Liste für die Tabelle
        table_data = []
        index = 1

        # Generiere die Tabelle
        for current, angles in zip(currents, angles_grid):
            for angle in angles:
                table_data.append([index, speed, current, round(angle, 2)])
                index += 1

        # DataFrame erstellen
        df_global = pd.DataFrame(table_data, columns=["index", "drehzahl", "strom_effektiv", "stromwinkel"])

        # Plot und Tabelle aktualisieren
        update_plot(currents, angles_grid)
        update_table()

    except ValueError:
        messagebox.showerror("Ungültige Eingabe", "Bitte stellen Sie sicher, dass alle Werte gültige Zahlen sind.")
        return

def save_csv():
    if df_global is not None:
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")], title="Tabelle speichern")
        if file_path:
            df_global.to_csv(file_path, index=False)

def on_closing():
    save_default_values()
    root.destroy()

def main():
    global root, speed_var, current_start_var, current_end_var, current_step_var, angle_start_var, angle_end_var, grid_fineness_var, plot_frame, canvas, fig, tree

    root = tk.Tk()
    root.title("Stromwinkel-Messung Generator")

    load_default_values()

    # Haupt-Layout
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

    tk.Label(frame, text="Stromwinkelbereich (Grad)", font=('Arial', 12, 'bold')).grid(row=5, column=0, columnspan=2, pady=5, sticky='w')
    tk.Label(frame, text="Startwinkel:").grid(row=6, column=0, sticky=tk.E)
    tk.Label(frame, text="Endwinkel:").grid(row=7, column=0, sticky=tk.E)

    angle_start_var = tk.StringVar(root, value=str(default_values['angle_start']))
    angle_end_var = tk.StringVar(root, value=str(default_values['angle_end']))

    tk.Entry(frame, textvariable=angle_start_var).grid(row=6, column=1, padx=5, pady=5, sticky='ew')
    tk.Entry(frame, textvariable=angle_end_var).grid(row=7, column=1, padx=5, pady=5, sticky='ew')

    tk.Label(frame, text="Feinheit des Gitters", font=('Arial', 12, 'bold')).grid(row=8, column=0, columnspan=2, pady=5, sticky='w')
    grid_fineness_var = tk.StringVar(root, value=str(default_values['grid_fineness']))
    tk.Entry(frame, textvariable=grid_fineness_var).grid(row=9, column=0, columnspan=2, padx=5, pady=5, sticky='ew')

    generate_and_show_button = tk.Button(frame, text="Tabelle generieren und anzeigen", command=generate_and_show_table)
    generate_and_show_button.grid(row=10, column=0, columnspan=2, pady=5)

    save_button = tk.Button(frame, text="Tabelle als CSV speichern", command=save_csv)
    save_button.grid(row=11, column=0, columnspan=2, pady=5)

    # Frame für den Plot
    plot_frame = tk.Frame(root)
    plot_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Tabelle der Messpunkte
    table_frame = tk.Frame(root)
    table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    columns = ["index", "drehzahl", "strom_effektiv", "stromwinkel"]
    tree = ttk.Treeview(table_frame, columns=columns, show='headings')

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=100, anchor='center')

    vsb = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=vsb.set)
    tree.pack(side='left', fill='both', expand=True)
    vsb.pack(side='right', fill='y')

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

# Wenn das Skript direkt ausgeführt wird, starte das Hauptprogramm
if __name__ == "__main__":
    main()
