import requests
import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import time

# Constants
API_KEY = "369fdb84b6aa3f07f5a2684ccf78453c"
ICON_URL = "http://openweathermap.org/img/wn/{}@2x.png"
FORECAST_URL = "http://api.openweathermap.org/data/2.5/forecast"

# Error messages
ERROR_MESSAGES = {
    "input_error": "Incorrect City name.Please try again",
    "coord_error": "Error fetching coordinates: ",
    "weather_error": "Error fetching weather data: ",
    "forecast_error": "Error fetching forecast data: "
}

# Create root window
root = tk.Tk()
root.title("Weather Forecast App by Oshada Rashmika")
root.geometry("800x600")
root.configure(bg='#2c3e50')

# Loading the fonts
root.option_add("*Font", "Sansation 12")

# Create a style for ttk widgets
style = ttk.Style()
style.theme_use('clam')
style.configure("TButton",
                background="#e74c3e",
                foreground="white",
                font=("Sansation", 14, "bold"),
                padding=10)
style.map("TButton", background=[('active', '#c0392b')])
style.configure("TLabel", background="#2c3e50", foreground="white", font=("Sansation", 12))
style.configure("TEntry", fieldbackground='white', foreground='black', font=("Sansation", 12))

def get_coords(city):
    """Fetch latitude and longitude from OpenWeatherMap's Geocoding API."""
    geocode_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}"
    response = requests.get(geocode_url)
    
    if response.status_code == 200:
        data = response.json()
        return data['coord']['lat'], data['coord']['lon']
    else:
        raise Exception(ERROR_MESSAGES["coord_error"] + response.json().get('message', ''))

def get_weather_data(lat, lon, units):
    """Fetch the weather data from OpenWeatherMap API using latitude and longitude."""
    weather_url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units={units}"
    response = requests.get(weather_url)
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(ERROR_MESSAGES["weather_error"] + response.json().get('message', ''))

def get_forecast_data(lat, lon, units):
    """Fetch the weather forecast data from OpenWeatherMap API."""
    response = requests.get(f"{FORECAST_URL}?lat={lat}&lon={lon}&appid={API_KEY}&units={units}")
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(ERROR_MESSAGES["forecast_error"] + response.json().get('message', ''))

def show_loading():
    """Show loading animation during data fetching."""
    loading_label.pack(pady=5)
    loading_label.after(1000, animate_loading)

def animate_loading():
    """Animate the loading message."""
    loading_label.config(text=loading_label.cget("text") + ".")
    if len(loading_label.cget("text")) < 10: 
        loading_label.after(500, animate_loading)

def update_weather():
    """Update weather based on user input."""
    city = city_entry.get().strip()
    if not city:
        messagebox.showwarning("Input Error", ERROR_MESSAGES["input_error"])
        return

    show_loading()
    root.update()

    try:
        lat, lon = get_coords(city)
        weather_data = get_weather_data(lat, lon, unit_var.get())
        forecast_data = get_forecast_data(lat, lon, unit_var.get())
        display_weather(weather_data, forecast_data)
    except Exception as e:
        messagebox.showerror("Error", str(e))
    finally:
        loading_label.pack_forget()

def display_weather(data, forecast):
    """Display the weather information in the GUI."""
    city_name = f"{data['name']}, {data['sys']['country']}"
    temperature = f"{data['main']['temp']}°{'C' if unit_var.get() == 'metric' else 'F'}"
    weather_description = data['weather'][0]['description'].capitalize()
    humidity = f"Humidity: {data['main']['humidity']}%"
    wind_speed = f"Wind Speed: {data['wind']['speed']} {'m/s' if unit_var.get() == 'metric' else 'mph'}"
    sunrise_time = time.strftime('%I:%M %p', time.localtime(data['sys']['sunrise']))
    sunset_time = time.strftime('%I:%M %p', time.localtime(data['sys']['sunset']))

    city_label.config(text=city_name)
    temp_label.config(text=temperature)
    desc_label.config(text=weather_description)
    humidity_label.config(text=humidity)
    wind_label.config(text=wind_speed)
    sunrise_label.config(text=f"Sunrise: {sunrise_time}")
    sunset_label.config(text=f"Sunset: {sunset_time}")

    # Load and display weather icon
    icon_code = data['weather'][0]['icon']
    icon_url = ICON_URL.format(icon_code)
    img = Image.open(requests.get(icon_url, stream=True).raw)
    img = img.resize((100, 100), Image.LANCZOS)
    img_tk = ImageTk.PhotoImage(img)

    icon_label.config(image=img_tk)
    icon_label.image = img_tk

    # Change background color based on weather condition
    if "rain" in weather_description.lower():
        root.configure(bg='#3498db')  # Light blue for rain
    elif "clear" in weather_description.lower():
        root.configure(bg='#f39c12')  # Orange for clear
    else:
        root.configure(bg='#2c3e50')  # Default dark background

    # Clear previous forecast
    for widget in forecast_frame.winfo_children():
        widget.destroy()

    # Display the forecast
    for day in forecast['list']:
        if '12:00:00' in day['dt_txt']:  # Only take the forecast at noon
            date_time = day['dt_txt']
            date = date_time.split()[0]  # Get the date part
            temp = f"{day['main']['temp']}°{'C' if unit_var.get() == 'metric' else 'F'}"
            description = day['weather'][0]['description'].capitalize()

            # Style the forecast label
            forecast_label = ttk.Label(forecast_frame, text=f"{date}: {temp}, {description}",
                                       font=("Sansation", 10), background='#2c3e50')
            forecast_label.pack(fill=tk.X, padx=20, pady=2)  # Reduced padding

