import tkinter as tk
from tkinter import messagebox
import subprocess

def starten_programm(programm):
    """Startet das ausgewählte Programm."""
    try:
        subprocess.run(['python', programm], check=True)
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Fehler", f"Das Programm konnte nicht gestartet werden:\n{e}")

def on_programm1_click():
    """Wird aufgerufen, wenn der erste Button geklickt wird."""
    starten_programm('uploadCSV.py')

def on_programm2_click():
    """Wird aufgerufen, wenn der zweite Button geklickt wird."""
    starten_programm('arbeitspunkte.py')

def on_programm3_click():
    """Wird aufgerufen, wenn der dritte Button geklickt wird."""
    starten_programm('Messdaten_auslesen.py')

def main():
    root = tk.Tk()
    root.title("Hauptprogramm")

    # Fenstergröße und Layout
    root.geometry("550x600")  # Größeres Fenster
    root.resizable(True, True)  # Fenstergröße anpassbar

    # Hauptrahmen
    main_frame = tk.Frame(root, padx=20, pady=20)
    main_frame.pack(expand=True, fill=tk.BOTH)

    # Titel
    tk.Label(main_frame, text="Verfügbare Programme", font=('Arial', 18, 'bold')).pack(pady=(0, 20))

    # Gruppierung: "Liste erstellen"
    liste_frame = tk.LabelFrame(main_frame, text="Liste erstellen", padx=10, pady=10, font=('Arial', 14, 'bold'))
    liste_frame.pack(fill=tk.X, pady=10)

    tk.Label(liste_frame, text="Erstellt eine Liste von Arbeitspunkten für die Kennfeldprüfung.", wraplength=450, justify='left').pack(pady=(5, 15))
    tk.Button(liste_frame, text="Starte Arbeitspunkte", command=on_programm2_click).pack(pady=(0, 5))

    # Gruppierung: "Messung durchführen"
    messung_frame = tk.LabelFrame(main_frame, text="Messung durchführen", padx=10, pady=10, font=('Arial', 14, 'bold'))
    messung_frame.pack(fill=tk.X, pady=10)

    # Upload CSV
    tk.Label(messung_frame, text="Stellt eine Verbindung zur SPS her und lädt eine Liste mit Arbeitspunkten hoch, welche vom Prüfstand angefahren werden.", wraplength=450, justify='left').pack(pady=(5, 15))
    tk.Button(messung_frame, text="Starte Upload CSV", command=on_programm1_click).pack(pady=(0, 5))

    # Messdaten Auslesen
    tk.Label(messung_frame, text="Liest die von der SPS protokollierten Messwerte nach der Messung aus und speichert sie als CSV-Datei.", wraplength=450, justify='left').pack(pady=(5, 15))
    tk.Button(messung_frame, text="Starte Messdaten Auslesen", command=on_programm3_click).pack(pady=(0, 5))

    # Beenden-Button
    tk.Button(main_frame, text="Beenden", command=root.quit, bg='red', fg='white', font=('Arial', 12, 'bold')).pack(pady=(15, 0))

    # GUI starten
    root.mainloop()

if __name__ == "__main__":
    main()
