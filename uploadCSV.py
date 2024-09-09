import tkinter as tk
from tkinter import filedialog, messagebox, ttk, Toplevel
import pandas as pd
import numpy as np
from opcua import Client, ua

# Globale Variablen für Einstellungen
opcua_url = "opc.tcp://192.168.0.1:4840"
db_name = "Messpunkte_DB"
namespace_index = 3
opcua_username = ""
opcua_password = ""

# Globale Variable für Daten
daten = None
dateiname = ""

# CSV Datei öffnen
def read_csv(csv_datei):
    try:
        daten = pd.read_csv(csv_datei)
        return daten
    except Exception as e:
        messagebox.showerror("Fehler", f"Fehler beim Lesen der CSV-Datei: {e}")
        return None

# CSV Format überprüfen
def validate_csv_format(daten):
    required_columns = []
    if mode.get() == "Kennfeld":
        required_columns = ['index', 'drehzahl', 'drehmoment']
    elif mode.get() == "Stromwinkel":
        required_columns = ['index', 'drehzahl', 'strom_effektiv', 'stromwinkel']

    missing_columns = [col for col in required_columns if col not in daten.columns]
    if missing_columns:
        return False, f"Fehlende Spalten: {', '.join(missing_columns)}"

    # Überprüfen der Datenformate
    for col in required_columns:
        if not pd.api.types.is_numeric_dtype(daten[col]):
            return False, f"Spalte '{col}' enthält keine numerischen Daten"
    
    return True, ""

# Variable in SPS schreiben
def write_SPS(variable, value_array, value_type):
    try:
        node_id = f'ns={namespace_index};s="{db_name}"."{variable}"'
        node = client.get_node(node_id)
        
        if value_type == ua.VariantType.Int16:
            value_array = value_array.astype(int)
        
        new_value = ua.DataValue(ua.Variant(value_array.tolist(), value_type))
        node.set_value(new_value)
        print(f"Value of '{variable}' set to: {new_value.Value}")
    except Exception as e:
        messagebox.showerror("Fehler", f"Fehler beim Schreiben der Variable in SPS: {e}")

# Verbindung zu OPC-UA Server herstellen
def connect_to_server():
    global client
    try:
        client = Client(opcua_url)
        if opcua_username and opcua_password:
            client.set_user(opcua_username)
            client.set_password(opcua_password)
        client.connect()
        print("Connected to OPC-UA server")
    except Exception as e:
        messagebox.showerror("Fehler", f"Fehler beim Verbinden zum OPC-UA Server: {e}")

# Verbindung zu OPC-UA Server trennen
def disconnect_from_server():
    try:
        client.disconnect()
        print("Disconnected from OPC-UA server")
    except Exception as e:
        messagebox.showerror("Fehler", f"Fehler beim Trennen vom OPC-UA Server: {e}")

# CSV Datei hochladen und anzeigen
def upload_csv():
    global daten, dateiname
    csv_datei = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if csv_datei:
        dateiname = csv_datei.split("/")[-1]
        daten = read_csv(csv_datei)
        if daten is not None:
            valid, message = validate_csv_format(daten)
            if not valid:
                messagebox.showerror("Fehler", message)
            else:
                # Dateinamen Label aktualisieren
                filename_label.config(text=f"Dateiname: {dateiname}")
                display_data(daten)

# CSV-Daten in der Tabelle anzeigen
def display_data(daten):
    for row in tree.get_children():
        tree.delete(row)

    tree["columns"] = list(daten.columns)
    tree["show"] = "headings"

    for col in tree["columns"]:
        tree.heading(col, text=col)

    for index, row in daten.iterrows():
        tree.insert("", "end", values=list(row))

