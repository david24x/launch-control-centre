import threading
import tkinter
import serial.tools.list_ports
import customtkinter
import serial
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("blue")

app = customtkinter.CTk()

app.title("ESSA Control Centre")
app.geometry("500x500")

def interface():
    for widget in app.winfo_children():
        widget.destroy()
    button1 = customtkinter.CTkButton(master=app, text="IMPORT DATA", command=import_data)
    button2 = customtkinter.CTkButton(master=app, text="CONTROL CENTRE", command=lambda:start_serial_reading(arduino_serial))
    button3 = customtkinter.CTkButton(master=app, text="SETTINGS", command=settings)
    button4 = customtkinter.CTkButton(master=app, text="CONNECT ARDUINO", command=lambda:connect_arduino(status_of_connection))
    button1.place(relx=0.5, rely=0.2, anchor=tkinter.CENTER)
    button2.place(relx=0.5, rely=0.4, anchor=tkinter.CENTER)
    button3.place(relx=0.5, rely=0.6, anchor=tkinter.CENTER)
    button4.place(relx=0.5, rely=0.8, anchor=tkinter.CENTER)


def import_data():
    print("import_data")

def start_serial_reading(serial_inst):
    thread = threading.Thread(target=control_centre, args=(serial_inst,), daemon=True)
    thread.start()

def control_centre(serial_inst):
    print("control centre")
    temperature = [0, 0]
    try:
        while True:
            if serial_inst.in_waiting:
                packet = serial_inst.readline()
                data = packet.decode('utf').rstrip('\n')
                print(data)
                temperature.append(float(data))
                draw_chart(temperature)



    except KeyboardInterrupt:
        print("Program terminated by user.")
    finally:
        if serial_inst:
            # Zamknij połączenie z portem szeregowym przed zakończeniem programu
            serial_inst.close()

def draw_chart(data):
    for widget in app.winfo_children():
        widget.destroy()
    figure = Figure(figsize=(5, 4), dpi=100)
    ax = figure.add_subplot(1, 1, 1)
    ax.plot(data, marker='o', linestyle='-')
    ax.set_xlabel('Index')
    ax.set_ylabel('Values')
    ax.set_title('Temperature')

    canvas = FigureCanvasTkAgg(figure, master=app)
    canvas.get_tk_widget().pack()

def settings():
    for widget in app.winfo_children():
        widget.destroy()
    button1 = customtkinter.CTkButton(master=app, text="DARK/LIGHT MODE", command=change_dark_mode)
    button2 = customtkinter.CTkButton(master=app, text="COLOUR MODE", command=change_colour_mode)
    button3 = customtkinter.CTkButton(master=app, text="BACK", command=interface)

    button1.place(relx=0.5, rely=0.2, anchor=tkinter.CENTER)
    button2.place(relx=0.5, rely=0.4, anchor=tkinter.CENTER)
    button3.place(relx=0.5, rely=0.6, anchor=tkinter.CENTER)

dark_mode = "dark"
def change_dark_mode():
    global dark_mode
    if dark_mode == "dark":
        customtkinter.set_appearance_mode("light")
        dark_mode = "light"
    else:
        customtkinter.set_appearance_mode("dark")
        dark_mode = "dark"
status_of_connection = 0
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
    button1 = customtkinter.CTkButton(master=app, text="CONNECT", command=lambda:connect_to_arduino(input1.get()))
    button2 = customtkinter.CTkButton(master=app, text="BACK", command=lambda:interface())
    subtitle1.place(relx=0.5, rely=0.3, anchor=tkinter.CENTER)
    input1.place(relx=0.5, rely=0.4, anchor=tkinter.CENTER)
    button1.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)
    button2.place(relx=0.5, rely=0.7, anchor=tkinter.CENTER)

arduino_serial = 0
def connect_to_arduino(port_name):
    global arduino_serial
    try:
        # Inicjalizacja połączenia z portem szeregowym
        serial_inst = serial.Serial(port_name, baudrate=9600, timeout=1)
        connect_arduino(1)
        arduino_serial = serial_inst
    except Exception as e:
        print(f"Error connecting to Arduino on port {port_name}: {e}")
        connect_arduino(2)

colour_mode = "blue"
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

interface()
app.mainloop()
