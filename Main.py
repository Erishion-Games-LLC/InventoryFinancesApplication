import sqlite3
from datetime import datetime
import os
from enum import Enum
from dataclasses import dataclass

class InputOptions(Enum):
    EXIT = (0, "Exit")
    SHOW_ALL_MARKETPLACE_ENTRIES = (1, "Show all Marketplace entries")
    CREATE_MARKETPLACE_ENTRY = (2, "Create Marketplace entry")
    SHOW_SHIPMENTSIN_ENTRY = (3, "Show a certain (or all) shipments in entries")
    CREATE_SHIPMENTSIN_ENTRY = (4, "Create Shipment In entry")

    CREATE_GAME_INVENTORY_ITEMS_GAMEID_ENTRIES = (5, "Create the 12 GameInventoryItems entries for new GameID")
    CREATE_GAME_INFO_ENTRY = (6, "Create GameInfo entry")
    CREATE_REGION_ENTRY = (7, "Create Region entry")
    SHOW_ALL_REGION_ENTRIES = (8, "Show all Regions entries")

    def __new__(cls, value: int, description: str):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.description = description
        return obj

@dataclass
class ColumnConstraints:
    PrimaryKeyColumnName: str
    ForeignKeyColumnNamesDict: dict[str]
    UniqueColumnNamesSet:set[str]
    NotNullColumnNamesSet:set[str]

def displayMenu() -> None:
    print("Make a selection between the following options:")
    for inputOption in InputOptions:
        print(f"{inputOption.value}: {inputOption.description}")

def strippedInput(prompt: str, newLine: bool=True) -> str:
    if newLine:
         return input(prompt + "\n").strip()
    else:
        return input(prompt).strip()

def pauseOrError(message: str, shouldClearScreen: bool=True) -> None:
    if message:
        strippedInput(f"{message}\nEnter any key to continue")
    else:
        strippedInput("Enter any key to continue")
    if shouldClearScreen: clearScreen()
   
def createLog(error_message: str) -> None:
    errorLogFile = 'Error Log.log'

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(errorLogFile, 'a') as errorFile:
        errorFile.write(f"[{timestamp}] {error_message}\n")

def handleException(exception: BaseException) -> None:
    exceptionName = type(exception).__name__
    exceptionMessage = str(exception)
    exceptionMessageLowered = exceptionMessage.lower()
    errorMessage = f"{exceptionName}: {exceptionMessage}"

    foreignKeyMessage = "foreign key constraint failed"
    uniqueMessage = "unique constraint failed"
    notNullMessage = "not null constraint failed"
    checkMessage = "check constraint failed"

    if isinstance(exception, sqlite3.IntegrityError):
        if foreignKeyMessage in exceptionMessageLowered:
            pauseOrError(errorMessage + "\nThe value entered does not exist in the referenced table. Please try a new value\n")
        elif uniqueMessage in exceptionMessageLowered:
            pauseOrError(errorMessage + "\nThe value entered already exists in the database. Please try a new value\n")
        elif notNullMessage in exceptionMessageLowered:
            pauseOrError(errorMessage + "\nThis column requires a value to be entered. You supplied a null. Please enter an appropriate value\n")
        elif checkMessage in exceptionMessageLowered:
            pauseOrError(errorMessage + "\nThe value entered violates the check constraint. Please enter an appropraite value\n")
        else:
            pauseOrError(errorMessage + "\nAn integrity violation has occurred. Please enter an appropraite value\n")

        createLog(errorMessage)
    else:
        pauseOrError(errorMessage)
        createLog(errorMessage)

def clearScreen() -> None:
    os.system('cls' if os.name == 'nt' else 'clear')

def getTrueFalseFromInput(message: str) -> bool:
    validTrue = {"1", "y", "yes"}
    validFalse = {"0", "n", "no"}

    while True:
        response = strippedInput(message).lower()
        if response in validTrue:
            return True
        if response in validFalse: 
            return False
        else:
            pauseOrError("Invalid response. Please enter 0, 1, n, y, no, yes")

