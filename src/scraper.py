from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.select import Select
from selenium.webdriver.chrome.options import Options
import time
from dataclasses import dataclass
import typing
from typing import Any
from json.encoder import JSONEncoder
import json
import os
from os.path import dirname, abspath

@dataclass
class Period():
    periodNum: int
    periodName: str
    teacherName: str
    gradePercent: float
    currentMark: str
    isPrior: bool

class PeriodEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__

class Request:
    def __init__(self, URL, password, username):
        #Configure website URL and logins
        self.URL = URL
        self.password = password
        self.username = username

        #Set chrome options
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')

        #Configure webdriver
        parentDirectory = dirname(dirname(abspath(__file__)))
        driverLocation = os.path.join(parentDirectory, "ext/", "chromedriver.exe")
        print(driverLocation)
        self.driver = webdriver.Chrome(driverLocation, options=options)
        self.driver.get(self.URL)

        username = self.driver.find_element_by_id("portalAccountUsername")
        username.send_keys(self.username)
        self.driver.find_element_by_id("next").click()

        password = self.driver.find_element_by_id("portalAccountPassword")
        password.send_keys(self.password)

        self.driver.find_element_by_id("LoginButton").click() 
        self.driver.implicitly_wait(5)

    def loadSummary(self):
        self.driver.get("https://aeries.smhs.org/Parent/Widgets/ClassSummary/GetClassSummary?IsProfile=True&_=1622154593572")
        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        self.driver.quit()
        return soup.text

    @staticmethod
    def writeFile(filename, JSONFile):
        with open (filename, 'w') as json_file:
            json_file.write(JSONFile)
        

class DataParser:
    
    def __init__(self, rawJSON) -> None:
        self.rawJSON = rawJSON

    def parseData(self) -> list[Period]:
        allClasses: list[Period] = []
        for period in json.loads(self.rawJSON):
            semesterTime: bool = period['TermGrouping'] == 'Prior Terms'
            currentPeriod: Period = Period(periodNum=period["Period"],
                                    periodName=period["CourseName"],
                                    teacherName=period["TeacherName"],
                                    gradePercent=period["Percent"],
                                    currentMark=period["CurrentMark"],
                                    isPrior=semesterTime)
            allClasses.append(currentPeriod)
        return allClasses

if __name__ == "__main__":
    requestData: Request = Request("https://aeries.smhs.org/Parent/LoginParent.aspx?page=Dashboard.aspx",
                                        "Mao511969",
                                        "jingwen.mao@smhsstudents.org")
    rawJson = requestData.loadSummary()
    dataParser: DataParser = DataParser(rawJson)
    parsedPeriods: list[Period] = dataParser.parseData()
    encodedPeriods: str = PeriodEncoder().encode(parsedPeriods)