def reset_fields():
    """Reset input fields and weather display."""
    city_entry.delete(0, tk.END)
    city_label.config(text="")
    temp_label.config(text="")
    desc_label.config(text="")
    humidity_label.config(text="")
    wind_label.config(text="")
    sunrise_label.config(text="")
    sunset_label.config(text="")
    icon_label.config(image='')

    # Clear forecast
    for widget in forecast_frame.winfo_children():
        widget.destroy()

# Set up the GUI components
# City input
input_frame = tk.Frame(root, bg='#2c3e50')
input_frame.pack(pady=10)

city_label = ttk.Label(input_frame, text="Enter City Name:", background='#2c3e50')
city_label.pack(side=tk.LEFT, padx=5)

city_entry = ttk.Entry(input_frame, width=30)
city_entry.pack(side=tk.LEFT, padx=5)

# Unit selection
unit_var = tk.StringVar(value='metric')
metric_radio = ttk.Radiobutton(root, text='Celsius (Metric)', variable=unit_var, value='metric')
imperial_radio = ttk.Radiobutton(root, text='Fahrenheit (Imperial)', variable=unit_var, value='imperial')
metric_radio.pack(pady=5)
imperial_radio.pack(pady=5)

# Create a frame for weather and forecast
main_frame = tk.Frame(root, bg='#2c3e50')
main_frame.pack(pady=10, fill=tk.BOTH, expand=True)

# Grid layout for centering the frames
main_frame.grid_rowconfigure(0, weight=1)
main_frame.grid_columnconfigure(0, weight=1)
main_frame.grid_columnconfigure(1, weight=1)

# Current weather frame
weather_frame = tk.Frame(main_frame, bg='#2c3e50')
weather_frame.grid(row=0, column=0, padx=5, pady=5)

city_label = ttk.Label(weather_frame, text="", font=("Sansation", 16, "bold"), background='#2c3e50')
city_label.pack(pady=5)

temp_label = ttk.Label(weather_frame, text="", font=("Sansation", 32, "bold"), background='#2c3e50')
temp_label.pack(pady=5)

desc_label = ttk.Label(weather_frame, text="", font=("Sansation", 12), background='#2c3e50')
desc_label.pack(pady=5)

humidity_label = ttk.Label(weather_frame, text="", font=("Sansation", 12), background='#2c3e50')
humidity_label.pack(pady=5)

wind_label = ttk.Label(weather_frame, text="", font=("Sansation", 12), background='#2c3e50')
wind_label.pack(pady=5)

sunrise_label = ttk.Label(weather_frame, text="", font=("Sansation", 12), background='#2c3e50')
sunrise_label.pack(pady=5)

sunset_label = ttk.Label(weather_frame, text="", font=("Sansation", 12), background='#2c3e50')
sunset_label.pack(pady=5)

# Icon label
icon_label = ttk.Label(weather_frame, background='#2c3e50')
icon_label.pack(pady=5)

# Forecast frame
forecast_frame = tk.Frame(main_frame, bg='#2c3e50')
forecast_frame.grid(row=0, column=1, padx=5, pady=5)  # Reduced padding

# Button frame
button_frame = tk.Frame(root, bg='#2c3e50')
button_frame.pack(pady=10)

get_weather_btn = ttk.Button(button_frame, text="Get Weather", command=update_weather)
get_weather_btn.pack(side=tk.LEFT, padx=10)

reset_btn = ttk.Button(button_frame, text="Reset", command=reset_fields)
reset_btn.pack(side=tk.LEFT, padx=10)

# Loading label
loading_label = ttk.Label(root, text="", background='#2c3e50')

# Run the application
root.mainloop()
































































