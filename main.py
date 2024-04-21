import csv
import threading
import tkinter as tk
from datetime import datetime
from tkinter import filedialog

import pandas as pd
import serial.tools.list_ports
import customtkinter
import serial
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("blue")

app = customtkinter.CTk()
app.title("ESSA Launch Control System")
app.geometry("1500x1500")

writing_data = 0
dark_mode = "dark"
colour_mode = "blue"
status_of_connection = 0
arduino_serial = 0
list_of_data = []

def interface():
    for widget in app.winfo_children():
        widget.destroy()
    button1 = customtkinter.CTkButton(master=app, text="IMPORT DATA", command=import_data)
    button2 = customtkinter.CTkButton(master=app, text="CONTROL CENTRE", command=lambda: start_serial_reading(arduino_serial))
    button3 = customtkinter.CTkButton(master=app, text="SETTINGS", command=settings)
    button4 = customtkinter.CTkButton(master=app, text="CONNECT ARDUINO", command=lambda: connect_arduino(status_of_connection))
    button1.place(relx=0.5, rely=0.2, anchor=tk.CENTER)
    button2.place(relx=0.5, rely=0.4, anchor=tk.CENTER)
    button3.place(relx=0.5, rely=0.6, anchor=tk.CENTER)
    button4.place(relx=0.5, rely=0.8, anchor=tk.CENTER)

def import_data():
    try:
        file_path = filedialog.askopenfilename(title="Select CSV file", filetypes=[("CSV files", "*.csv")])
        if not file_path:
            return

        data_list = pd.read_csv(file_path, encoding='utf-8')
        draw_chart(data_list)
    except Exception as e:
        print(f"Error importing data: {e}")

def start_serial_reading(serial_inst):
    thread = threading.Thread(target=control_centre, args=(serial_inst,), daemon=True)
    thread.start()

def control_centre(serial_inst):
    c = 0
    actual_date = datetime.now().strftime('%Y-%m-%d_%H-%M')
    file_name = f'data_{actual_date}.csv'

#rssi, temp, cisnienie, swiatlo %, wilgotnosc, lat, long
    try:
        while True:
            if serial_inst.in_waiting:
                packet = serial_inst.readline()
                data = packet.decode('utf').rstrip('\n')
                print(data)

                elements = data.split()
                numeric_data = [element for element in elements]
                numeric_data[2] = float(numeric_data[2])
                #altitude = 4330*(1-pow(((numeric_data[2]/100)/1013),0.1903))
                altitude = (1 - pow(((float(numeric_data[2])/100)/979.5),0.1903)) * 4330
                numeric_data.append(altitude)
                list_of_data.append(numeric_data)
                if writing_data == 1:
                    with open(file_name, 'a', newline='') as csv_file:
                        writer = csv.writer(csv_file)

                        if csv_file.tell() == 0:
                            writer.writerow(['RSSI', 'Temperature', 'Pressure', 'Light Value', 'Humidity', 'Latitude', 'Longitude'])

                        writer.writerow(numeric_data)
                if c == 0:
                    draw_chart2(list_of_data, c)
                else:
                    c = 1
                    draw_chart2(list_of_data, c)

    except KeyboardInterrupt:
        print("END")
    finally:
        if serial_inst:
            serial_inst.close()

def draw_chart(data_list):
    for widget in app.winfo_children():
        widget.destroy()

    if len(data_list) > 100:
        data_list = data_list[-100:]

    figure = Figure(figsize=(30, 20), dpi=100)

    ax1 = figure.add_subplot(2, 2, 1)
    ax1.plot(data_list['Temperature'], linestyle='-')
    ax1.set_xlabel('')
    ax1.set_ylabel('Temperature')
    ax1.set_title('Temperature')

    ax2 = figure.add_subplot(2, 2, 2)
    ax2.plot(data_list['Pressure'], linestyle='-')
    ax2.set_xlabel('')
    ax2.set_ylabel('Pressure')
    ax2.set_title('Pressure')

    ax3 = figure.add_subplot(2, 2, 3)
    ax3.plot(data_list['Light Value'], linestyle='-')
    ax3.set_xlabel('')
    ax3.set_ylabel('Light Value')
    ax3.set_title('Light Value')

    ax4 = figure.add_subplot(2, 2, 4)
    ax4.plot(data_list['Humidity'], linestyle='-')
    ax4.set_xlabel('')
    ax4.set_ylabel('Humidity')
    ax4.set_title('Humidity')

    canvas = FigureCanvasTkAgg(figure, master=app)
    canvas.get_tk_widget().pack()


import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import customtkinter  # Assuming this is a custom module used for labeling
from datetime import datetime


import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk

