import sqlite3
import datetime
import os
from enum import Enum

class InputOptions(Enum):
    EXIT = (0, "Exit")
    CREATE_GAME_INVENTORY_ITEMS_GAMEID_ENTRIES = (1, "Create the 12 GameInventoryItems entries for new GameID")
    CREATE_GAME_INFO_ENTRY = (2, "Create GameInfo entry")
    CREATE_REGION_ENTRY = (3, "Create Region entry")
    SHOW_ALL_REGION_ENTRIES = (4, "Show all Regions entries")
    CREATE_MARKETPLACE_ENTRY = (5, "Create Marketplace entry")
    SHOW_ALL_MARKETPLACE_ENTRIES = (6, "Show all Marketplace entries")

    def __new__(cls, value, description):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.description = description
        return obj

def createLog(error_message):
    errorLogFile = 'Error Log.log'

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(errorLogFile, 'a') as errorFile:
        errorFile.write(f"[{timestamp}] {error_message}\n")

def createGameInventoryItemsGameIDEntries(databaseConnection, GameID):
    cursor = databaseConnection.cursor()

    #grab contentTypes from the database
    cursor.execute(f"SELECT ContentType from GamePackageContents")
    contentTypes = [row[0] for row in cursor.fetchall()]

    #grab conditions from the database
    cursor.execute(f"SELECT Condition from Conditions")
    conditions = [row[0] for row in cursor.fetchall()]

    for contentType in contentTypes:
        for condition in conditions:
            cursor.execute(
                f"INSERT INTO GameInventoryItems (GameID, ContentType, Condition)"
                f"VALUES (?, ?, ?)",
                (GameID, contentType, condition)
            )
    databaseConnection.commit()

def createGameInfoEntry(databaseConnection):
    cursor = databaseConnection.cursor()

    gameID = input("Enter the GameID\n")
    name = input("Enter the Name\n")

    cursor.execute(f"SELECT Region from Regions")
    regions = [row[0] for row in cursor.fetchall()]
    print("Select one of the following: " + ", ".join(regions))
    region = input("Enter the Region\n")

    platform = input("Enter the Platform\n")
    priceChartingURL = input("Enter the PriceChartingURL\n")

    cursor.execute(
    f"INSERT INTO GameInfo (GameID, Name, Region, Platform, PriceChartingURL)"
    f"VALUES (?, ?, ?, ?, ?)",
    (gameID, name, region, platform, priceChartingURL)
    )
    databaseConnection.commit()

def createRegionEntry(databaseConnection):
    while True:
        cursor = databaseConnection.cursor()
        shouldDisplayRegions = getTrueFalseFromInput("Show existing region entries?: 0/no, 1/yes\n")

        if shouldDisplayRegions:
            displayRegions(databaseConnection)

        region = input("Enter the Region\n")
        try:
            cursor.execute(
                f"INSERT INTO Regions (Region)"
                f"VALUES (?)",
                (region,))
            databaseConnection.commit()
        except sqlite3.IntegrityError:
            handleError(f"{region} already exists.")
        #Check if user wants to add additional entries. If not, break
        if not getTrueFalseFromInput("Add another Region entry? 0/no 1/yes\n"):
            break

def displayRegions(databaseConnection):
    cursor = databaseConnection.cursor()
    cursor.execute("SELECT Region FROM Regions")
    regions = [row[0] for row in cursor.fetchall()]
    print("Existing Regions: \n")
    for region in regions:
        print(f"{region}")
    pause()

def createMarketplaceEntry(databaseConnection):
    while True:
        cursor = databaseConnection.cursor()
        shouldDisplayMarketplaces = getTrueFalseFromInput("Show existing marketplace entries?: 0/no, 1/yes\n")

        if shouldDisplayMarketplaces:
            displayMarketplaces(databaseConnection)
        
        marketplace = input("Enter the Marketplace\n")
        try:
            cursor.execute(
                f"INSERT INTO Marketplaces (Marketplace)"
                f"VALUES (?)",
                (marketplace,))
            databaseConnection.commit()
        except sqlite3.IntegrityError:
            handleError(f"{marketplace} already exists.")

        #Check if user wants to add additional entries. If not, break
        if not getTrueFalseFromInput("Add another Marketplace entry? 0/no 1/yes\n"):
            break

def displayMarketplaces(databaseConnection):
    cursor = databaseConnection.cursor()
    cursor.execute("SELECT Marketplace FROM Marketplaces")
    marketplaces = [row[0] for row in cursor.fetchall()]
    print("Existing Marketplaces: \n")
    for marketplace in marketplaces:
        print(f"{marketplace}")
    pause()



def displayMenu():
    print("Make a selection between the following options:")
    for inputOption in InputOptions:
        print(f"{inputOption.value}: {inputOption.description}")

def clearScreen():
    os.system('cls' if os.name == 'nt' else 'clear')

def handleError(message: str, shouldClearScreen: bool=True):
    if shouldClearScreen: clearScreen()
    input(f"{message}\nEnter any key to continue\n")
    if shouldClearScreen: clearScreen()
   

def getTrueFalseFromInput(prompt):
    validTrue = {"1", "y", "yes"}
    validFalse = {"0", "n", "no"}

    while True:
        response = input(prompt).strip().lower()
        if response in validTrue:
            return True
        if response in validFalse: 
            return False
        else:
            handleError("Invalid response. Please enter 0, 1, n, y, no, yes")

def pause(message: str ="Enter any key to continue"):
    input(f"\n{message}\n")


def main():
    databaseFile = 'Inventory Finances Database.sqlite'
    with sqlite3.connect(databaseFile) as databaseConnection:
        while True:
            displayMenu()
            userInput = input("Enter your choice: \n")
            
            #ensure input is an integer before we cast it to an int
            if not userInput.isnumeric():
                handleError("Input must be an integer")
                continue

            intUserInput = int(userInput)
            try:
                selectionOption = InputOptions(intUserInput)
            except ValueError:
                handleError("Invalid option selected. Please choose a valid entry")
                continue

            match selectionOption:
                case InputOptions.EXIT:
                    break

                case InputOptions.CREATE_GAME_INVENTORY_ITEMS_GAMEID_ENTRIES:
                    clearScreen()
                    gameID = input("Input the GameID, ensure you insert correctly\n")
                    createGameInventoryItemsGameIDEntries(databaseConnection, gameID)
                    continue

                case InputOptions.CREATE_GAME_INFO_ENTRY:

                    createGameInfoEntry(databaseConnection)
                    continue

                case InputOptions.CREATE_REGION_ENTRY:
                    createRegionEntry(databaseConnection)
                    continue

                case InputOptions.SHOW_ALL_REGION_ENTRIES:
                    displayRegions(databaseConnection)
                    continue

                case InputOptions.CREATE_MARKETPLACE_ENTRY:
                    createMarketplaceEntry(databaseConnection)
                    continue

                case InputOptions.SHOW_ALL_MARKETPLACE_ENTRIES:
                    displayMarketplaces(databaseConnection)
                    continue

if __name__ == '__main__':
    main()