from datetime import datetime
import datetime
import json
from bs4 import BeautifulSoup
import requests
from dataclasses import dataclass
from config import readJSON
from config import writeJSON
from config import apikey

def getResponse(url):
    return requests.get(url)

def getHTML(response):
    return response.text

# -------------------------------------------
# Modify the holiday class to 
# 1. Only accept Datetime objects for date.
# 2. You may need to add additional functions
# 3. You may drop the init if you are using @dataclasses
# --------------------------------------------
@dataclass
class Holiday:
    """Holiday Class"""
    name: str
    date: datetime
    
    def __str__ (self):
        return f"{self.name} ({self.date})"
        # holiday class should include a way to display a holiday
        # String output
        # Holiday output when printed.

# -------------------------------------------
# The HolidayList class acts as a wrapper and container
# For the list of holidays
# Each method has pseudo-code instructions
# --------------------------------------------
class HolidayList:
    """HolidayList Class"""
    def __init__(self):
        self.innerHolidays = []

    def addHoliday(self, holidayObj):
        if type(holidayObj) != Holiday:
            print("Invalid holiday")
            return
        self.innerHolidays.append(Holiday(holidayObj.name, holidayObj.date))
        print(f"Success:\n{holidayObj} has been added to the holiday list.")
        # Make sure holidayObj is an Holiday Object by checking the type
        # Use innerHolidays.append(holidayObj) to add holiday
        # print to the user that you added a holiday

    def findHoliday(self, HolidayName, Date):
        for holiday in self.innerHolidays:
            while True:
                if holiday.name == HolidayName:
                    if holiday.date == Date:
                        print(f"{holiday} exists!")
                        return Holiday
                    else:
                        print(f"Invalid date for {holiday}. Please try again.")
                else:
                    print(f"'{holiday}' does not exist.")

    def removeHoliday(self, HolidayName, Date):
        holidayRemoved = False
        for holiday in self.innerHolidays:
            if holiday.name == HolidayName and holiday.date == Date:
                self.innerHolidays.remove(holiday)
                print(f"\nSuccess:\n{holiday} has been deleted.")
                holidayRemoved = True
        if holidayRemoved == False:
            print(f"{hol_name} ({hol_date}) was not found.")
    
        # Find Holiday in innerHolidays by searching the name and date combination.
        # remove the Holiday from innerHolidays
        # inform user you deleted the holiday

    def read_json(self, filelocation):
        with open(filelocation, "r") as infile:
            data = json.load(infile)
            for holiday in data["holidays"]:
                self.addHoliday(Holiday(holiday["name"],holiday["date"]))
        # Read in things from json file location
        # Use addHoliday function to add holidays to inner list.

    def save_to_json(self, filelocation):
        holiday_list = []
        new_dict = {}
        for i in range(len(self.innerHolidays)):
            holiday_list.append(self.innerHolidays[i].__dict__)
        unique_list = [k for j, k in enumerate(holiday_list) if k not in holiday_list[j + 1:]]
        new_dict.update(holidays = unique_list)
        json_obj = json.dumps(new_dict, indent=4)
        with open(filelocation, "w") as outfile:
            outfile.write(json_obj)

        # Write out json file to selected file.
        
    def scrapeHolidays(self):
        try:
            holidays = []
            for yr in range(2020,2025):
                url = f"https://www.timeanddate.com/holidays/us/{yr}?hol=33554809"
                print(f"Scraping url: {url}")
                resp = requests.get(url, timeout=3)
                html = resp.text
                soup = BeautifulSoup(html,'html.parser')
                table = soup.find('table', attrs={'id':'holidays-table'})
                body = table.find('tbody')
                days = body.find_all("tr")
                for entry in days:
                    holDict = {}
                    yr_date = entry.find("th", attrs={"class": "nw"})
                    name = entry.find("a")
                    if yr_date is not None and name is not None:
                        yr_date = yr_date.text
                        yr_date = f"{yr_date} {yr}"
                        yr_date = datetime.datetime.strptime(yr_date,'%b %d %Y').strftime('%Y-%m-%d')
                        holDict['name'] = name.text
                        holDict['date'] = yr_date
                        holidays.append(holDict)
            for iter in holidays:
                add = Holiday(iter['name'], iter['date'])
                if add not in self.innerHolidays:
                    self.innerHolidays.append(add)
        except:
            print("An error occurred while scraping the data.")
        # Scrape Holidays from https://www.timeanddate.com/holidays/us/ 
        # Remember, 2 previous years, current year, and 2  years into the future. You can scrape multiple years by adding 
            # year to the timeanddate URL. For example https://www.timeanddate.com/holidays/us/2022
        # Check to see if name and date of holiday is in innerHolidays array
        # Add non-duplicates to innerHolidays
        # Handle any exceptions.     

    def numHolidays(self):
        return len(self.innerHolidays)
        # Return the total number of holidays in innerHolidays
    
    def filter_holidays_by_week(self, year, week_number):
        # filter (year chosen) on innerHolidays
        yearChoice = filter(lambda x: datetime.datetime.strptime(x.date, '%Y-%m-%d').isocalendar()[0] == int(year),
                            self.innerHolidays)
        yearChoice = list(yearChoice) # Cast filter results as list
        # Use a lambda function to filter by week number and save this as holidays
        holidays = filter(lambda x: datetime.datetime.strptime(x.date, '%Y-%m-%d').isocalendar()[1] == int(week_number),
                          yearChoice) # Week number is part of the the Datetime object
        holidays = list(holidays)
        return holidays # return your holidays
        
    def displayHolidaysInWeek(self, holidayList):
        for holiday in holidayList:
            print(str(holiday))
        # Use your filter_holidays_by_week to get list of holidays within a week as a parameter
        # Output formated holidays in the week. 
        # * Remember to use the holiday __str__ method.

    def getWeather(self, year, weekNum):
        date1 = str(datetime.date(year, 1, 1) + datetime.timedelta(weeks=+weekNum-1))
        date2 = str(datetime.date(year, 1, 1) + datetime.timedelta(weeks=+weekNum))
        try:
            url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/11223/{date1}/{date2}?unitGroup=metric&include=days&key={apikey}"
            response = requests.get(url).json()
            weather_data = []
            for i in range(len(response['days'])):
                date = response['days'][i]['datetime']
                condition = response['days'][i]['conditions']
                weather_data.append({'date': f'{date}', 'condition': f'{condition}'})
            return weather_data
        except:
            print("Error retrieving weather. Max API calls may have been reached.")
        # Convert weekNum to range between two days
        # Use Try / Except to catch problems
        # Query API for weather in that week range
        # Format weather information and return weather string.

    def viewCurrentWeek(self):
        # Use the Datetime Module to look up current week and year
        weekNum = int(datetime.datetime.today().isocalendar().week)
        year = int(datetime.datetime.today().isocalendar().year)
        # Use your filter_holidays_by_week function to get the list of holidays for the current week/year
        hol_list = self.filter_holidays_by_week(year, weekNum)
        # Use your displayHolidaysInWeek function to display the holidays in the week
        # Ask user if they want to get the weather
        viewWeather = str(input("Would you like to see this week's weather? [y/n] ")).lower()
        if viewWeather == "y":
            weather = self.getWeather(year, weekNum)
            no_holidays = False
            for holiday in hol_list:
                for iter in range(len(weather)):
                    if holiday.__dict__["date"] == weather[iter]["date"]:
                        condition = weather[iter]["condition"]
                        print(f"{holiday} - {condition}")
                        no_holidays = False
            if no_holidays == True:
                print("There are no holidays this week.")
        elif viewWeather == "n":
           self.displayHolidaysInWeek(hol_list)
        else:
            print("Not an option.")
        # If yes, use your getWeather function and display results

