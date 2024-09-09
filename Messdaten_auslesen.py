import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from opcua import Client, ua
import pandas as pd

class OPCUAGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("OPC-UA Data Viewer")
        self.client = None
        self.data = None
        
        # Setup GUI components
        self.setup_gui()
    
    def setup_gui(self):
        # Configure window resize behavior
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)

        # Frame for the buttons
        button_frame = tk.Frame(self.root)
        button_frame.grid(row=0, column=0, sticky='ew', padx=10, pady=10)

        # Fetch Data Button
        self.fetch_button = tk.Button(button_frame, text="Fetch Data", command=self.fetch_data)
        self.fetch_button.pack(side=tk.LEFT, padx=5)

        # Save to CSV Button
        self.save_button = tk.Button(button_frame, text="Save to CSV", command=self.save_to_csv, state=tk.DISABLED)
        self.save_button.pack(side=tk.LEFT, padx=5)

        # Table
        self.tree = ttk.Treeview(self.root, columns=[], show='headings')
        self.tree.grid(row=1, column=0, sticky='nsew')

        # Scrollbars
        self.vsb = ttk.Scrollbar(self.root, orient="vertical", command=self.tree.yview)
        self.vsb.grid(row=1, column=1, sticky='ns')
        self.tree.configure(yscrollcommand=self.vsb.set)
        
        self.hsb = ttk.Scrollbar(self.root, orient="horizontal", command=self.tree.xview)
        self.hsb.grid(row=2, column=0, sticky='ew')
        self.tree.configure(xscrollcommand=self.hsb.set)

        # Configure row and column weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)

    def fetch_data(self):
        try:
            # OPC-UA Client Setup
            url = "opc.tcp://192.168.0.1:4840"
            self.client = Client(url)
            self.client.connect()
            print("Connected to OPC-UA server")
            
            # Variables to fetch
            variables = [
                "index",
                "n",
                "M",
                "Pmech",
                "I",
                "U",
                "Pauf",
                "eta",
                "Temperatur",
                "I_R_mess",
                "U_R_mess"
            ]
            
            # Fetch Data
            self.data = self.fetch_data_for_variables(variables)
            
            # Display Data
            self.display_data()
            self.save_button.config(state=tk.NORMAL)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch data: {str(e)}")
        finally:
            if self.client:
                self.client.disconnect()
                print("Disconnected from OPC-UA server")
    
    def fetch_data_for_variables(self, variables):
        data = {variable: [] for variable in variables}
        
        for variable in variables:
            node_id = f"ns=3;s=\"Messwerte_DB\".\"{variable}\""
            node = self.client.get_node(node_id)
            array_data = self.get_array_from_node(node)
            data[variable] = array_data
        
        max_length = max(len(arr) for arr in data.values())
        
        for key in data:
            data[key].extend([0] * (max_length - len(data[key])))
        
        return data

    def get_array_from_node(self, node):
        value, _ = self.get_node_data(node)
        if isinstance(value, (list, tuple)):
            return value
        else:
            return []
    
    def get_node_data(self, node):
        value = node.get_value()
        datatype = node.get_attribute(ua.AttributeIds.DataType).Value
        return value, datatype

    def display_data(self):
        # Clear the table
        self.tree.delete(*self.tree.get_children())
        
        # Setup columns
        columns = list(self.data.keys())
        self.tree["columns"] = columns
        for col in columns:
            self.tree.heading(col, text=col)
        
        # Populate rows
        for i in range(len(self.data[columns[0]])):
            row_data = [self.data[col][i] for col in columns]
            if any(val != 0 for val in row_data):  # Filter out rows where all values are zero
                self.tree.insert("", "end", values=row_data)

    def save_to_csv(self):
        if self.data:
            try:
                df = pd.DataFrame(self.data)
                # Remove rows where all values are zero
                df = df.loc[~(df == 0).all(axis=1)]
                file_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                                       filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
                if file_path:
                    df.to_csv(file_path, index=False)
                    messagebox.showinfo("Success", "Data successfully saved to CSV.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save data: {str(e)}")
        else:
            messagebox.showwarning("No Data", "No data to save.")

def main():
    root = tk.Tk()
    app = OPCUAGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
