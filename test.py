import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Standardwerte
default_values = {
    'speed': 500,  # konstante Drehzahl
    'current_start': 1,
    'current_end': 20,
    'current_step': 1,
    'angle_start': 0,
    'angle_end': 90
}

def generate_dynamic_angle_grid(current_start, current_end, current_step, angle_start, angle_end):
    # Anzahl der Strompunkte basierend auf Schrittweite
    current_values = np.arange(current_start, current_end + current_step, current_step)
    
    # Erzeuge leeres Array für Winkelpunkte (dynamisch angepasst)
    dynamic_angle_values = []

    # Dynamische Winkelverteilung basierend auf Stromstärke
    max_points = 30  # Maximal erlaubte Winkelpunkte bei höherem Strom
    min_points = 5   # Minimal erlaubte Winkelpunkte bei niedrigerem Strom

    for current in current_values:
        # Lineare Skalierung der Anzahl der Winkelpunkte basierend auf dem Stromwert
        angle_count = int(np.interp(current, [current_start, current_end], [min_points, max_points]))
        angle_values = np.linspace(angle_start, angle_end, angle_count)
        dynamic_angle_values.append(angle_values)

    return current_values, dynamic_angle_values

def plot_id_iq(current_values, angle_grid):
    # Erstelle eine leere Liste für die id/iq-Werte
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

    # Erstelle den Plot
    plt.figure(figsize=(8, 6))
    plt.scatter(id_values, iq_values, c='red', marker='x')
    plt.title('id/iq Plot mit dynamischen Messpunkten')
    plt.xlabel('id (Strom in D-Richtung)')
    plt.ylabel('iq (Strom in Q-Richtung)')
    plt.grid(True)
    plt.axhline(0, color='black',linewidth=0.5)
    plt.axvline(0, color='black',linewidth=0.5)
    plt.show()

def main():
    # Hole die Standardwerte
    current_start = default_values['current_start']
    current_end = default_values['current_end']
    current_step = default_values['current_step']
    angle_start = default_values['angle_start']
    angle_end = default_values['angle_end']

    # Erzeuge das dynamische Gitter
    currents, angle_grid = generate_dynamic_angle_grid(current_start, current_end, current_step, angle_start, angle_end)

    # Erstelle den id/iq-Plot mit den Messpunkten
    plot_id_iq(currents, angle_grid)

if __name__ == "__main__":
    main()
