import os
import pyttsx3
import subprocess
import pyautogui
import re
import json
import pyaudio
import time
import struct
from playsound import playsound
import eel
import sqlite3
import webbrowser
import pvporcupine
import pywhatkit as kit
from urllib.parse import quote
from engine.config import ASSISTANT_NAME
from engine.helper import extract_yt_term, remove_words
from hugchat import hugchat
import psutil
import datetime
import random
import requests
import pprint
import wikipedia
import string
# Database connection
con = sqlite3.connect("aurora.db")
cursor = con.cursor()
# Play assistant start sound
@eel.expose
def playAssistantSound():
    music_dir = "www/assets/audio/start_sound.mp3"
    playsound(music_dir)

# Function to open applications and web apps
def openCommand(query):
    query = query.replace(ASSISTANT_NAME, "").replace("open", "").strip().lower()

    web_apps = {
        "telegram": "https://web.telegram.org",
        "linkedin": "https://www.linkedin.com",
        "unstop": "https://unstop.com",
        "instagram": "https://www.instagram.com",
        "facebook": "https://www.facebook.com",
    }

    if query in web_apps:
        from engine.command import speak
        speak(f"Opening {query.capitalize()}")
        webbrowser.open(web_apps[query])
        return

    browsers = {
        "chrome": "C:/Program Files/Google/Chrome/Application/chrome.exe",
        "firefox": "C:/Program Files/Mozilla Firefox/firefox.exe",
        "edge": "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
        "opera": "C:/Program Files/Opera/launcher.exe",
        "brave": "C:/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe",
        "vivaldi": "C:/Program Files/Vivaldi/Application/vivaldi.exe",
    }

    if query in browsers:
        from engine.command import speak
        speak(f"Opening {query.capitalize()}")
        os.startfile(browsers[query])
        return

    if query == "whatsapp":
        from engine.command import speak
        speak("Opening WhatsApp")
        webbrowser.open("https://web.whatsapp.com")
        return
    if query == "notepad++":
        from engine.command import speak
        speak("Opening notepad++")
        webbrowser.open("C:\\ProgramData\\Microsoft\\Windows\\Start Menu\\Programs\\Notepad++.lnk")
        return

    if query == "youtube":
        from engine.command import speak
        speak("Opening YouTube")
        webbrowser.open("https://www.youtube.com")
        return

    from engine.command import speak
    speak("Sorry, I didn't understand the command. Please try again.")

# Function to open specific system applications
def openApp(command):
    if "calculator" in command:
        from engine.command import speak
        speak("Opening Calculator")
        os.startfile('C:\\Windows\\System32\\calc.exe')
    elif "notepad" in command:
        speak("Opening Notepad")
        os.startfile('C:\\Windows\\System32\\notepad.exe')
    elif "paint" in command:
        speak("Opening Paint")
        os.startfile('C:\\Windows\\System32\\mspaint.exe')

# Function to close specific system applications
def closeApp(command):
    if "calculator" in command:
        from engine.command import speak
        speak("Closing Calculator")
        os.system("taskkill /f /im calc.exe")
    elif "notepad" in command:
        speak("Closing Notepad")
        os.system("taskkill /f /im notepad.exe")
    elif "paint" in command:
        speak("Closing Paint")
        os.system("taskkill /f /im mspaint.exe")

# Function to play YouTube videos
def PlayYoutube(query):
    search_term = extract_yt_term(query)
    from engine.command import speak
    if search_term:
        speak("Playing " + search_term + " on YouTube")
        kit.playonyt(search_term)
    else:
        speak("Could not understand the search term.")

# Browsing functionality
def browsing(query):
    if 'google' in query:
        from engine.command import speak, takecommand
        speak("What should I search on Google?")
        search_query = takecommand().lower()
        webbrowser.open(f"https://www.google.com/search?q={search_query}")

# Hotword detection using Porcupine
def hotword():
    porcupine = None
    paud = None
    audio_stream = None
    try:
        porcupine = pvporcupine.create(keywords=["jarvis", "alexa"])
        paud = pyaudio.PyAudio()
        audio_stream = paud.open(
            rate=porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=porcupine.frame_length
        )

        while True:
            keyword = audio_stream.read(porcupine.frame_length)
            keyword = struct.unpack_from("h" * porcupine.frame_length, keyword)
            keyword_index = porcupine.process(keyword)

            if keyword_index >= 0:
                print("Hotword detected")
                pyautogui.hotkey("win", "j")
                time.sleep(2)

    except Exception as e:
        print("Error:", e)
    finally:
        if porcupine:
            porcupine.delete()
        if audio_stream:
            audio_stream.close()
        if paud:
            paud.terminate()

# Find contact from the database
def findContact(query):
    words_to_remove = [ASSISTANT_NAME, 'make', 'a', 'to', 'phone', 'call', 'send', 'message', 'whatsapp', 'video']
    query = remove_words(query, words_to_remove).strip().lower()

    try:
        cursor.execute("SELECT mobile_no FROM contacts WHERE LOWER(name) LIKE ? OR LOWER(name) LIKE ?",
                       ('%' + query + '%', query + '%'))
        results = cursor.fetchall()

        mobile_number_str = str(results[0][0])
        if not mobile_number_str.startswith('+91'):
            mobile_number_str = '+91' + mobile_number_str

        return mobile_number_str, query
    except Exception as e:
        print("Contact not found:", e)
        from engine.command import speak
        speak('Contact does not exist in database')
        return None, None