# Daten an SPS senden
def send_to_sps():
    global daten
    if daten is None:
        messagebox.showerror("Fehler", "Keine CSV-Daten zum Senden. Bitte laden Sie zuerst eine CSV-Datei hoch.")
        return

    try:
        # Verbindung herstellen
        connect_to_server()

        if mode.get() == "Kennfeld":
            index_array = np.zeros(1000, dtype=np.int16)
            drehzahl_array = np.zeros(1000, dtype=np.float32)
            drehmoment_array = np.zeros(1000, dtype=np.float32)

            rows_to_copy = min(len(daten), 1000)
            index_array[:rows_to_copy] = daten['index'][:rows_to_copy].values
            drehzahl_array[:rows_to_copy] = daten['drehzahl'][:rows_to_copy].values
            drehmoment_array[:rows_to_copy] = daten['drehmoment'][:rows_to_copy].values
            
            write_SPS("index", index_array, ua.VariantType.Int16)
            write_SPS("drehzahl", drehzahl_array, ua.VariantType.Float)
            write_SPS("drehmoment", drehmoment_array, ua.VariantType.Float)
        
        elif mode.get() == "Stromwinkel":
            index_array = np.zeros(1000, dtype=np.int16)
            drehzahl_array = np.zeros(1000, dtype=np.float32)
            strom_effektiv_array = np.zeros(1000, dtype=np.float32)
            stromwinkel_array = np.zeros(1000, dtype=np.float32)

            rows_to_copy = min(len(daten), 1000)
            index_array[:rows_to_copy] = daten['index'][:rows_to_copy].values
            drehzahl_array[:rows_to_copy] = daten['drehzahl'][:rows_to_copy].values
            strom_effektiv_array[:rows_to_copy] = daten['strom_effektiv'][:rows_to_copy].values
            stromwinkel_array[:rows_to_copy] = daten['stromwinkel'][:rows_to_copy].values
            
            write_SPS("index", index_array, ua.VariantType.Int16)
            write_SPS("drehzahl", drehzahl_array, ua.VariantType.Float)
            write_SPS("Strom_Effektivwert", strom_effektiv_array, ua.VariantType.Float)
            write_SPS("Stromwinkel", stromwinkel_array, ua.VariantType.Float)
        
        messagebox.showinfo("Erfolg", "Daten erfolgreich an SPS gesendet")

    except KeyError as e:
        messagebox.showerror("Fehler", f"Fehlender Spaltenname in der CSV-Datei: {e}")

    finally:
        # Verbindung trennen
        disconnect_from_server()

# Daten manuell eingeben
def enter_data_manually():
    def on_submit():
        try:
            start_drehzahl = float(entry_start_drehzahl.get())
            step_drehzahl = float(entry_step_drehzahl.get())
            end_drehzahl = float(entry_end_drehzahl.get())
            
            start_drehmoment = float(entry_start_drehmoment.get())
            step_drehmoment = float(entry_step_drehmoment.get())
            end_drehmoment = float(entry_end_drehmoment.get())
            
            drehzahl_values = np.arange(start_drehzahl, end_drehzahl + step_drehzahl, step_drehzahl)
            drehmoment_values = np.arange(start_drehmoment, end_drehmoment + step_drehmoment, step_drehmoment)
            
            data = [(i, dz, dm) for i, (dz, dm) in enumerate(np.array(np.meshgrid(drehzahl_values, drehmoment_values)).T.reshape(-1, 2))]
            
            global daten
            daten = pd.DataFrame(data, columns=['index', 'drehzahl', 'drehmoment'])
            
            display_data(daten)
            manual_entry_window.destroy()
            messagebox.showinfo("Erfolg", "Daten erfolgreich manuell eingegeben")
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler bei der manuellen Dateneingabe: {e}")

    # Fenster für die manuelle Eingabe
    manual_entry_window = Toplevel(root)
    manual_entry_window.title("Daten manuell eingeben")

    # Drehzahl Eingabe
    tk.Label(manual_entry_window, text="Anfangswert Drehzahl:").grid(row=0, column=0, padx=10, pady=5, sticky='e')
    entry_start_drehzahl = tk.Entry(manual_entry_window)
    entry_start_drehzahl.grid(row=0, column=1, padx=10, pady=5)
    
    tk.Label(manual_entry_window, text="Schrittweite Drehzahl:").grid(row=1, column=0, padx=10, pady=5, sticky='e')
    entry_step_drehzahl = tk.Entry(manual_entry_window)
    entry_step_drehzahl.grid(row=1, column=1, padx=10, pady=5)
    
    tk.Label(manual_entry_window, text="Endwert Drehzahl:").grid(row=2, column=0, padx=10, pady=5, sticky='e')
    entry_end_drehzahl = tk.Entry(manual_entry_window)
    entry_end_drehzahl.grid(row=2, column=1, padx=10, pady=5)
    
    # Drehmoment Eingabe
    tk.Label(manual_entry_window, text="Anfangswert Drehmoment:").grid(row=3, column=0, padx=10, pady=5, sticky='e')
    entry_start_drehmoment = tk.Entry(manual_entry_window)
    entry_start_drehmoment.grid(row=3, column=1, padx=10, pady=5)
    
    tk.Label(manual_entry_window, text="Schrittweite Drehmoment:").grid(row=4, column=0, padx=10, pady=5, sticky='e')
    entry_step_drehmoment = tk.Entry(manual_entry_window)
    entry_step_drehmoment.grid(row=4, column=1, padx=10, pady=5)
    
    tk.Label(manual_entry_window, text="Endwert Drehmoment:").grid(row=5, column=0, padx=10, pady=5, sticky='e')
    entry_end_drehmoment = tk.Entry(manual_entry_window)
    entry_end_drehmoment.grid(row=5, column=1, padx=10, pady=5)
    
    # Bestätigungsbutton
    btn_submit = tk.Button(manual_entry_window, text="Eingaben bestätigen", command=on_submit)
    btn_submit.grid(row=6, column=0, columnspan=2, pady=10)