def formatAndPrintTable(columnNames: list[str], rows: list[tuple]) -> None:
    # Calculate max width for each column based on header and values
    columnWidths = []
    spacedColumnNames = []
    
    #Loop through each column, add the larger of the length of the header or the largest value to the columnWidths list
    for columnIndex, columnName in enumerate(columnNames):
        headerWidth = len(columnName)
        
        highestWidthValue = 0
        for row in rows:
            #Get the value in the current row for the current column and cast it to a string
            value = str(row[columnIndex])
            #Get the length of the current value
            valueLength = len(value)
            #if the length is greater than the previously largest length, overwrite it
            if valueLength > highestWidthValue:
                highestWidthValue = valueLength

        #Add the larger width of either the header or the largest value
        columnWidths.append(max(headerWidth, highestWidthValue))
    
    #Loop through each column, left justify the names and increase the size with spaces, then add them all to the spacedColumnNames list
    for columnIndex, columnName in enumerate(columnNames):
        #Get the previously stored max width of this column
        columnWidth = columnWidths[columnIndex]
        #Take the columnName and expand it to be the desired width. Fill the empty with spaces.
        spacedColumnName = columnName.ljust(columnWidth)
        #Add each spacedColumnName to a list
        spacedColumnNames.append(spacedColumnName)

    #Combine each column's name into one string, and separate them with a line
    header = " | ".join(spacedColumnNames)
    #Add a second line to header and make it all dashes equal to the length of the first line of the header
    header = header + "\n" + "-" * len(header)

    print(header)     

    #Loop through each row, format its values, then print the formatted rows
    for row in rows:
        spacedRowValues = []
        #Loop through each value in the row, left justify the value and increase the size with spaces, then add them all to the spacedRowValues list
        for columnIndex, rowValue in enumerate(row):
            #Get the value in one columns entry and cast it to a string
            rowValue = str(rowValue)
            #Take the rowValue and expand it to be the desired width. Fill the empty with spaces.
            spacedRowValue = rowValue.ljust(columnWidths[columnIndex])
            #Add each spacedRowValue to a list
            spacedRowValues.append(spacedRowValue)

        #Combine each row value into one string, and separate them with a line
        rowStr = " | ".join(spacedRowValues)
        print(rowStr)

def displayTable(databaseConnection: sqlite3.Connection, tableName: str, columnNames: list[str], beforeCommit: bool=False, loneCall: bool=False) -> None:
    clearScreen()
    cursor = databaseConnection.cursor()
    tablesConstraints = getColumnConstraints(databaseConnection, tableName)
    primaryKeyColumnName = tablesConstraints.PrimaryKeyColumnName

    #combine the primaryKey column name with the columnNames previously specified. 
    columns = [primaryKeyColumnName] + columnNames

    #take the combined names and convert them from a list of strings into a single formated string for use in sql SELECT
    columnsJoined = ", ".join(columns)

    #Sort by most recent added entries
    orderClause = f"ORDER BY {primaryKeyColumnName} DESC"

    cursor.execute(f"SELECT {columnsJoined} FROM {tableName} {orderClause} LIMIT 24")
    rows = cursor.fetchall()
    rows.reverse()

    #minor formatting differences depending on when the function is called
    if beforeCommit:
        print(f"Displaying {tableName} including uncommited changes\n")
    else:
        print(f"Displaying {tableName}\n")

    #if rows is empty, inform user and exit
    if not rows:
        print("No entries found.\n")
        if loneCall:
            print("")
            pauseOrError(None, False)
            clearScreen()
        return

    formatAndPrintTable(columns, rows)

    print("")
    if loneCall:
        pauseOrError(None, False)
        clearScreen()

def confirmCommit(databaseConnection: sqlite3.Connection) -> bool:
    if getTrueFalseFromInput("Commit Entry?"):
        databaseConnection.commit()
        pauseOrError("Entry(s) Commited.\n")
        return True
    else:
        databaseConnection.rollback()
        pauseOrError("Previous entry(s) discarded\n")
        return False

