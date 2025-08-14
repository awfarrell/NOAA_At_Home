import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from datetime import datetime
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import json

main_scrollable_frame = tk.Tk()
max_width = 360
max_height = 640
main_scrollable_frame(f"{max_width}x{max_height}")
main_scrollable_frame.title("NOAA At Home")

canvas = tk.Canvas(main_scrollable_frame)
scrollbar = tk.Scrollbar(main_scrollable_frame, orient="vertical", command=canvas.yview)
main_scrollable_frame = tk.Frame(canvas)

main_scrollable_frame.bind
(
    "<Configure>",
    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)

canvas.create_window((0, 0), window=main_scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

DATA_FILE = "weather_data.json"

#==============STORE DATA===============
temperatures = []
humidities = []
dew_points = []
rainfall = []
timestamps = []
pressures = []
cloud_keywords = {}

directions = ["N", "NW", "W", "SW", "S", "SE", "E", "NE"]
direction_vars = {}

speeds = [
    "calm (smoke rises straight up)",
    "light breeze (leaves rustle)",
    "breeze (leaves & twigs move)",
    "moderate breeze (branches & loose paper move)",
    "strong wind (large branches move)",
    "light gale (whole trees sway)",
    "gale (small trees uprooted, shingles missing)",
    "whole gale (extensive damage to trees)",
    "hurricane (extensive damage to trees & structures)",
]
speed_vars = {}

#==============LOADING & SAVING DATA=================

#Save data by month/year. Retrieve data by entering date in new window
#clear all data before launching app
#can use on phone? or just computer? 

def load_data():
    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
            for entry in data:
                try:
                    t = entry.get("temperature")
                    h = entry.get("humidity")
                    ts_str = entry.get("timestamp")
                    r = entry.get("rainfall", 0.0)
                    p = entry.get("pressure", 0.0)
                    
                    if t is None or h is None or ts_str is None:
                        continue
                    
                    temperatures.append(t)
                    humidities.append(h)
                    timestamps.append(datetime.fromisoformat(ts_str))
                    rainfall.append(r)
                    pressures.append(p)
                    dew_points.append(t-((100-h)/5))
                except Exception as e:
                    print("Skipping corrupted entry: ", entry, " Error: ", e)
    except FileNotFoundError:
        pass

def save_data():
    data = [
        {"temperature": t, "humidity": h, "timestamp": ts.isoformat(), "rainfall": r, "pressures": p}
        for t, h, ts, r, p in zip(temperatures, humidities, timestamps, rainfall, pressures)
    ]
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

        
#===========UI CALLBACK===========     
def submit_data():
    try:
        temp = float(temp_entry.get())
        temperatures.append(temp)
        
        humidity = float(humid_entry.get())
        humidities.append(humidity)
        
        dew_point = temp-((100-humidity)/5)
        dew_points.append(dew_point)
        
        rain = float(rain_entry.get())
        rainfall.append(rain)
        
        pressure = float(pressure_entry.get())
        pressures.append(pressure)
        
        cloud_text = cloud_entry.get().strip().lower()
        words = cloud_text.split()
        
        for word in words:
            if word in cloud_keywords:
                cloud_keywords[word] += 1
            else:
                cloud_keywords[word] = 1
                
        wind_directions = [d for d, var in direction_vars.items() if var.get() == 1]
        
        timestamps.append(datetime.now())
        
        save_data()
        show_todays_weather(temp, humidity, dew_point, rain, pressure, cloud_keywords, wind_directions)
        show_averages(temperatures, humidities, dew_points, rainfall, pressures)

        temp_entry.delete(0, tk.END)
        humid_entry.delete(0, tk.END)
        rain_entry.delete(0, tk.END)
        pressure_entry.delete(0, tk.END)
        cloud_entry.delete(0, tk.END)

    except ValueError:
        messagebox.showerror("Invalid input", "Please enter valid numbers.")

#not displaying correctly - fix next time! (Asign the weather label to a variable rather than using the label thingy)

#==========SHOW TODAY'S WEATHER========
def show_todays_weather(temp, humidity, dew_point, rain, pressure, cloud_keywords, wind_directions):
    if temp is not None and humidity is not None and dew_point is not None and rain is not None and pressure is not None:
        today = datetime.now().strftime("%B %d, %Y")
        data_label.config(
            text=f"Data entered successfully!\n\n"
             f"Today's weather ({today}):\n"
             f"Temp: {temp:.1f}°F\n"
             f"Humidity: {humidity:.1f}%\n"
             f"Dew Point: {dew_point}°F\n"
             f"Rainfall: {rain:.1f} in\n"
             f"Pressure: {pressure:.1f} in\n\n")
        predict_weather(cloud_keywords, wind_directions, temp)
        
        
#=========PREDICT WEATHER===========
def predict_weather(cloud_keywords, wind_directions, temp):
    
    now = datetime.now()
    prediction = ""
    
    if "cirrus" in cloud_keywords:
        if temp > 45:
            if any(word in cloud_keywords for word in ["fibratus", "spissatus", "unicus"]):
                if any(direction in wind_directions for direction in ["W", "NW", "N"]):
                    prediction = "Good weather ahead.\n"
                elif any(direction in wind_directions for direction in ["NE", "E", "S"]):
                    prediction = "Precipitation possible within 20-30 hours\n"
        
    elif "altocumulus" in cloud_keywords:
        if "translucidus" in cloud_keywords:
            if any(direction in wind_directions for direction in ["NE", "S"]):
                prediction = "Precipitation likely in 15-20 hours.\n"
            else:
               prediction = "Overcast sky ahead.\n"
        elif "undulatus" in cloud_keywords:
            if any(direction in wind_directions for direction in ["NE", "S"]):
                prediction = "Precipitation likely in 15-20 hours.\n"
            else:
                prediction = "Overcast sky ahead with likely drizzle.\n"
        elif "perlucidus" in cloud_keywords:
            if any(direction in wind_directions for direction in ["NE", "S"]):
                prediction = "Some precipitation likely in 15-20 hours.\n"
            else:
                prediction ="Overcast sky ahead.\n"
                
    elif all(word in cloud_keywords for word in ["altostratus", "translucidus"]):
        if any (direction in wind_directions for direction in ["NE", "S"]):
            prediction = "Precipitation likely in 15-20 hours.\n"
        else:
            prediction = "Overcast sky ahead.\n"
        
    elif all(word in cloud_keywords for word in ["stratocumulus", "stratiformis"]):
        prediction = "Precipitation ahead.\n"
        if temp < 55:
            prediction = "Expect gusty winds & thundershowers.\n"
        else:
            prediction = "\n"
            
    elif "cirrocumulus" in cloud_keywords:
        if any (direction in wind_directions for direction in ["NE", "S"]):
            if (now.month == 6 and now.day >= 1) or \
            (now.month == 7) or \
            (now.month == 8 and now.day <= 31):
                prediction = "Afternoon thundershowers possible.\n"
            else:
                prediction = "Precipitation likely in 15-20 hours.\n"
        else:
            prediction = "Overcast sky ahead.\n"
            
    elif "stratus" in cloud_keywords:
        if any (direction in wind_directions for direction in ["NE", "S"]):
            prediction = "Heavy precipitation ahead. Bring an umbrella.\n"
        else:
            prediction = "Drizzle and/or overcast sky ahead.\n"
            
    elif "cumulus" in cloud_keywords:
        if "humulis" in cloud_keywords:
            prediction = "Fair weather provided clouds don't develop vertically.\n"
        elif "fractus" in cloud_keywords:
            if any (direction in wind_directions for direction in ["NE", "S"]):
                prediction = "Precipitation possible if winds remains steady.\n"
            else:
                prediction = "Good weather ahead.\n"
        elif "congestus" in cloud_keywords:
            if any (direction in wind_directions for direction in ["NW", "SW"]):
                prediction = "Squalls & possible thunderstorms within 5-10 hours.\n"
                
    elif "cirrostratus" in cloud_keywords:
        if any (direction in wind_directions for direction in ["NE", "E", "S"]):
            prediction = "Precipitation within 15-25 hours. "
            if any (direction in wind_directions for direction in ["E", "SE"]):   
                prediction += "(...possibly sooner.)\n"
        else:
            prediction = "Overcast sky ahead.\n"
    
    elif "nimbostratus" in cloud_keywords:
        if any (direction in wind_directions for direction in ["NE", "S"]):
            prediction = "Long period of precipitation predicted.\n"
        elif any (direction in wind_directions for direction in ["SW", "W", "N"]):
            prediction = "Short period of precipitation predicted.\n"
            
            
    elif "cumulonimbus" in cloud_keywords:
        if "mamma" in cloud_keywords:
            prediction = "Severe weather ahead. Take precautions.\n"
        else:
            if any (direction in wind_directions for direction in ["SW", "W", "N"]):
                prediction = "Precipitation likely, and soon. Bring an umbrella.\n"     
        
    else: 
        prediction = "Have a blessed day, ya dingus."

    prediction_label.config(text=prediction)
        

#==========CALCULATE AVGS==========
def show_averages(temperatures_list, humidities_list, dew_points_list, rainfall_list, pressures_list):
    
    global avg_label
    
    if temperatures_list and humidities_list and dew_points_list and rainfall_list and pressures_list:
        avg_temp = sum(temperatures_list)/len(temperatures_list)
        avg_humidity = sum(humidities_list)/len(humidities_list)
        avg_dew_point = sum(dew_points_list)/len(dew_points_list)
        avg_rainfall = sum(rainfall_list)/len(rainfall_list)
        avg_pressure = sum(pressures_list)/len(pressures_list)
        
        avg_label.config(
            text=(
                f"Avg Temp: {avg_temp:.1f}°F\n"
                 f"Avg Humidity: {avg_humidity:.1f}%\n"
                 f"Avg Dew Point: {avg_dew_point:.1f}°F\n"
                 f"Avg Rainfall: {avg_rainfall:.1f} in\n"
                 f"Avg Pressure: {avg_pressure:.1f} in\n"
            ),
        )
    else:
        avg_label.config(text="Function runs....No data yet.")
        
    
#===========OPEN VIEW DATA WINDOW=========

def open_view_data_window():
    view_scrollable_frame = tk.Toplevel(main_scrollable_frame)
    view_scrollable_frame(f"{max_width}x{max_height}")
    view_scrollable_frame.title("NOAA AT HOME - View Past Data")
    
    canvas = tk.Canvas(view_scrollable_frame)
    scrollbar = tk.Scrollbar(view_scrollable_frame, orient="vertical", command=canvas.yview)
    view_scrollable_frame = tk.Frame(canvas)

    view_scrollable_frame.bind
    (
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=view_scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    data_header_label = tk.Label(view_scrollable_frame, text="NOAA AT HOME - View Past Data", font=("Helvetica", 14, "bold"), fg="blue")
    data_header_label.grid(row=0, column=0, columnspan=2, pady=(10, 10))
    
    tk.Label(view_scrollable_frame, text="Start Date (YYYY-MM-DD): ").grid(row=1, column=0)
    start_date = tk.Entry(view_scrollable_frame)
    start_date.grid(row=1, column=1)
    
    tk.Label(view_scrollable_frame, text="End Date (YYYY-MM-DD): ").grid(row=2, column=0)
    end_date = tk.Entry(view_scrollable_frame)
    end_date.grid(row=2, column=1)
    
    tree = ttk.Treeview(view_scrollable_frame, columns=("Date", "Temp", "Humidity", "Dew Point", "Rainfall", "Pressure"), show="headings")
    tree.heading("Date", text="Date")
    tree.heading("Temp", text="Temp (°F)")
    tree.heading("Humidity", text="Humidity (%)")
    tree.heading("Dew Point", text="Dew Point")
    tree.heading("Rainfall", text="Rainfall (in)")
    tree.heading("Pressure", text="Pressure (in)")
    tree.grid(row=3, column=0, columnspan=2, padx=10, pady=10)
    
    def get_filtered_data():
        # Clear previous entries
        for item in tree.get_children():
            tree.delete(item)

        try:
            start = datetime.fromisoformat(start_date.get())
            end = datetime.fromisoformat(end_date.get())
        except ValueError:
            tree.insert("", tk.END, values=("Invalid date format", "", "", "", ""))
            return
        
        dates = []
        temps = []
        hums = []
        dew_pts = []
        rains = []
        press = []

        results = []
        for i, ts in enumerate(timestamps):
            if start <= ts <= end:
                results.append({
                    "timestamp": ts,
                    "temperature": temperatures[i],
                    "dew points": temperatures[i] - ((100 - humidities[i]) / 5),
                    "humidity": humidities[i],
                    "rainfall": rainfall[i],
                    "pressure": pressures[i]
                })

        if not results:
            tree.insert("", tk.END, values=("No data found", "", "", "", ""))
            return

        for entry in results:
            dt = entry['timestamp'].strftime("%Y-%m-%d")
            t = entry['temperature']
            h = entry['humidity']
            dp = entry['dew points']
            r = entry['rainfall']
            p = entry['pressure']
            tree.insert("", tk.END, values=(dt, t, h, dp, r, p))

            dates.append(entry['timestamp'])
            temps.append(t)
            hums.append(h)
            dew_pts.append(dp)
            rains.append(r)
            press.append(p)

        # --- Graph ---
        screen_width = view_scrollable_frame.winfo_screenwidth()
        screen_height = view_scrollable_frame.winfo_screenheight()
        fig_width = screen_width / 100
        fig_height = screen_height/200
        
        fig, ax = plt.subplots(figsize=(fig_width, fig_height), dpi=100)
        
        ax.plot(dates, temps, label="Temp (°F)", marker="o")
        ax.plot(dates, hums, label="Humidity (%)", marker="o")
        ax.plot(dates, dew_pts, label="Dew Point ", marker="o")
        ax.plot(dates, rains, label="Rainfall (in)", marker="o")
        ax.plot(dates, press, label="Pressure (in)", marker="o")
        ax.set_title("Weather Trends")
        ax.set_xlabel("Date")
        ax.set_ylabel("Values")
        ax.legend()
        ax.grid(True)
        fig.autofmt_xdate()

        canvas = FigureCanvasTkAgg(fig, master=view_scrollable_frame)
        canvas.get_tk_widget().grid(row=4, column=0, columnspan=2)
        canvas.draw()
        
        #avg label not displaying correctly in data window (but does display correctly in main window)
        
        avg_label = tk.Label(view_scrollable_frame, text="Period Averages:", font=("Helvetica", 13), fg="blue")
        avg_label.grid(row=50, column=0, columnspan=2, pady=(10, 5))
        show_averages(temps, hums, dew_pts, rains, press)

    tk.Button(view_scrollable_frame, text="View", command=get_filtered_data).grid(row=4, column=0, columnspan=2, pady=5)
              
#=========GUI============

main_header_label = tk.Label(main_scrollable_frame, text="WE HAVE NOAA AT HOME", font=("Helvetica", 16, "bold"), fg="blue")
main_header_label.grid(row=0, column=0, columnspan=2, pady=(10, 5))
main_header_label_2 = tk.Label(main_scrollable_frame, text="~a homemade weather app~", font=("Helvetica", 14, "italic"), fg="blue")
main_header_label_2.grid(row=1, column=0, columnspan=2, pady=(10, 5))

temp_label = tk.Label(main_scrollable_frame, text="Temperature (°F):")
temp_label.grid(row=3, column=0, padx=10, pady=5, sticky="e")
temp_entry = tk.Entry(main_scrollable_frame)
temp_entry.grid(row=3, column=1, padx=10, pady=5)

humid_label = tk.Label(main_scrollable_frame, text="% Humidity:")
humid_label.grid(row=4, column=0, padx=10, pady=5, sticky="e")
humid_entry = tk.Entry(main_scrollable_frame)
humid_entry.grid(row=4, column=1, padx=10, pady=5)

rain_label = tk.Label(main_scrollable_frame, text="Rainfall (in):")
rain_label.grid(row=5, column=0, padx=10, pady=5, sticky="e")
rain_entry = tk.Entry(main_scrollable_frame)
rain_entry.grid(row=5, column=1, padx=10, pady=5)

pressure_label = tk.Label(main_scrollable_frame, text="Barometer Height (in):")
pressure_label.grid(row=6, column=0, padx=10, pady=5, sticky="w")
pressure_entry = tk.Entry(main_scrollable_frame)
pressure_entry.grid(row=6, column=1, padx=10, pady=5)

cloud_label = tk.Label(main_scrollable_frame, text="Clouds: ")
cloud_label.grid(row=7, column=0, padx=10, pady=5, sticky="e")
cloud_entry = tk.Entry(main_scrollable_frame, width=30)
cloud_entry.grid(row=7, column=1, padx=10, pady=5)

for i, d in enumerate(directions):
    var = tk.IntVar() #0 is unchecked, 1 is checked
    wind_direction = tk.Checkbutton(main_scrollable_frame, text=d, variable=var)
    wind_direction.grid(row=8+i, column=0, padx=40, pady=0.5, sticky="w")
    direction_vars[d] = var
    
for i, s in enumerate(speeds):
    var = tk.IntVar() #0 is unchecked, 1 is checked
    wind_speed = tk.Checkbutton(main_scrollable_frame, text=s, variable=var)
    wind_speed.grid(row=8+i, column=1, sticky="w", pady=0.5)
    speed_vars[s] = var

submit_button = tk.Button(main_scrollable_frame, text="Enter Data", command=submit_data)
submit_button.grid(row=20, column=0, columnspan=2, pady=10)

viewPastData_button = tk.Button(main_scrollable_frame, text="View Past Data", command=open_view_data_window)
viewPastData_button.grid(row=21, column=0, columnspan=2, pady=10)

data_label = tk.Label(main_scrollable_frame, text="")
data_label.grid(row=22, column=0, columnspan=2, pady=10)

prediction_label= tk.Label(main_scrollable_frame, text = "")
prediction_label.grid(row=23, column=0, columnspan=2, pady=10)

avg_label = tk.Label(main_scrollable_frame, text="No data yet.", font=("Helvetica", 10, "italic"), fg="blue")
avg_label.grid(row=24, column=0, columnspan=2, pady=10)
      
    

#=========MAIN========
load_data()
main_scrollable_frame.mainloop()