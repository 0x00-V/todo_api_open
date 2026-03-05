import sqlite3, bcrypt, datetime

class Database:
    def __init__(self):
        self.connection = sqlite3.connect("todolist-database.db", check_same_thread=False)
        self.connection.execute("PRAGMA foreign_keys = ON")
        self.connection.row_factory = sqlite3.Row
        self.cursor = self.connection.cursor()
    
    def createDatabase(self):
        query = "CREATE TABLE IF NOT EXISTS users (userID INTEGER PRIMARY KEY, EmailAddress TEXT NOT NULL UNIQUE, Password BLOB NOT NULL, Username TEXT NOT NULL UNIQUE, DisplayName TEXT NOT NULL )"
        self.cursor.execute(query)
        self.connection.commit()
        query = "CREATE TABLE IF NOT EXISTS todoitems (todoitemID INTEGER PRIMARY KEY, userID INTEGER, title TEXT NOT NULL, description TEXT, FOREIGN KEY (userID) REFERENCES users(userID) ON DELETE CASCADE )"
        self.cursor.execute(query)
        self.connection.commit()
        query = "CREATE TABLE IF NOT EXISTS sessions (sessionID INTEGER PRIMARY KEY, userID INTEGER, session TEXT NOT NULL UNIQUE, EmailAddress TEXT NOT NULL, Username TEXT NOT NULL, TimeCreated TIMESTAMP, FOREIGN KEY (userID) REFERENCES users(userID) ON DELETE CASCADE )"
        self.cursor.execute(query)
        self.connection.commit()


    def addTestData(self):
        try:
            query = "SELECT count(*) FROM users"
            self.cursor.execute(query)
            count = self.cursor.fetchone()[0]
            if count == 0:
                query = "INSERT INTO users(EmailAddress, Password, Username, DisplayName) VALUES (?,?,?,?)"
                self.cursor.execute(query, ("test@user.com", "1234", "@test_user", "Test User",))
                self.connection.commit()
            else:
                return {"Successful": False, "Response": "Table is already populated."}
                
            return {"Successful": True, "Response": "Table Populated."}
        except Exception as e :
            return {"Successful": False, "Response": "[SQLITE] Backend Error (Add Test Data)"}
    
    def userLogin(self, email_address, password):
        query = "SELECT userId, EmailAddress, Password, Username, DisplayName FROM users WHERE EmailAddress = ?"
        self.cursor.execute(query, (email_address,))
        row = self.cursor.fetchone()
        if row != None:
            databasePassword = row[2]
            if bcrypt.checkpw(password.encode('utf-8'), databasePassword):
                return {"Successful": True, "Response": "Correct Credentials", "UserID": row[0], "EmailAddress": row[1], "Username": row[3]}
            else:
                return {"Successful": False, "Response": "Incorrect Credentials"}
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
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        query = "INSERT INTO users(EmailAddress, Password, Username, DisplayName) VALUES (?,?,?,?)"
        self.cursor.execute(query, (email_address, hashed_password, username, display_name,))
        self.connection.commit()
        return {"Successful": True, "Email": email_address, "Username": username}
    
    def createSession(self, user_id, session, email_address, username):
        # TODO: CHECK IF USER HAS ANY OTHER SESSIONS. IF GREATER THAN 10 SESSIONS, DELETE THE OLDEST SESSION
        query = "INSERT INTO sessions(userID, session, EmailAddress, Username, TimeCreated) VALUES (?,?,?,?,?)"
        self.cursor.execute(query, (user_id, session, email_address, username, datetime.datetime.now(),))
        self.connection.commit()
        return {"Successful": True, "Response": "Session Created."}