def insertRows(databaseConnection: sqlite3.Connection, tableName: str, columnNames: list[str], values: list[str] | list[list[str]]) -> None:
    cursor = databaseConnection.cursor()
    columnNamesJoined = ", ".join(columnNames)
    valuePlaceholders = ", ".join(["?"] * len(columnNames))
    sqlInsertStatement = f"INSERT INTO {tableName} ({columnNamesJoined}) VALUES ({valuePlaceholders})"

    try:
        #if values is many lists of strings, conduct more performant executemany method
        if isinstance(values[0], list):
            cursor.executemany(sqlInsertStatement, values)

        #if it isn't do standard execute method
        else:
            cursor.execute(sqlInsertStatement, values)
            
        #display the table showing the uncommited new entry   
        displayTable(databaseConnection, tableName, columnNames, True)
        confirmCommit(databaseConnection)

    except Exception as exception:
        databaseConnection.rollback()
        handleException(exception)

def valueExistsInColumn(databaseConnection: sqlite3.Connection, tableName: str, columnName: str, value: str) -> bool:
    cursor = databaseConnection.cursor()
    cursor.execute(f"SELECT COUNT(*) FROM {tableName} WHERE {columnName} = ?", (value,))
    count = cursor.fetchone()[0]
    return count > 0

def getColumnConstraints(databaseConnection: sqlite3.Connection, tableName: str) -> ColumnConstraints:
    cursor = databaseConnection.cursor()
    primaryKeyColumnName = ""
    foreignKeyColumnNamesDict = dict()
    uniqueColumnNamesSet = set()
    notNullColumnNamesSet = set()

    cursor.execute(f"PRAGMA table_info({tableName})")
    tableInfo = cursor.fetchall()
    #look through table_info and store which columns are primaryKeys and which are notNull
    for row in tableInfo:
        #tableInfo spits out data in these columns (cid, name, type, notnull, dflt_value, pk)
        #so index 1 gives the name
        columnName = row[1] 
        #index 3 is a not null flag
        notNull = row[3]
        #index 5 is a primary key flag
        isPrimaryKey = row[5]

        if notNull:
            notNullColumnNamesSet.add(columnName)
        if isPrimaryKey:
            primaryKeyColumnName = columnName

    #look through foreign_key_list and store which columns are foreign keys
    cursor.execute(f"PRAGMA foreign_key_list({tableName})")
    #foreign_key_list returns data as (id, seq, table, from, to, on_update, on_delete, match)
    column = cursor.fetchall()
    #Loop through each foreignKey and grab the appropriate data from it. Use that to store the data into a dict
    for row in column:
        localColumnName = row[3]
        foreignTableName = row[2]
        foreignColumnName = row[4]
        foreignKeyColumnNamesDict[localColumnName] = (foreignTableName, foreignColumnName)


    cursor.execute(f"PRAGMA index_list({tableName})")
    indexes = cursor.fetchall()
    #look through index_list and store which columns are unique
    for index in indexes:
        #index_List returns data in these columns (index_number, index_name, unique_flag, origin, partial)
        indexName = index[1]
        isUnique = index[2]

        #if a column has a unique flag, we check the index_info table to get the columns name and add it to the uniqueColumns set
        if isUnique:
            cursor.execute(f"PRAGMA index_info({indexName})")
            indexInfo = cursor.fetchall()
            for row in indexInfo:
                #index_info returns data in these columns (seqno, cid, name)
                uniqueColumnNamesSet.add(row[2])

    return ColumnConstraints(primaryKeyColumnName, foreignKeyColumnNamesDict, uniqueColumnNamesSet, notNullColumnNamesSet)