def main():
    global readJSON
    global writeJSON

    initHLO = HolidayList() # Initialize HolidayList Object

    initHLO.read_json(readJSON) # Load JSON file via HolidayList read_json function

    initHLO.scrapeHolidays() # Scrape additional holidays using your HolidayList scrapeHolidays function
    
    print(f"""\n                    Holiday Management
      =============================================
      There are {initHLO.numHolidays()} holidays stored in the system.""")

    menu = True # Create while loop for user to keep adding or working with the Calender
    saved = False
    while menu:
        # Display User Menu (Print the menu)
        print("")
        print("""           Holiday Menu
      ======================
      1. Add a Holiday
      2. Remove a Holiday
      3. Save Holiday List
      4. View Holidays
      5. Exit""")
        option = str(input("      Enter an option #: "))
        if option == "1" or option == "1.":
            print("\nAdd a Holiday\n=============")
            name = str(input("Holiday name: ")).title()
            while True:
                date = input(f"Date for '{name}' as YYYY-MM-DD: ")
                try:
                    datetime.datetime.strptime(date, '%Y-%m-%d')
                    holidayObj = Holiday(name, date)
                    initHLO.addHoliday(holidayObj)
                    break
                except:
                    print(f"Invalid date. Please try again.")
        elif option == "2" or option == "2.":
            print("\nRemove a Holiday\n================")
            global hol_name
            global hol_date
            hol_name = str(input("Which holiday do you want to remove? "))
            hol_date = str(input("What is its date? [YYYY-MM-DD] "))
            initHLO.removeHoliday(hol_name, hol_date)
        elif option == "3" or option == "3.":
            print("\nSaving Holiday List\n===================")
            certain = str(input("Are you sure you want to save your changes? [y/n]: ")).lower()
            if certain == "y":
                initHLO.save_to_json(writeJSON)
                print("\nSuccess:\nYour changes have been saved.")
                saved = True
            else:
                print("\nCanceled:\nHoliday list file save canceled.")
                saved = False
        elif option == "4" or option == "4.":
            print("\nView Holidays\n=============")
            while True:
                try:
                    year = int(input("Which year? "))
                    currentYear = datetime.datetime.today().isocalendar().year
                    weekNum = input(f"Which week? #[1-52, Leave blank for the current week]: ")
                    if year == int(currentYear) and (weekNum == "" or weekNum == " "):
                        initHLO.viewCurrentWeek()
                        break
                    elif year > 1000 and str(weekNum).isnumeric():
                        print(f"\nThese are the holidays for {year} week #{weekNum}:")
                        initHLO.displayHolidaysInWeek(initHLO.filter_holidays_by_week(year, weekNum))
                        break
                    else:
                        print("No holidays correspond with the information provided.")
                        break
                except:
                    print(f"\nYou cannot leave this field blank for any other year than {str(currentYear)}.")
                    continue
        elif option == "5" or option == "5.":
            print("\nExit\n====")
            if saved == True:
                saved_exit = str(input("Are you sure you want to exit? [y/n] ")).lower()
                if saved_exit == "y":
                    print("Goodbye!")
                    break
                elif saved_exit == "n":
                    continue
            elif saved == False:
                unsaved_exit = str(input("Are you sure you want to exit?\nYour changes will be lost.\n[y/n]: ")).lower()
                if unsaved_exit == "y":
                    print("Goodbye!")
                    break
                elif unsaved_exit == "n":
                    continue
        else:
            print("Not an option. Try again.")
    # Large Pseudo Code steps
    # -------------------------------------
    # 5. Take user input for their action based on Menu and check the user input for errors
    # 6. Run appropriate method from the HolidayList object depending on what the user input is
    # 7. Ask the User if they would like to Continue, if not, end the while loop, ending the program.  If they do wish to continue, keep the program going. 


if __name__ == "__main__":
    main();


# Additional Hints:
# ---------------------------------------------
# You may need additional helper functions both in and out of the classes, add functions as you need to.
#
# No one function should be more then 50 lines of code, if you need more then 50 lines of code
# excluding comments, break the function into multiple functions.
#
# You can store your raw menu text, and other blocks of texts as raw text files 
# and use placeholder values with the format option.
# Example:
# In the file test.txt is "My name is {fname}, I'm {age}"
# Then you later can read the file into a string "filetxt"
# and substitute the placeholders 
# for example: filetxt.format(fname = "John", age = 36)
# This will make your code far more readable, by seperating text from code.