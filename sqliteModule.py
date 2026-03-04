import sqlite3, json

class Database:
    def __init__(self):
        self.connection = sqlite3.connect("todolist-database.db", check_same_thread=False)
        self.connection.execute("PRAGMA foreign_keys = ON")
        self.connection.row_factory = sqlite3.Row
        self.cursor = self.connection.cursor()
    
    def createDatabase(self):
        query = "CREATE TABLE IF NOT EXISTS users (userID INTEGER PRIMARY KEY, EmailAddress TEXT NOT NULL UNIQUE, Password TEXT NOT NULL, Username TEXT NOT NULL UNIQUE, DisplayName TEXT NOT NULL )"
        self.cursor.execute(query)
        self.connection.commit()
        query = "CREATE TABLE IF NOT EXISTS todoitems (todoitemID INTEGER PRIMARY KEY, userID INTEGER, title TEXT NOT NULL, description TEXT, FOREIGN KEY (userID) REFERENCES users(userID) ON DELETE CASCADE )"
        self.cursor.execute(query)
        self.connection.commit()


    def addTestData(self):
        try:
            query = "INSERT INTO users(EmailAddress, Password, Username, DisplayName) VALUES (?,?,?,?)"
            self.cursor.execute(query, ("test@user.com", "1234", "@test_user", "Test User",))
            self.connection.commit()
            return {"Successful": True, "Response": "Account Created."}

        except Exception as e :
            return {"Successful": False, "Response": "[SQLITE] Backend Error (Add Test Data)"}
    def userLogin(self, email_address, password):
        query = "SELECT EmailAddress, Username, DisplayName FROM users WHERE EmailAddress = ? AND Password = ?"
        self.cursor.execute(query, (email_address, password))
        row = self.cursor.fetchone()
        if row != None:
            return {"Successful": True, "Response": "Correct Credentials. NOT YET IMPLEMENTED FUNCTIONALITY"}
        else:
            return {"Successful": False, "Response": "Incorrect Credentials."}
        
    def registerUser(self, email_address, password, username, display_name):
        query = "SELECT emailAddress FROM users WHERE emailAddress = ?"
        self.cursor.execute(query, (email_address,))
        rows = self.cursor.fetchone()
        if(rows):
            return {"Successful": False, "Response": "Email Taken."}
        query = "SELECT Username FROM users WHERE Username = ?"
        self.cursor.execute(query, (username,))
        rows = self.cursor.fetchone()
        if(rows):
            return {"Successful": False, "Response": "Username Taken."}
        
        query = "INSERT INTO users(EmailAddress, Password, Username, DisplayName) VALUES (?,?,?,?)"
        self.cursor.execute(query, (email_address, password, username, display_name))
        self.connection.commit()
        return {"Successful": True, "Email": email_address, "Username": username}

sqlite3Database = Database()
sqlite3Database.createDatabase()