def createEntry(databaseConnection: sqlite3.Connection, tableName: str, columnName: list[str]) -> None:
    while True:
        clearScreen()
        tableConstraints = getColumnConstraints(databaseConnection, tableName)
        foreignKeysDict = tableConstraints.ForeignKeyColumnNamesDict

        #Ask the user if they wish to see any existing entries, if so display it
        if getTrueFalseFromInput(f"Show existing {tableName} entries?"):
            displayTable(databaseConnection, tableName, columnName)

        values = []
        for column in columnName:
            #if the column has a foreignKey, display the foreign table
            if column in foreignKeysDict:
                foreignTableName, foreignColumnName = foreignKeysDict[column]
                try:
                    displayTable(databaseConnection, foreignTableName, [foreignColumnName])
                except sqlite3.Error as error:
                    handleException(error)
                
                wrongEntry = True
                #Loop this column entry until a valid foreignKey is entered
                while wrongEntry:
                    value = strippedInput(f"Enter the {column}")
                    #Check if the foreign key value is valid
                    if valueExistsInColumn(databaseConnection, foreignTableName, foreignColumnName, value):
                        values.append(value)
                        wrongEntry = False
                    else:
                        print(f"{value} is not a valid entry for {foreignColumnName}. Please try again\n")
                    
            else:
                value = strippedInput(f"Enter the {column}")
                values.append(value)

        insertRows(databaseConnection, tableName, columnName, values)

        if not getTrueFalseFromInput(f"Add another {tableName} entry?"):
            clearScreen()
            break

def createRegionEntry(databaseConnection: sqlite3.Connection) -> None:
    createEntry(databaseConnection, "Regions", ["Region"])

def createMarketplaceEntry(databaseConnection: sqlite3.Connection) -> None:
    createEntry(databaseConnection, "Marketplaces", ["Marketplace"])

def createGameInventoryItemsGameIDEntries(databaseConnection: sqlite3.Connection) -> None:
    clearScreen()
    gameID = strippedInput("Input the GameID, ensure you insert correctly")
    cursor = databaseConnection.cursor()

    #grab contentTypes from the database
    cursor.execute(f"SELECT ContentType from GamePackageContents")
    contentTypes = [row[0] for row in cursor.fetchall()]

    #grab conditions from the database
    cursor.execute(f"SELECT Condition from Conditions")
    conditions = [row[0] for row in cursor.fetchall()]
    
    values = []
    for contentType in contentTypes:
        for condition in conditions:
            values.append([gameID, contentType, condition])
            
    insertRows(databaseConnection, "GameInventoryItems", ["GameID", "ContentType", "Condition"], values)

def createGameInfoEntry(databaseConnection: sqlite3.Connection) -> None:
    createEntry(databaseConnection, "GameInfo", ["GameID", "Name", "Region", "Platform", "PriceChartingURL"])

def main():
    databaseFile = 'Inventory Finances Database.sqlite'
    with sqlite3.connect(databaseFile) as databaseConnection:
        databaseConnection.execute("PRAGMA foreign_keys = ON")
        while True:
            displayMenu()
            userInput = strippedInput("Enter your choice:")
            
            #ensure input is an integer before we cast it to an int
            if not userInput.isnumeric():
                pauseOrError("Input must be an integer")
                continue

            intUserInput = int(userInput)
            try:
                selectionOption = InputOptions(intUserInput)
            except ValueError:
                pauseOrError("Invalid option selected. Please choose a valid entry")
                continue

            match selectionOption:
                case InputOptions.EXIT:
                    break

                case InputOptions.CREATE_GAME_INVENTORY_ITEMS_GAMEID_ENTRIES:
                    createGameInventoryItemsGameIDEntries(databaseConnection)
                    continue

                case InputOptions.CREATE_GAME_INFO_ENTRY:
                    createGameInfoEntry(databaseConnection)
                    continue

                case InputOptions.CREATE_REGION_ENTRY:
                    createRegionEntry(databaseConnection)
                    continue

                case InputOptions.SHOW_ALL_REGION_ENTRIES:
                    displayTable(databaseConnection, "Regions", ["Region"], False, True)
                    continue

                case InputOptions.CREATE_MARKETPLACE_ENTRY:
                    createMarketplaceEntry(databaseConnection)
                    continue

                case InputOptions.SHOW_ALL_MARKETPLACE_ENTRIES:
                    displayTable(databaseConnection, "Marketplaces", ["Marketplace"], False, True)
                    continue

    #            case InputOptions.CREATE_SHIPMENTSIN_ENTRY:
    #                createShipmentsInEntry(databaseConnection)
    #                continue
                
    #            case InputOptions.SHOW_SHIPMENTSIN_ENTRY:
    #                displayShipmentsInEntry(databaseConnection)
    #                continue

if __name__ == '__main__':
    main()