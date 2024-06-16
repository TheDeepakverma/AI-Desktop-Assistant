import speech_recognition as sr
import pyttsx3
import webbrowser
import subprocess
from datetime import datetime
import requests
import screen_brightness_control as sbc
from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume
import threading
import time
import os

recognizer = sr.Recognizer()
engine = pyttsx3.init()

# Global variable to store alarm time
alarm_time = None
alarm_thread = None

def speak(text):
    engine.say(text)
    engine.runAndWait()

def listen():
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source, duration=0)  # Adjust for ambient noise
        recognizer.pause_threshold = 0.5  # Pause threshold for faster recognition
        audio = recognizer.listen(source, timeout=10, phrase_time_limit=10)  # Timeout and phrase time limit
        
        try:
            print("Recognizing...")
            query = recognizer.recognize_google(audio, language='en-in')
            print(f"User said: {query}")
        except sr.UnknownValueError:
            print("Sorry, I did not catch that. Please try again.")
            return "None"
        except sr.RequestError:
            print("Could not request results; check your network connection.")
            return "None"
        
    return query

def handle_command(query):
    query = query.lower()

    if 'hello' in query:
        speak("Hello! How can I assist you?")
    
    elif 'your name' in query:
        speak("I am your AI Desktop Assistant.")
    
    elif 'time' in query:
        now = datetime.now().strftime("%H:%M:%S")
        speak(f"The current time is {now}")
    
    elif 'open calculator' in query:
        speak("Opening Calculator")
        subprocess.Popen(['calc.exe'])
    
    elif 'open chrome' in query:
        speak("Opening Google Chrome")
        webbrowser.get("chrome").open("http://www.google.com")
    
    elif 'open notepad' in query:
        speak("Opening Notepad")
        subprocess.Popen(['notepad.exe'])
    
    elif 'search' in query:
        speak("What do you want to search for?")
        print("What do you want to search for?")
        search_query = listen()
        if search_query != "None":
            speak(f"Searching for {search_query}")
            print(f"Searching for {search_query}")
            webbrowser.open(f"https://www.google.com/search?q={search_query}")
    
    elif 'weather' in query:
        speak("Please tell me the city name.")
        print("Please tell me the city name.")
        city = listen()
        if city != "None":
            get_weather(city)
    
    elif 'news' in query:
        speak("Fetching the latest news")
        get_news()

    elif 'set volume' in query:
        try:
            volume_level = int(query.split("set volume to")[-1].strip().replace("%", ""))
            sessions = AudioUtilities.GetAllSessions()
            for session in sessions:
                volume = session._ctl.QueryInterface(ISimpleAudioVolume)
                volume.SetMasterVolume(volume_level / 100.0, None)
            speak(f"Volume set to {volume_level} percent")
        except Exception as e:
            speak("Sorry, I could not set the volume")
            print(e)

    elif 'set brightness' in query:
        try:
            brightness_level = int(query.split("set brightness to")[-1].strip().replace("%", ""))
            sbc.set_brightness(brightness_level)
            speak(f"Brightness set to {brightness_level} percent")
        except Exception as e:
            speak("Sorry, I could not set the brightness")
            print(e)
    
    elif 'increase volume' in query:
        sessions = AudioUtilities.GetAllSessions()
        for session in sessions:
            volume = session._ctl.QueryInterface(ISimpleAudioVolume)
            current_volume = volume.GetMasterVolume()
            volume.SetMasterVolume(min(current_volume + 0.1, 1.0), None)
        speak("Volume increased")

    elif 'decrease volume' in query:
        sessions = AudioUtilities.GetAllSessions()
        for session in sessions:
            volume = session._ctl.QueryInterface(ISimpleAudioVolume)
            current_volume = volume.GetMasterVolume()
            volume.SetMasterVolume(max(current_volume - 0.1, 0.0), None)
        speak("Volume decreased")

    elif 'increase brightness' in query:
        current_brightness = sbc.get_brightness(display=0)
        new_brightness = min(current_brightness + 10, 100)
        sbc.set_brightness(new_brightness)
        speak("Brightness increased")

    elif 'decrease brightness' in query:
        current_brightness = sbc.get_brightness(display=0)
        new_brightness = max(current_brightness - 10, 0)
        sbc.set_brightness(new_brightness)
        speak("Brightness decreased")

    elif 'set alarm' in query:
        alarm_time_str = query.split("for")[-1].strip()
        set_alarm(alarm_time_str)

    elif 'check alarm' in query:
        if alarm_time:
            alarm_time_str = alarm_time.strftime("%H:%M")
            print(f"Alarm is set for {alarm_time_str}")
            speak(f"Alarm is set for {alarm_time_str}")

    elif 'open gmail' in query:
        speak("Opening Gmail")
        webbrowser.open("https://mail.google.com")

    else:
        speak("I am not sure how to help with that.")

def set_alarm(alarm_time_str):
    global alarm_time, alarm_thread
    
    # Convert alarm time string to datetime object
    try:
        alarm_time = datetime.strptime(alarm_time_str, "%H:%M").time()
        speak(f"Alarm set for {alarm_time_str}")
        print(f"Alarm set for {alarm_time_str}")
        
        # Start a new thread to check the alarm
        if alarm_thread is None or not alarm_thread.is_alive():
            alarm_thread = threading.Thread(target=check_alarm)
            alarm_thread.start()
    except ValueError:
        speak("Sorry, I couldn't understand the time format. Please use HH:MM format.")
        print("Sorry, I couldn't understand the time format. Please use HH:MM format.")

def check_alarm():
    global alarm_time
    while alarm_time:
        now = datetime.now().time()
        if now.hour == alarm_time.hour and now.minute == alarm_time.minute:
            speak("Alarm ringing!")
            print("Alarm ringing!")
            alarm_time = None  # Reset alarm
        time.sleep(30)  # Check every 30 seconds

def get_weather(city):
    api_key = "1dcc631d2b793e6e36aa2c67d5041c55"  # OpenWeatherMap API key
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    complete_url = base_url + "appid=" + api_key + "&q=" + city
    response = requests.get(complete_url)
    data = response.json()
    if data["cod"] != "404":
        main = data["main"]
        weather = data["weather"]
        temperature = main["temp"]
        pressure = main["pressure"]
        humidity = main["humidity"]
        weather_description = weather[0]["description"]
        location = data["name"]
        country = data["sys"]["country"]
        weather_report = (
            f"The temperature in {location}, {country} is {temperature - 273.15:.2f} degrees Celsius with {weather_description}. "
            f"The atmospheric pressure is {pressure} hPa and the humidity is {humidity}%."
        )
        speak(weather_report)
        print(weather_report)
    else:
        speak("City not found.")
        print("City not found.")

def get_news():
    api_key = "7e900670424f4ed6990783eb36e081ef"  # NewsAPI key
    url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={api_key}"
    response = requests.get(url)
    data = response.json()
    if data["status"] == "ok":
        articles = data["articles"]
        for i, article in enumerate(articles[:5]):
            news_item = f"News {i+1}: {article['title']}"
            speak(news_item)
            print(news_item)
    else:
        speak("Unable to fetch news at the moment.")
        print("Unable to fetch news at the moment.")
