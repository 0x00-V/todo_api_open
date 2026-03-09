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
        query = "CREATE TABLE IF NOT EXISTS todoitems (todoitemID INTEGER PRIMARY KEY, completed BOOL DEFAULT 0, userID INTEGER, title TEXT NOT NULL, description TEXT, TimeCreated TIMESTAMP, FOREIGN KEY (userID) REFERENCES users(userID) ON DELETE CASCADE )"
        self.cursor.execute(query)
        self.connection.commit()
        query = "CREATE TABLE IF NOT EXISTS sessions (sessionID INTEGER PRIMARY KEY, userID INTEGER, session TEXT NOT NULL UNIQUE, EmailAddress TEXT NOT NULL, Username TEXT NOT NULL, TimeCreated TIMESTAMP, FOREIGN KEY (userID) REFERENCES users(userID) ON DELETE CASCADE )"
        self.cursor.execute(query)
        self.connection.commit()


    def userLogin(self, email_address, password):
        try:
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
        except sqlite3.Error as err:
            return {"Successful": False, "Response": f"There was an error:\n{err}"}

    def registerUser(self, email_address, password, username, display_name):
        try:
            query = "SELECT emailAddress FROM users WHERE emailAddress = ?"
            self.cursor.execute(query, (email_address,))
            row = self.cursor.fetchone()
            if(row):
                return {"Successful": False, "Response": "Email Taken."}
            query = "SELECT Username FROM users WHERE Username = ?"
            self.cursor.execute(query, (username,))
            row = self.cursor.fetchone()
            if(row):
                return {"Successful": False, "Response": "Username Taken."}
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            query = "INSERT INTO users(EmailAddress, Password, Username, DisplayName) VALUES (?,?,?,?)"
            self.cursor.execute(query, (email_address, hashed_password, username, display_name,))
            self.connection.commit()
        except sqlite3.Error as err:
            return {"Successful": False, "Response": f"There was an error:\n{err}"}
        return {"Successful": True, "Email": email_address, "Username": username}
    

    def createSession(self, user_id, session, email_address, username):
        try:
            query = "SELECT sessionId, TimeCreated FROM SESSIONS WHERE userId = ? ORDER BY TimeCreated ASC"
            self.cursor.execute(query, (user_id,))
            rows = self.cursor.fetchall()
            if len(rows) >= 10:
                query = "DELETE FROM sessions WHERE sessionId = ? AND userId = ?"
                self.cursor.execute(query, (rows[0][0], user_id)) 
            query = "INSERT INTO sessions(userID, session, EmailAddress, Username, TimeCreated) VALUES (?,?,?,?,?)"
            self.cursor.execute(query, (user_id, session, email_address, username, datetime.datetime.now(datetime.timezone.utc),))
            self.connection.commit()
        except sqlite3.Error as err:
            return {"Successful": False, "Response": f"There was an error:\n{err}"}
        return {"Successful": True, "Response": "Session Created."}
    
    
    def checkSession(self, session_id):
        try:
            query = "SELECT userID, EmailAddress, Username FROM sessions WHERE session = ?"
            self.cursor.execute(query, (session_id,))
            row = self.cursor.fetchone()
            if(row):
                return {"Successful": True, "Response": "User session valid.", "UserID": row[0],"EmailAddress": row[1], "Username": row[2]}
            else:
                return {"Successful": False, "Response": "User session not valid."}
        except sqlite3.Error as err:
            return {"Successful": False, "Response": f"There was an error:\n{err}"}
        
    
    def todo_listItems(self, user_id):
        try:
            query = "SELECT * FROM todoitems WHERE userID = ?"
            self.cursor.execute(query, (user_id,))
            rows = self.cursor.fetchall()
            items = []
            if(rows):
                for row in rows:
                    items.append(dict(row))
        except sqlite3.Error as err:
            return {"Successful": False, "Response": f"There was an error:\n{err}"}
        return {"Successful": True, "data": items}


    def todo_createItem(self, user_id, title, description):
        try:
            query = "INSERT INTO todoitems(userID, title, description, TimeCreated) VALUES (?, ?, ?, ?)"
            self.cursor.execute(query, (user_id, title, description, datetime.datetime.now(datetime.timezone.utc),))
            self.connection.commit()   
        except sqlite3.Error as err:
            return {"Successful": False, "Response": f"There was an error:\n{err}"}   
        return {"Successful": True, "Response": "Item Created."}


    def todo_editItem(self, todoitem_id, user_id, title, description):
        try:
            query = "UPDATE todoitems SET title = ?, description = ? WHERE todoitemID = ? AND userID = ?"
            self.cursor.execute(query, (title, description,todoitem_id, user_id))
            self.connection.commit()
        except sqlite3.Error as err:
            return {"Successful": False, "Response": f"There was an error:\n{err}"}       
        return {"Successful": True, "Response": "Item Updated."}


    def todo_toggleCompletion(self, todoitem_id, user_id):
        try:
            query = "SELECT completed FROM todoitems WHERE todoitemID = ? AND userID = ?"
            self.cursor.execute(query, (todoitem_id, user_id))
            row = self.cursor.fetchone()
            if(row == None):
                return {"Successful": False, "Response": "Item doesn't exist."}
            completed = int(row[0])
            query = "UPDATE todoitems SET completed = ? WHERE todoitemID = ? AND userID = ?"
            self.cursor.execute(query, (1, todoitem_id, user_id)) if bool(completed) == False else self.cursor.execute(query, (0, todoitem_id, user_id)) 
            self.connection.commit()
        except sqlite3.Error as err:
            return {"Successful": False, "Response": f"There was an error:\n{err}"} 
        return {"Successful": True, "Response": "Item Updated."}

    def todo_deleteItem(self, todoitem_id, user_id):
        try:
            query = "DELETE FROM todoitems WHERE todoitemID = ? AND userID = ?"
            self.cursor.execute(query, (todoitem_id, user_id,))
            self.connection.commit()
            if self.cursor.rowcount == 0:
                return {"Successful": False, "Response": "Item not found or not owned by user."}
        except sqlite3.Error as err:
            return {"Successful": False, "Response": f"There was an error:\n{err}"}
        return {"Successful": True, "Response": "Item Deleted."}