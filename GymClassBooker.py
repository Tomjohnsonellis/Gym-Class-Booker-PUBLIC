import time
from datetime import datetime
import traceback

import schedule
import selenium
from UserInfo import (
    username,
    password,
)
import GymClasses
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def bookClass(activityType, className):
    #This is the bulk of the code, every class is booked via the code in this function
    try:
        print("---------> Attempting to book: \'" + className + "\'")

        # We need to be logged in to book anything .
        login()
        # To avoid booking classes at a gym in a different town, the location is set every time.
        setSite()
        # We then attempt to book the class by navigating the website as a user would,
        # Clicking on the category of the class, then clicking the class we want to book, and confirming.
        makeBooking(className, activityType)
        # Finally to avoid any issues when booking the next class, we log out so we can log in again next time.
        logout()


    except Exception:
        # Should there be an error when booking a class, this allows the program to continue
        # rather than completely crashing, which is helpful when there are 2 classes in a day or there
        # isn't an oppurtunity to restart the program before it is needed again.
        # The exceptions are printed to the console to help debugging.
        # The #####s are to make it stand out when searching for the errors.

        print("##### FAILED TO BOOK \'" + className + "\' - TRYING NEXT CLASS #####")
        print()
        print("####################")
        print()
        print(traceback.format_exc())
        print()
        print("####################")
        print()

        # The error is also saved to a file with the filename of "ERROR - < The current date and time >.txt".
        logFilename = ("ERROR - " + str(datetime.now()) + ".txt")
        logFilename = logFilename.replace(":","-")
        exceptionToLog = str(traceback.format_exc())
        with open(logFilename, "w") as file:
            file.write(exceptionToLog)


def selectActivityType(activityType):
    print("---------> Navigating to \'" + activityType + "\' category...")
    activityTypeButton = wait.until(
        EC.presence_of_element_located((By.XPATH, ('//input[@value="' + activityType + '"]'))))
    activityTypeButton.click()
    print("----> Navigated to \'" + activityType + "\'!")


def logout():
    print("---------> Attempting to logout...")
    logoutButton = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="ctl00_LoginControl_Logoutlnk"]')))
    logoutButton.click()
    print("----> Logout successful!")
    driver.get('https://www.johnsonellis.xyz/i-made-that')


def makeBooking(classToBook, activityType):
    # Classes on the website are split into categories,
    # to book a class you would select the category then the class listed in that category.
    selectActivityType(activityType)

    print("---------> Locating \' " + classToBook + "\' button...")
    classButton = wait.until(
        EC.presence_of_element_located((By.XPATH, '//input[@value="' + classToBook + '"]')))
    print("----> " + classToBook + " found!")
    classButton.click()

    print("---------> Attempting to book...")
    bookButton = wait.until(EC.presence_of_element_located((By.XPATH, '//input[@value="Book"]')))
    bookButton.click()
    print("---------> Confirming...")
    confirmButton = wait.until(EC.presence_of_element_located((By.XPATH, '//input[@value="Book"]')))
    confirmButton.click()
    print("----> Booking confirmed!")
    print("#-> " + username + " is booked in for:")
    print("#-> " + classToBook)


def setSite():
    print("---------> Setting site to corfe mullen...")
    driver.get('https://my.bhliveactive.org.uk/Connect/mrmSelectSite.aspx')
    siteButton = wait.until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="ctl00_MainContent_sitesGrid_ctrl1_lnkListCommand"]')))
    siteButton.click()
    print("----> Site set to corfe mullen!")


def login():
    print("---------> Navigating to main page...")
    driver.get('https://my.bhliveactive.org.uk/Connect/mrmLogin.aspx')
    print("----> Main page navigated to!")

    print("---------> Collecting elements...")
    usernameField = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="ctl00_MainContent_InputLogin"]')))
    passwordField = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="ctl00_MainContent_InputPassword"]')))
    loginButton = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="ctl00_MainContent_btnLogin"]')))
    print("----> Elements collected!")

    print("---------> Entering username + password...")
    usernameField.clear()
    usernameField.send_keys(username)
    passwordField.clear()
    passwordField.send_keys(password)
    print("----> Username + password entered!")

    print("---------> Logging in...")
    loginButton.click()
    print("----> Logged in successfully!")

def initialise():
    print("#####SETTING UP#####")
    chrome_options = ''

    ## THIS IS SYSTEM SPECIFIC - CHANGE THE executable_path ON PI
    driver = webdriver.Chrome(executable_path='C:\\Users\\tomjo\\PycharmProjects\\GymBookerRevamp\\venv\\Scripts\\chromedriver.exe',
                              chrome_options=chrome_options)
    wait = WebDriverWait(driver, 30)
    driver.get('https://www.johnsonellis.xyz/i-made-that')

    schedule.clear()
    print("--------->Constructing schedule commands...")
    scheduleCodeSectionsTemplate = ["schedule.every().", '#DAY#', ".at(\"06:00\").do(bookClass, \'", '#CLASSTYPE#',"\', \'", "#CLASSTIME&NAME#", "\')"]
    codeLinesToExec = []
    for classes in GymClasses.gymClasses:
        codeToExec = ""
        scheduleCodeSections = scheduleCodeSectionsTemplate
        scheduleCodeSections[1] = classes['Day']
        scheduleCodeSections[3] = classes['Type']
        scheduleCodeSections[5] = classes['Name']
        for section in scheduleCodeSections:
            codeToExec += section
        codeLinesToExec.append(codeToExec)
    print("---->Commands constructed!")

    print("--------->Executing constructed commands...")
    for codeLines in codeLinesToExec:
        exec(codeLines)

    print("#->These are the scheduled jobs:")
    print("#####")
    for job in schedule.jobs:
        print(job)
    print("#####")

    print("#####SETUP SUCCESSFUL#####")

initialise()
while True:
    schedule.run_pending()
    print("--------->Waiting...")
    time.sleep(11)

#####
## Links and xcodes used:
# Main page of the gym - https://my.bhliveactive.org.uk/Connect/mrmLogin.aspx
# -Username field - //*[@id="ctl00_MainContent_InputLogin"]
# -Password field - //*[@id="ctl00_MainContent_InputPassword"]
# -Login Button - //*[@id="ctl00_MainContent_btnLogin"]
# Location Setting page - https://my.bhliveactive.org.uk/Connect/mrmSelectSite.aspx
# -Button for 'Corfe Mulllen' - //*[@id="ctl00_MainContent_sitesGrid_ctrl1_lnkListCommand"]
# A button that says 'Book' - //input[@value="Book"]
# Shameless plug - https://www.johnsonellis.xyz/i-made-that
## These publicly available libraries were used:
# Selenium for the web browser control - https://docs.seleniumhq.org/
# Schedule API for executing tasks at specific times- https://pypi.org/project/schedule/
