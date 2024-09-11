import tkinter as tk
from tkinter import messagebox
import pandas as pd  # pandas importieren
import subprocess
import sys
import os
import uploadCSV
import arbeitspunkte
import Messdaten_auslesen
import stromwinkel  # Das neue Stromwinkel-Programm importieren

DEFAULT_VALUES_CSV = 'default_values.csv'

def load_default_values():
    """Lädt die Standardwerte aus der CSV-Datei."""
    default_values = {
        'speed_start': 100,
        'speed_end': 2500,
        'speed_step': 100,
        'torque_start': 5,
        'torque_end': 70,
        'torque_step': 5,
        'torque_limits': "1200=65,1300=60,1400=55,1500=50,1600=45,1700=40,1800=40,1900=35,2000=35,2100=30,2200=30,2300=25,2400=25,2500=25"
    }

    try:
        df = pd.read_csv(DEFAULT_VALUES_CSV)
        for key in default_values.keys():
            if key in df.columns:
                default_values[key] = df[key].iloc[0]
    except (FileNotFoundError, pd.errors.EmptyDataError):
        # Datei nicht gefunden oder leer, Standardwerte bleiben erhalten
        pass
    
    return default_values

def starten_programm(programm):
    """Startet das ausgewählte Programm."""
    try:
        # Den Pfad zur EXE finden und das Programm ausführen
        programm_exe = os.path.join(os.path.dirname(sys.executable), programm)
        subprocess.run([programm_exe], check=True)
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Fehler", f"Das Programm konnte nicht gestartet werden:\n{e}")

def on_programm1_click():
    uploadCSV.main()  # Startet das GUI des uploadCSV-Programms

def on_programm2_click():
    default_values = load_default_values()  # Standardwerte laden
    arbeitspunkte.main()  # Startet das GUI des Arbeitspunkte-Programms

def on_programm3_click():
    Messdaten_auslesen.main()

def on_stromwinkel_click():
    stromwinkel.main()  # Startet das GUI des Stromwinkel-Programms

def main():
    root = tk.Tk()
    root.title("TestbenchManager")

    root.geometry("550x800")
    root.resizable(True, True)

    main_frame = tk.Frame(root, padx=20, pady=20)
    main_frame.pack(expand=True, fill=tk.BOTH)

    tk.Label(main_frame, text="Werkzeuge", font=('Arial', 16, 'bold')).pack(pady=(0, 20))

    liste_frame = tk.LabelFrame(main_frame, text="Messung vorbereiten", padx=10, pady=10, font=('Arial', 14, 'bold'))
    liste_frame.pack(fill=tk.X, pady=10)

    # Stromwinkel zuerst hinzufügen
    tk.Label(liste_frame, text="Führt eine Stromwinkelmessung durch und speichert die Ergebnisse.", wraplength=450, justify='left').pack(pady=(5, 15))
    tk.Button(liste_frame, text="Starte Stromwinkel-Messung", command=on_stromwinkel_click).pack(pady=(0, 5))

    # Arbeitspunkte danach hinzufügen
    tk.Label(liste_frame, text="Erstellt eine Liste von Arbeitspunkten für die Kennfeldprüfung.", wraplength=450, justify='left').pack(pady=(5, 15))
    tk.Button(liste_frame, text="Starte Arbeitspunkte", command=on_programm2_click).pack(pady=(0, 5))

    messung_frame = tk.LabelFrame(main_frame, text="Messung durchführen", padx=10, pady=10, font=('Arial', 14, 'bold'))
    messung_frame.pack(fill=tk.X, pady=10)

    tk.Label(messung_frame, text="Stellt eine Verbindung zur SPS her und lädt eine Liste mit Arbeitspunkten hoch, welche vom Prüfstand angefahren werden.", wraplength=450, justify='left').pack(pady=(5, 15))
    tk.Button(messung_frame, text="Starte Upload CSV", command=on_programm1_click).pack(pady=(0, 5))

    tk.Label(messung_frame, text="Liest die von der SPS protokollierten Messwerte nach der Messung aus und speichert sie als CSV-Datei.", wraplength=450, justify='left').pack(pady=(5, 15))
    tk.Button(messung_frame, text="Starte Messdaten Auslesen", command=on_programm3_click).pack(pady=(0, 5))
    
    messung_frame = tk.LabelFrame(main_frame, text="Messdaten auswerten", padx=10, pady=10, font=('Arial', 14, 'bold'))
    messung_frame.pack(fill=tk.X, pady=10)
    
    tk.Label(messung_frame, text="Ermöglicht das grafische Analysieren von dokumentierten Messdaten", wraplength=450, justify='left').pack(pady=(5, 15))
    tk.Button(messung_frame, text="Starte CSV Plot", command=on_programm1_click).pack(pady=(0, 5))
    
    tk.Label(messung_frame, text="Berechnung verschiedener Verlustarten in bestimmten Arbeitspunkten anhand von Messergebnissen und Maschinenkenndaten", wraplength=450, justify='left').pack(pady=(5, 15))
    tk.Button(messung_frame, text="Starte Verlustberechnung", command=on_programm1_click).pack(pady=(0, 5))

    tk.Button(main_frame, text="Beenden", command=root.quit, font=('Arial', 12, 'bold')).pack(pady=(15, 0))

    root.mainloop()

if __name__ == "__main__":
    main()