# Hauptprogramm
if __name__ == "__main__":
    root = tk.Tk()
    root.title("CSV zu OPC-UA")

    # Hauptframe
    main_frame = tk.Frame(root, padx=20, pady=20)
    main_frame.pack(fill='both', expand=True)

    # Modus-Umschalter
    mode = tk.StringVar(value="Kennfeld")  # Standardmäßig auf "Kennfeld" gesetzt
    mode_frame = tk.LabelFrame(main_frame, text="Modus auswählen", padx=10, pady=10)
    mode_frame.pack(fill='x', padx=10, pady=10)

    tk.Radiobutton(mode_frame, text="Kennfeld", variable=mode, value="Kennfeld").pack(anchor='w')
    tk.Radiobutton(mode_frame, text="Stromwinkel", variable=mode, value="Stromwinkel").pack(anchor='w')

    # CSV hochladen Button
    btn_upload = tk.Button(main_frame, text="CSV Datei hochladen", command=upload_csv, width=30)
    btn_upload.pack(pady=10)

    # Dateiname Label
    filename_label = tk.Label(main_frame, text="Dateiname: None", padx=10, pady=10)
    filename_label.pack()

    # Tabelle für CSV-Daten
    table_frame = tk.LabelFrame(main_frame, text="CSV Daten", padx=10, pady=10)
    table_frame.pack(fill='both', expand=True, padx=10, pady=10)

    # Scrollbars und Tabelle erstellen
    tree = ttk.Treeview(table_frame, columns=[], show='headings')
    tree.pack(side='left', fill='both', expand=True)

    vsb = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
    vsb.pack(side='right', fill='y')
    tree.configure(yscrollcommand=vsb.set)

    hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=tree.xview)
    hsb.pack(side='bottom', fill='x')
    tree.configure(xscrollcommand=hsb.set)

    # Daten senden Button
    btn_send = tk.Button(main_frame, text="Daten an SPS senden", command=send_to_sps, width=30)
    btn_send.pack(pady=10)

    # Manuelle Eingabe Button
    btn_manual_entry = tk.Button(main_frame, text="Daten manuell eingeben", command=enter_data_manually, width=30)
    btn_manual_entry.pack(pady=10)

    # Beenden Button
    btn_exit = tk.Button(main_frame, text="Beenden", command=root.quit, width=30)
    btn_exit.pack(pady=10)

    root.mainloop()
