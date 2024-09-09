# TestbenchManager

This project provides a graphical user interface (GUI) for managing the operation of a test bench used for electrical machine testing. It allows the user to create and upload operating points, perform tests, and save measurement data.

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
- [Programs Description](#programs-description)

## Overview

This application provides a user-friendly interface to interact with the test bench, helping to:
- Create operating points for testing.
- Upload operating points to the PLC (SPS).
- Perform tests and retrieve measurement data from the PLC.
- Save the results in CSV format.

## Features

- **Generate and Display Operating Points**: Generate a table of operating points based on user inputs for speed, torque, and torque limitations at specific speeds.
- **CSV Upload**: Connect to the PLC and upload a list of operating points for the test bench to execute.
- **Measurement Data Retrieval**: After the test is complete, read the measurement data logged by the PLC and save it as a CSV file.
- **Customizable Settings**: Save and load default operating parameters from a `default_values.csv` file to streamline the setup process.

## Project Structure

The repository contains the following key files:

- `main.py`: The entry point for the GUI.
- `uploadCSV.py`: Handles the uploading of operating points to the PLC.
- `arbeitspunkte.py`: Generates operating points for testing.
- `Messdaten_auslesen.py`: Reads and saves measurement data from the PLC.
- `default_values.csv`: A CSV file storing default settings such as speed, torque, and limits.

## Installation

### Prerequisites

Make sure you have the following installed:
- Python 3.x
- Required Python libraries: `tkinter`, `pandas`

### Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/TestbenchManager.git
   cd TestbenchManager
Install required Python libraries:

bash

    pip install pandas
    
### Option 2: Windows Executable

Alternatively, you can download the pre-built Windows executable version of the application. This version does not require Python to be installed.

1. Download the executable from [here](https://github.com/y0cky/TestbenchManager/releases/).

2. Double-click the `main.exe` file to launch the application.

## Usage

    Run the main.py file to launch the GUI:

    bash

    python main.py

    From the main window, you can choose to:
        Create Operating Points: Generate a table of operating points based on your specified ranges for speed, torque, and torque limitations.
        Upload Operating Points: Connect to the PLC and upload the operating points.
        Retrieve Measurement Data: Fetch measurement data after the test and save it as a CSV file.

    The application will automatically load default values from default_values.csv. If the file is missing, it will be created with default values upon the first run.

## Programs Description
### 1. main.py

The main GUI that integrates all functionalities. It allows the user to:

    Generate and view operating points in a table format.
    Save the table and a sorted list as CSV.
    Upload the generated operating points to the PLC.
    Retrieve and save measurement data.

### 2. uploadCSV.py

Uploads a list of operating points to the PLC (SPS) via OPC-UA for test execution on the test bench.

### 3. arbeitspunkte.py

Generates a list of operating points for characteristic curve testing, which can be viewed and saved as a CSV.

### 4. Messdaten_auslesen.py

Reads and saves measurement data logged by the PLC after testing is complete.
