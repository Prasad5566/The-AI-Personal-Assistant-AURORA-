import pyttsx3
import speech_recognition as sr
import eel
import time
import pprint
import datetime
import pyautogui
import requests
import re
import sys
import os
from PIL import Image
from engine.features import (
    openCommand,
    PlayYoutube,
    findContact,
    whatsApp,
    cal_day,
    wishMe,
    schedule,
    openApp,
    condition,
    date,
    time1,
    news,
    fetch_weather,
    tell_me_about,
    chatBot,
)
# Text-to-speech function
def speak(text):
    text = str(text)
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id)
    engine.setProperty('rate', 174)
    eel.DisplayMessage(text)
    engine.say(text)
    eel.receiverText(text)
    engine.runAndWait()

# Voice command capture
@eel.expose
def takecommand():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=0.5)
        print("Listening.......", end="", flush=True)
        r.pause_threshold=1.0
        r.phrase_threshold=0.3
        r.sample_rate = 48000
        r.dynamic_energy_threshold=True
        r.operation_timeout=5
        r.non_speaking_duration=0.5
        r.dynamic_energy_adjustment=2
        r.energy_threshold=4000
        r.phrase_time_limit = 10
        # print(sr.Microphone.list_microphone_names())
        audio = r.listen(source)
    try:
        print("\r" ,end="", flush=True)
        print("Recognizing......", end="", flush=True)
        query = r.recognize_google(audio, language='en-in')
        print("\r" ,end="", flush=True)
        print(f"User said : {query}\n")
    except Exception as e:
        print("Say that again please")
        return "None"
    return query