# WhatsApp messaging, calling, and video calling
def whatsApp(mobile_no, message, flag, name):
    if flag == 'message':
        target_tab = 12
        jarvis_message = f"Message sent successfully to {name}"
    elif flag == 'call':
        target_tab = 7
        message = ''
        jarvis_message = f"Calling {name}"
    else:
        target_tab = 6
        message = ''
        jarvis_message = f"Starting video call with {name}"

    encoded_message = quote(message)
    whatsapp_url = f"whatsapp://send?phone={mobile_no}&text={encoded_message}"
    subprocess.run(f'start "" "{whatsapp_url}"', shell=True)
    time.sleep(5)
    subprocess.run(f'start "" "{whatsapp_url}"', shell=True)

    pyautogui.hotkey('ctrl', 'f')
    for _ in range(target_tab):
        pyautogui.hotkey('tab')
    pyautogui.hotkey('enter')
    from engine.command import speak
    speak(jarvis_message)

# Function to determine the current day
def cal_day():
    day = datetime.datetime.today().weekday() + 1
    day_dict = {
        1: "Monday",
        2: "Tuesday",
        3: "Wednesday",
        4: "Thursday",
        5: "Friday",
        6: "Saturday",
        7: "Sunday"
    }
    return day_dict.get(day, "Unknown")

# Greeting function
def wishMe():
    hour = int(datetime.datetime.now().hour)
    t = time.strftime("%I:%M %p")
    day = cal_day()

    if 0 <= hour < 12:
        return f"Good morning, it's {day} and the time is {t}"
    elif 12 <= hour < 18:
        return f"Good afternoon, it's {day} and the time is {t}"
    else:
        return f"Good evening, it's {day} and the time is {t}"

# Schedule for the day
def schedule():
    day = cal_day().lower()
    week = {
        "monday": "From 2:00 to 3:00 pm you have Prompt engineering class and 3:15 to 4:15 pm you have Software engineering class",
        "tuesday": "From 9:00 to 9:50 you have Web Development class...",
        "wednesday": "From 9:00 to 10:50 you have Machine Learning class...",
        "thursday": "From 9:00 to 10:50 you have Computer Networks class...",
        "friday": "From 9:00 to 9:50 you have Artificial Intelligence class...",
        "saturday": "From 9:00 to 11:50 you have team meetings...",
        "sunday": "Today is a holiday, consider catching up on projects."
    }
    return week.get(day, "No schedule available for today.")
def condition():
    from engine.command import speak
    usage = str(psutil.cpu_percent())
    speak(f"CPU is at {usage} percentage")
    battery = psutil.sensors_battery()
    percentage = battery.percent
    speak(f"sir our system have {percentage} percentage battery")
    if percentage>=80:
        speak("sir we could have enough charging to continue our recording")
    elif percentage>=40 and percentage<=75:
        speak("sir we should connect our system to charging point to charge our battery")
    else:
        speak("sir we have very low power, please connect to charging otherwise recording should be off...")
def date():
    """
    Just return date as string
    :return: date if success, False if fail
    """
    try:
        date = datetime.datetime.now().strftime("%b %d %Y")
    except Exception as e:
        print(e)
        date = False
    return date
def time1():
    """
    Just return time as string
    :return: time if success, False if fail
    """
    try:
        time1 = datetime.datetime.now().strftime("%H:%M:%S")
    except Exception as e:
        print(e)
        time1 = False
    return time1
def news():
    url = 'http://newsapi.org/v2/top-headlines?sources=the-times-of-india&apiKey=ae5ccbe2006a4debbe6424d7e4b569ec'
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error if the request failed
        news_dict = response.json()  # Directly parse JSON
        articles = news_dict.get('articles', [])
        return articles
    except requests.exceptions.RequestException as e:
        print(f"Error fetching news: {e}")
        return []
    except KeyError:
        print("Error: Unexpected response structure.")
        return []
def fetch_weather(city):
    """
    Fetch the weather for a given city.
    :param city: Name of the city
    :return: Weather details or error message
    """
    # API Key and base URL
    api_key = "cdf024a85b9ab6120e651f9d6c682d6f"  # Use your actual API key here
    units_format = "&units=metric"
    base_url = "http://api.openweathermap.org/data/2.5/weather?q="

    # Remove punctuation from the city name (e.g., "Hubli?")
    city = city.translate(str.maketrans("", "", string.punctuation))

    # Build the complete URL
    complete_url = base_url + city + "&appid=" + api_key + units_format

    # Send the GET request
    response = requests.get(complete_url)

    # Parse the JSON response
    city_weather_data = response.json()

    # Check if the city is found
    if city_weather_data["cod"] != "404":
        main_data = city_weather_data["main"]
        weather_description_data = city_weather_data["weather"][0]
        weather_description = weather_description_data["description"]
        current_temperature = main_data["temp"]
        current_pressure = main_data["pressure"]
        current_humidity = main_data["humidity"]
        wind_data = city_weather_data["wind"]
        wind_speed = wind_data["speed"]

        # Build the final weather response
        final_response = f"""
        The weather in {city} is currently {weather_description} 
        with a temperature of {current_temperature}°C, 
        atmospheric pressure of {current_pressure} hPa, 
        humidity of {current_humidity}% 
        and wind speed of {wind_speed} km/h.
        """
        return final_response
    else:
        return "Sorry, I couldn't find the city in my database. Please try again."
def tell_me_about(topic):
    try:
        # info = str(ny.content[:500].encode('utf-8'))
        # res = re.sub('[^a-zA-Z.\d\s]', '', info)[1:]
        res = wikipedia.summary(topic, sentences=3)

        return res
    except Exception as e:
        print(e)
        return False
# Chatbot interaction using HugChat
def chatBot(query):
    user_input = query.lower()
    chatbot = hugchat.ChatBot(cookie_path="engine/cookies.json")
    id = chatbot.new_conversation()
    chatbot.change_conversation(id)
    response = chatbot.chat(user_input)
    from engine.command import speak
    print(response)
    speak(response)
    return response
