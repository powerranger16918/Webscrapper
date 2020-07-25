import json
import requests
import pyttsx3
import speech_recognition as sr
import re
import threading
import time



API_Key='tTyjMeT3LCTA'
Project_Token='tXeF4Obh3AT_'
Run_Token='tTHSTxx7JQZy'

class Data:
    def __init__(self,API_Key,Project_Token):
        self.API_Key=API_Key
        self.Project_Token=Project_Token
        self.params={
            "API_Key": self.API_Key
        }
        self.data = self.get_data()
    def get_data(self):
        response = requests.get(f"https://www.parsehub.com/api/v2/projects/{self.Project_Token}/last_ready_run/data",
                                params={'api_key': API_Key})
        data = json.loads(response.text)
        return data
    def get_total_cases(self):
        data=self.data["NAME"]

        for content in data:
            if content["name"] == "Coronavirus Cases:":
                return content["VALUE"]
        return"0"
    def get_total_deaths(self):
        data = self.data["NAME"]

        for content in data:
            if content["name"] == "Deaths:":
                return content["VALUE"]
        return"0"
    def get_total_recovered(self):
        data = self.data["NAME"]

        for content in data:
            if content["name"] == "Recovered:":
                return content["VALUE"]
        return"0"
    def get_country_data(self,country):
        data=self.data["COUNTRY"]

        for content in data:
            if content["name"].lower() == country.lower():
                return content
        return"0"
    def get_list_of_countries(self):
        countries=[]
        for country in self.data['COUNTRY']:
            countries.append(country['name'].lower())
        return countries

    def update_data(self):
        response = requests.post(f'https://www.parsehub.com/api/v2/projects/{self.Project_Token}/run',
                                 params=self.params)

        def poll():
            time.sleep(0.1)
            old_data = self.data
            while True:
                new_data = self.get_data()
                if new_data != old_data:
                    self.data = new_data
                    print("Data updated")
                    break
                time.sleep(5)

        t = threading.Thread(target=poll)
        t.start()


def speak(text):
    engine=pyttsx3.init()
    engine.say(text)
    engine.runAndWait()
def get_audio():
    r=sr.Recognizer()
    with sr.Microphone() as source:
        audio=r.listen(source)
        said=''

        try:
            said= r.recognize_google(audio)
        except Exception as E:
            print("EXCEPTION:"+str(E))
    return said.lower()
def main():
    print("Started program")
    data = Data(API_Key, Project_Token)
    END_PHRASE="stop"
    country_list=data.get_list_of_countries()
    TOTAL_SEARCH_PATTERNS={
        re.compile("[\w\s]+ total [\w\s]+ cases"): data.get_total_cases,
        re.compile("[\w\s]+ total cases"): data.get_total_cases,
        re.compile("[\w\s]+ total [\w\s]+ deaths"): data.get_total_deaths,
        re.compile("[\w\s]+ total deaths"): data.get_total_deaths
    }
    COUNTRY_PATTERNS = {
        re.compile("[\w\s]+ cases [\w\s]+"): lambda country: data.get_country_data(country)['total_cases'],
        re.compile("[\w\s]+ deaths [\w\s]+"): lambda country: data.get_country_data(country)['total_deaths'],
    }

    UPDATE_COMMAND = "update"

    while True:
        print("Listening...")
        text = get_audio()
        print(text)
        result = None

        for pattern, func in COUNTRY_PATTERNS.items():
            if pattern.match(text):
                words = set(text.split(" "))
                for country in country_list:
                    if country in words:
                        result = func(country)
                        break

        for pattern, func in TOTAL_SEARCH_PATTERNS.items():
            if pattern.match(text):
                result = func()
                break

        if text == UPDATE_COMMAND:
            result = "Data is being updated. This may take a moment!"
            data.update_data()

        if result:
            speak(result)

        if text.find(END_PHRASE) != -1:  # stop loop
            print("Exit")
            break

main()