def draw_chart2(data_list, n):

    if not hasattr(draw_chart2, 'figure'):
        draw_chart2.figure = Figure(figsize=(30, 20), dpi=100)
        draw_chart2.ax1 = draw_chart2.figure.add_subplot(2, 2, 1)
        draw_chart2.ax2 = draw_chart2.figure.add_subplot(2, 2, 2)
        draw_chart2.ax3 = draw_chart2.figure.add_subplot(2, 2, 3)
        draw_chart2.ax4 = draw_chart2.figure.add_subplot(2, 2, 4)

        draw_chart2.ax1.set_title('Temperature')
        draw_chart2.ax2.set_title('Pressure')
        draw_chart2.ax3.set_title('Light Value')
        draw_chart2.ax4.set_title('Altitude')

        canvas = FigureCanvasTkAgg(draw_chart2.figure, master=app)
        canvas.get_tk_widget().pack()

    for ax in [draw_chart2.ax1, draw_chart2.ax2, draw_chart2.ax3, draw_chart2.ax4]:
        ax.clear()

    if len(data_list) > 100:
        data_list = data_list[-100:]

    draw_chart2.ax1.plot([row[1] for row in data_list], linestyle='-')
    draw_chart2.ax2.plot([row[2] for row in data_list], linestyle='-')
    draw_chart2.ax3.plot([row[3] for row in data_list], linestyle='-')
    draw_chart2.ax4.plot([row[7] for row in data_list], linestyle='-')



    draw_chart2.ax1.set_xlabel('')
    draw_chart2.ax2.set_xlabel('')
    draw_chart2.ax3.set_xlabel('')
    draw_chart2.ax4.set_xlabel('')

    draw_chart2.ax1.set_ylabel('Temperature')
    draw_chart2.ax2.set_ylabel('Pressure')
    draw_chart2.ax3.set_ylabel('Light Value')
    draw_chart2.ax4.set_ylabel('Altitude')


    current_values = data_list[-1]
    subtitle1 = customtkinter.CTkLabel(master=app, text="Temperature: " + current_values[1])
    subtitle2 = customtkinter.CTkLabel(master=app, text="Pressure: " + str(current_values[2]))
    subtitle3 = customtkinter.CTkLabel(master=app, text="Light Value: " + current_values[3])
    subtitle4 = customtkinter.CTkLabel(master=app, text="Altitude: " + str(current_values[7]))
    subtitle5 = customtkinter.CTkLabel(master=app, text=("RSSI: " + current_values[0]))
    subtitle6 = customtkinter.CTkLabel(master=app, text=("Latitude: " + current_values[5]))
    subtitle7 = customtkinter.CTkLabel(master=app, text=("Longitude: " + current_values[6]))

    subtitle1.place(relx=0.3, rely=0.1, anchor=tk.CENTER)
    subtitle2.place(relx=0.75, rely=0.1, anchor=tk.CENTER)
    subtitle3.place(relx=0.3, rely=0.52, anchor=tk.CENTER)
    subtitle4.place(relx=0.75, rely=0.52, anchor=tk.CENTER)
    subtitle5.place(relx=0.05, rely=0.05, anchor=tk.CENTER)
    subtitle6.place(relx=0.05, rely=0.15, anchor=tk.CENTER)
    subtitle7.place(relx=0.05, rely=0.25, anchor=tk.CENTER)

    n = 1
    draw_chart2.figure.canvas.draw()
    draw_chart2.figure.canvas.flush_events()

def settings():
    for widget in app.winfo_children():
        widget.destroy()
    button1 = customtkinter.CTkButton(master=app, text="DARK/LIGHT MODE", command=change_dark_mode)
    button2 = customtkinter.CTkButton(master=app, text="COLOUR MODE", command=change_colour_mode)
    if writing_data == 1:
        button3 = customtkinter.CTkButton(master=app, text="TURN OFF WRITING DATA", command=change_writing_data)
    else:
        button3 = customtkinter.CTkButton(master=app, text="TURN ON WRITING DATA", command=change_writing_data)
    button4 = customtkinter.CTkButton(master=app, text="BACK", command=interface)

    button1.place(relx=0.5, rely=0.2, anchor=tk.CENTER)
    button2.place(relx=0.5, rely=0.4, anchor=tk.CENTER)
    button3.place(relx=0.5, rely=0.6, anchor=tk.CENTER)
    button4.place(relx=0.5, rely=0.8, anchor=tk.CENTER)

def change_writing_data():
    global writing_data
    writing_data = 1 if writing_data == 0 else 0
    settings()

def change_dark_mode():
    global dark_mode
    if dark_mode == "dark":
        customtkinter.set_appearance_mode("light")
        dark_mode = "light"
    else:
        customtkinter.set_appearance_mode("dark")
        dark_mode = "dark"

def change_colour_mode():
    global colour_mode
    if colour_mode == "blue":
        customtkinter.set_default_color_theme("dark-blue")
        colour_mode = "dark-blue"
        settings()
    elif colour_mode == "dark-blue":
        customtkinter.set_default_color_theme("green")
        colour_mode = "green"
        settings()
    else:
        customtkinter.set_default_color_theme("blue")
        colour_mode = "blue"
        settings()

def connect_arduino(status):
    global status_of_connection
    for widget in app.winfo_children():
        widget.destroy()
    if status == 0:
        subtitle1 = customtkinter.CTkLabel(master=app, text="Enter the port id")
    elif status == 1:
        status_of_connection = 1
        subtitle1 = customtkinter.CTkLabel(master=app, text="Successfully connected")
    else:
        subtitle1 = customtkinter.CTkLabel(master=app, text="Connection failed. Try again")
        status_of_connection = 2
    input1 = customtkinter.CTkEntry(master=app)
    button1 = customtkinter.CTkButton(master=app, text="CONNECT", command=lambda: connect_to_arduino(input1.get()))
    button2 = customtkinter.CTkButton(master=app, text="BACK", command=lambda: interface())
    subtitle1.place(relx=0.5, rely=0.3, anchor=tk.CENTER)
    input1.place(relx=0.5, rely=0.4, anchor=tk.CENTER)
    button1.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
    button2.place(relx=0.5, rely=0.7, anchor=tk.CENTER)

def connect_to_arduino(port_name):
    global arduino_serial
    try:
        serial_inst = serial.Serial(port_name, baudrate=9600, timeout=1)
        connect_arduino(1)
        arduino_serial = serial_inst
    except Exception as e:
        print(f"Error connecting to Arduino on port {port_name}: {e}")
        connect_arduino(2)

interface()
app.mainloop()