# Command processing
@eel.expose
def allCommands(message=1):
    if message == 1:
        query = takecommand().strip().lower()
        print(f"Debug: Recognized query: {query}")
        eel.senderText(query)
    else:
        query = message.strip().lower()
        eel.senderText(query)

    try:
        # Check for commands and execute corresponding functionality
        if "open" in query and ("app" in query or "application" in query):
            openApp(query)
        elif "close" in query and ("app" in query or "application" in query):
            closeApp(query)
        elif "open" in query:
            openCommand(query)
        elif "youtube" in query or "play" in query:
            PlayYoutube(query)
        elif "browse" in query or "google" in query:
            browsing(query)
        elif 'are you there' in query:
            speak("Yes Sir, I am here to help")
        elif 'who made you' in query:
            speak("I was built by team aurora and team members are Prasad Maddikar  Abhishek Hatti appu patil abhishek math")
        elif 'what is your name' in query or "who are you" in query:
            speak("My name is AURORA, the AI personal assistant")
        elif 'stands for' in query:
            speak("AURORA stands for Automated User Responsive Operational Resource assistant")
        elif 'who is our project guide' in query:
            speak("your project guide is Professor S S Yendingeri")
        elif 'who is our head of the department' in query:
            speak("your head of the department is docter v b pagi")
        elif 'who is our project coordinator' in query:
            speak("your project coordinator is Dr G B chittapur")
        elif 'Tell me about Basaveshwara Engineering College Bagalkot' in query:
            speak("The institution, established in 1963, operates as an autonomous entity with the motto Quality Technical Education through Innovation.Located in Karnataka, India, near Bagalkot city on Raichur-Belgaum Road, its urban campus spans 150 acres (610,000 m²). Led by President Veeranna C. Charantimath, the institution is accredited by AICTE and NBA and is affiliated with Visvesvaraya Technological University (VTU)")
        elif "send message" in query or "phone call" in query or "video call" in query:
            flag = ""
            contact_no, name = findContact(query)
            if contact_no:
                if "send message to" in query:
                    flag = "message"
                    speak("What message to send?")
                    query = takecommand()
                elif "phone call to" in query:
                    flag = "call"
                else:
                    flag = "video call to"
                whatsApp(contact_no, query, flag, name)
        elif "day" in query or "what day is today" in query:
            speak(f"Today is {cal_day()}")
        elif "wish me" in query or "greet me" in query:
            speak(f"Hello  {wishMe()}")
        elif "college time table" in query or "what is today schedule" in query :
            speak(f"college time table today is{schedule()}")
        elif ("system condition" in query) or ("condition of the system" in query):
            speak(f"checking the system condition {condition()}")
        elif ("volume up" in query) or ("increase volume" in query):
            pyautogui.press("volumeup")
            speak("Volume increased")
        elif ("volume down" in query) or ("decrease volume" in query):
            pyautogui.press("volumedown")
            speak("Volume decrease")
        elif ("volume mute" in query) or ("mute the sound" in query):
            pyautogui.press("volumemute")
            speak("Volume muted")
        elif "what is the date" in query:
            time_c1 = date()
            print(time_c1)
            speak(f"Sir, the Date is {time_c1}")
        elif "time" in query:
            time_c =time1()
            print(time_c)
            speak(f"Sir, the time is {time_c}")
        elif "buzzing" in query or "what is the news today" in query or "headlines" in query:
            news_res = news()
            speak('Source: The Times Of India')
            speak('Today\'s Headlines are...')
            for index, articles in enumerate(news_res):
                pprint.pprint(articles['title'])
                speak(articles['title'])
                if index == len(news_res) - 2:
                    break
            speak('These were the top headlines. Have a nice day, Sir!')
        elif "what is the weather" in query:
            try:
                # Check if "in" is part of the query
                if "in" in query:
                    city = query.split("in", 1)[-1].strip()  # Extract city after "in"
                else:
                    city = "default_city"  # Replace with your default city, e.g., "Mumbai"

                if city:
                    weather_res = fetch_weather(city)
                    print(weather_res)
                    speak(weather_res)
                else:
                    speak("Sorry, I couldn't understand the city name. Please try again.")
            except Exception as e:
                print(f"Error: {e}")
                speak("An error occurred while fetching the weather.")

        elif "tell me" in query:
            try:
                if "about" in query:
                    topic = query.split("about")[-1].strip()  # Extract topic after "about"
                    if topic:
                        wiki_res = tell_me_about(topic)
                        print(wiki_res)
                        speak(wiki_res)
                    else:
                        speak("Sorry, I couldn't understand the topic. Please try again.")
                else:
                    speak("Please specify a topic after 'tell me about'.")
            except Exception as e:
                print(f"Error: {e}")
                speak("An error occurred while processing your request.")
        elif "take screenshot" in query or "take a screenshot" in query:
            try:
                from datetime import datetime
                name = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                speak("Taking the screenshot.")
                img = pyautogui.screenshot()
                img.save(name)
                speak(f"The screenshot has been saved as {name}.")
            except Exception as e:
                print(f"Error: {e}")
                speak("An error occurred while taking the screenshot.")
        elif "show me the screenshot" in query:
            try:
                if last_screenshot_name:  # Ensure a screenshot has been taken
                    img = Image.open(f'C:\\Users\\DELL\\Desktop\\A.U.R.O.R.A\\AURORA\\{last_screenshot_name}')
                    img.show()  # Display the screenshot
                    speak("Here it is, sir.")
                    time.sleep(2)
                else:
                    speak("No screenshot has been captured yet. Please take a screenshot first.")
            except IOError:
                speak("Sorry, sir, I am unable to display the screenshot.")
            except Exception as e:
                print(f"Error: {e}")
                speak("An error occurred while trying to show the screenshot.")
        elif "ip address" in query:
            ip = requests.get('https://api.ipify.org').text
            print(ip)
            speak(f"Your ip address is {ip}")
        elif "goodbye" in query or "offline" in query or "bye" in query:
            speak("Alright sir, going offline. It was nice working with you")
            sys.exit()
        elif "restart the system" in query:
            speak("Restarting the system")
            os.system("shutdown /r /t 1")  # Windows command for restart

        elif "shutdown the system" in query:
            speak("Shutting down the system")
            os.system("shutdown /s /t 1")  # Windows command for shutdown

        elif "put the system to sleep" in query:
            speak("Putting the system to sleep")
            os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
        else:
            chatBot(query)
    except Exception as e:
        print(f"Error: {e}")
    eel.ShowHood()
