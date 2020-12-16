#!/usr/bin/env python
# coding: utf-8

# In[1]:


import sqlite3
import re
import random
import string
from termcolor import colored
import sys
import pandas as pd
from tabulate import tabulate 
import colorama

colorama.init()


# In[2]:


def get_random_string(length):
    # Random string with the combination of lower and upper case
    letters = string.ascii_letters
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str


# # User Class

# In[3]:


class User:
    userTypes = {
        1:"student",
        2:"teacher",
        3:"admin",
    }
    
    genders = {
        1: "male",
        2: "female",
        3: "rather not say"
    }
    
    def __init__(self, id="", email="", studentId="", firstName = "", surname="", dob="", userType=1, gender=1, address="", mobile="", password=""):
        self.id = id
        self.email = email
        self.firstName = firstName
        self.surname = surname
        self.studentId = studentId
        self.dob = dob
        self.userType = userType
        self.gender = gender
        self.address = address
        self.mobile = mobile
        self.password = password
    
    def getName(self):
        return "{} {}".format(self.firstName, self.surname)
    
    def fromTuple(userTuple):
        return User(userTuple[0], userTuple[1], userTuple[2], 
                    userTuple[3],userTuple[4],userTuple[5],
                    int(userTuple[6]),int(userTuple[7]),userTuple[8],
                    userTuple[9], userTuple[10])
    
    def __str__(self):
        return """
        User(
            email = {},
            first name = {},
            surname = {},
            studentId = {},
            dob = {},
            userType = {},
            gender = {},
            mobile number = {},
        )
        """.format(self.email, 
                   self.firstName, 
                   self.surname, 
                   self.studentId, 
                   self.dob, 
                   self.userTypes[self.userType], 
                   self.genders[self.gender],
                   self.mobile
                  )


# # UserRepository Class

# In[4]:


class UserRepository:
    def __init__(self):
        self.__initializeDatabase()
        
        
    def __initializeDatabase(self):
        conn = sqlite3.connect("student.db")
        cur = conn.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS student (id INTEGER PRIMARY KEY, Email text,
                   StdID text, 
                   Firstname text, 
                   Surname text, 
                   DOB text,
                   usertype text,
                   Gender text,
                   Address text,
                   Mobile text,
                   Password text
                   )""")
        conn.commit()
        conn.close()

    def create(self, email, studentId, firstName, surname, dob, usertype, gender, address, mobile, password):
        conn = sqlite3.connect("student.db")
        cur = conn.cursor()
        cur.execute ("INSERT INTO student VALUES (NULL, ?,?,?,?,?,?,?,?,?,?)", (email, studentId, firstName, surname, dob, usertype, gender, address, mobile, password))
        conn.commit()
        row = cur.fetchall()
        conn.close()
        return row

    def findAll(self):  
        conn = sqlite3.connect("student.db")
        cur = conn.cursor()
        cur.execute("SELECT id, Email, StdID, Firstname, Surname, DOB, usertype, Gender, Address, Mobile FROM student")
        conn.commit()
        row = cur.fetchall()
        conn.close()
        return row
    
    def findById(self, id):
        conn = sqlite3.connect("student.db")
        cur = conn.cursor()
        cur.execute("SELECT id, Email, StdID, Firstname, Surname, DOB, usertype, Gender, Address, Mobile, Password FROM student WHERE id=?", (str(id),))
        conn.commit()
        row = cur.fetchone()
        conn.close()
        return row
    
    def findByStudentId(self, studentId):
        conn = sqlite3.connect("student.db")
        cur = conn.cursor()
        cur.execute("SELECT id, Email, StdID, Firstname, Surname, DOB, usertype, Gender, Address, Mobile, Password FROM student WHERE StdID=?", (studentId,))
        conn.commit()
        row = cur.fetchone()
        conn.close()
        return row
    
    def findFirstByUserType(self, userType):
        conn = sqlite3.connect("student.db")
        cur = conn.cursor()
        cur.execute("SELECT id, Email, StdID, Firstname, Surname, DOB, usertype, Gender, Address, Mobile, Password FROM student WHERE usertype=?", (userType,))
        conn.commit()
        row = cur.fetchone()
        conn.close()
        return row
    
    def findByEmail(self, email):
        conn = sqlite3.connect("student.db")
        cur = conn.cursor()
        cur.execute("SELECT id, Email, StdID, Firstname, Surname, DOB, usertype, Gender, Address, Mobile, Password FROM student WHERE Email=?", (email,))
        conn.commit()
        row = cur.fetchone()
        conn.close()
        return row

    def delete(self, id):
        conn = sqlite3.connect("student.db")
        cur = conn.cursor()
        cur.execute("DELETE FROM student WHERE id=?", (str(id),))
        conn.commit()
        conn.close()

    def update(self, id, email = "", studentId="", firstName="",surname="", dob="", usertype="", gender="", address="", mobile="", password=""):
        conn = sqlite3.connect("student.db")
        cur = conn.cursor()
        cur.execute("UPDATE student SET Email=?, StdID=?, Firstname=?, Surname=?, DOB=?, usertype=?, Gender=?, Address=?, Mobile=?, Password=? WHERE id=?", 
                    (email, studentId, firstName, surname, dob, usertype, gender, address, mobile, password, id))
        conn.commit()
        conn.close()


# # UserService class

# conn = sqlite3.connect("student.db")
# cur = conn.cursor()
# cur.execute("DROP TABLE student")
# conn.commit()
# conn.close()

# In[5]:


class UserService:
    emailRegex = '^(\w+[\._]?)*\w+[@]\w+[.]\w{2,3}$'
    nameRegex = '^[a-zA-Z\-]+$'
    
    def __init__(self):
        self.repository = UserRepository()
        self.authenticatedUser = None
        
        # Find first admin
        userTuple = self.repository.findFirstByUserType(3)
        
        if userTuple == None:
            self.repository.create("admin@admin.com", "", 
                               "Joyce", "Odeh", 
                               "2020-2-20", 3, 
                               2, "", "",
                               "password")
            
    def findAll(self):
        if self.authenticatedUser == None:
            raise TypeError("Unauthenticated")
        authenticatedUserType = User.userTypes[int(self.authenticatedUser.userType)].lower()
        if authenticatedUserType != "admin" and authenticatedUserType != "teacher": 
            raise TypeError("The authenticated user doesn't have the permission to perform this action")
            
        
        return self.repository.findAll()
    
    def findByEmail(self, email):
        userTuple = self.repository.findByEmail(email)
        
        if userTuple == None:
            raise Exception("User not found")
        
        user = User.fromTuple(userTuple)
        return user
        
    def findById(self, id):
        userTuple = self.repository.findById(id)
        
        if userTuple == None:
            raise Exception("User not found")
        
        user = User.fromTuple(userTuple)
        return user
    
    def delete(self, id):
        userTuple = self.repository.delete(id)
        return
    
    def updateAuthenticatedUser(self):
        user = self.authenticatedUser
        
        self.validateUserRequiredFields(user)
        
        self.repository.update(id=user.id,
                               email = user.email,
                               studentId=user.studentId, 
                               firstName=user.firstName,
                               surname=user.surname, 
                               dob=user.dob, 
                               usertype=user.userType, 
                               gender=user.gender, 
                               address=user.address, 
                               mobile=user.mobile,
                               password=user.password)
        
    def canCreateNewUser(self):
        if self.authenticatedUser == None:
            raise TypeError("Unauthenticated")
        authenticatedUserType = User.userTypes[int(self.authenticatedUser.userType)].lower()
        if authenticatedUserType != "admin": 
            return False
        return True
    
    def validateUserRequiredFields(self, user):
        if user.email == None or user.email == "":
            raise ValueError("The email field is required")
            
        if not re.search(self.emailRegex, user.email):
            raise ValueError("The email supplied is not a valid email")
            
        if user.firstName == None or user.firstName == "":
            raise ValueError("The firstName field is required")
            
        if user.surname == None or user.surname == "":
            raise ValueError("The firstName field is required")
        
        if not re.search(self.nameRegex, user.firstName):
            raise ValueError("The firstName can only contain letters and hyphens")
            
        if not re.search(self.nameRegex, user.surname):
            raise ValueError("The surname can only contain letters and hyphens")
        
        if user.userType not in User.userTypes.keys():
            raise ValueError("Invalid value input for the userTypes, value can only be {}".format(list(User.userTypes.keys())))
            
        if user.gender not in User.genders.keys():
            raise ValueError("Invalid value input for the gender, value can only be {}".format(list(User.genders.keys())))
        
    def createUser(self, user):
        if not self.canCreateNewUser():
            raise TypeError("The authenticated user doesn't have the permission to perform this action")
        
        self.validateUserRequiredFields(user)
        
        studentId = ""
        
        if User.userTypes[int(user.userType)] == "student":
            while True:
                studentId = get_random_string(10)
                if self.repository.findByStudentId(studentId) == None: break
            
        self.repository.create(user.email, studentId, 
                               user.firstName, user.surname, 
                               user.dob, user.userType, 
                               user.gender, user.address, user.mobile,
                               user.password)
        return 1
    
    
    def login(self, email, password):
        userTuple = self.repository.findByEmail(email)
        
        if userTuple == None:
            raise Exception("The user with the email does not exist")
        
        user = User.fromTuple(userTuple)
        
        if user.password != password:
            raise Exception("Email or password is incorrect")
        
        self.authenticatedUser = user
        
        return user


# In[ ]:





# In[ ]:





# In[6]:


class CliHelper:
    @staticmethod
    def viewProfile( userService):
        user = userService.authenticatedUser
        
        print(user)
        while True:
            commands = """
            1 => Edit profile,
            2 => Back,
            3 => Exit
            """
            
            print(colored(commands, "yellow"))
            
            intVal = 0
            try:
                intVal = int(input("Enter command: "))

                if not (intVal > 0 and intVal <= 3):
                    raise Exception("")
            except:
                print(colored("Invalid input", "red"))
                continue
            
            if intVal == 3:
                sys.exit("Logged out.")
                
            if intVal == 2:
                break
            
            CliHelper.editProfile(userService)
            
    def populateUser(user):
        
        
        firstName = input("First Name ({}): ".format(user.firstName))
        if firstName != None and firstName != "":
            user.firstName = firstName
            
        surname = input("Surname ({}): ".format(user.surname))
        if surname != None and surname != "":
            user.surname = surname
        
        dob = input("Date of birth ({}): ".format(user.dob))
        if dob != None and dob != "":
            user.dob = dob
            
        password = input("Password ({}): ".format(user.password))
        if password != None and password != "":
            user.password = password
            
        
            
        address = input("Address ({}): ".format(user.address))
        if address != None and address != "":
            user.address = address
            
        mobile = input("Mobile ({}): ".format(user.mobile))
        if mobile != None and mobile != "":
            user.mobile = mobile
        
        
        # Genders
        print("Genders: ")
        genderKeys = User.genders.keys()
        for i in genderKeys:
            print("{} => {}".format(i, User.genders[i]))
        
        while True:
            try:
                genderInput = input("Gender ({}): ".format(User.genders[int(user.gender)]))
                if genderInput == None or genderInput == "":
                    break
                gender = int(genderInput)
                
                if gender not in genderKeys: raise Exception()
                    
                user.gender = gender
                break
            except:
                print("Invalid gender input, must be {}".format(list(genderKeys)))
        
        return user
            
    @staticmethod
    def editProfile(userService):
        print(colored("Click on <Enter> to leave the former value.", "cyan"))
        userService.authenticatedUser = CliHelper.populateUser(userService.authenticatedUser)
        
        try:
            userService.updateAuthenticatedUser()
        except ValueError as e:
            print(colored(e, "red"))
        else:
            print(colored("Profile updated successfully", "green"))
            print()
        
    @staticmethod
    def login(userService):
        while True:
            try:
                print(colored("enter any key to continue (q to exit): ", "yellow"), end="")
                value = input("")

                if value == "q" or value == "Q":
                    sys.exit("")
                email = input("Enter email address: ")
                password = input("Enter password: ")

                userService.login(email, password)
            except Exception as e:
                print(colored("\nLogin error: {}\n\n".format(e), "red"))
            else:
                break
                
    @staticmethod
    def teacherWorkOnDatabase(userService):
        user = userService.authenticatedUser
        
        while True:
            commands = """
            1 => View all users,
            -1 => Back,
            0 => exit,
            """

            print(colored(commands, "yellow"))
            intVal = 0
            try:
                intVal = int(input("Enter command: "))

                if not (intVal >= -1 and intVal <= 2):
                    raise Exception("")
            except:
                print(colored("Invalid input", "red"))
                continue
                
            if intVal == -1: break
            
            if intVal == 0:
                sys.exit("Logged out.")
                
            if intVal == 1:
                columns = ["id", "Email", "StdID", "Firstname", "Surname", "DOB", "usertype", "Gender", "Address", "Mobile"]
                dataTuple = userService.findAll()
                data = []
                
                for datum in dataTuple:
                    data.append(list(datum))
                    
                for datum in data:
                    datum[6] = User.userTypes[int(datum[6])]
                    datum[7] = User.genders[int(datum[7])]
                df = pd.DataFrame(data=data, columns=columns)
                print(tabulate(df, headers = 'keys', tablefmt = 'psql'))
                
    @staticmethod
    def adminWorkOnDatabase(userService):
        user = userService.authenticatedUser
        
        while True:
            commands = """
            1 => View all users,
            2 => Create New User,
            3 => find user by email,
            4 => find user by id,
            5 => Delete User,
            -1 => Back,
            0 => exit,
            """

            print(colored(commands, "yellow"))
            intVal = 0
            try:
                intVal = int(input("Enter command: "))

                if not (intVal >= -1 and intVal <= 5):
                    raise Exception("")
            except:
                print(colored("Invalid input", "red"))
                continue
                
            if intVal == -1: break
            
            if intVal == 0:
                sys.exit("Logged out.")
                
            if intVal == 1:
                columns = ["id", "Email", "StdID", "Firstname", "Surname", "DOB", "usertype", "Gender", "Address", "Mobile"]
                dataTuple = userService.findAll()
                data = []
                
                for datum in dataTuple:
                    data.append(list(datum))
                    
                for datum in data:
                    datum[6] = User.userTypes[int(datum[6])]
                    datum[7] = User.genders[int(datum[7])]
                df = pd.DataFrame(data=data, columns=columns)
                print(tabulate(df, headers = 'keys', tablefmt = 'psql'))
            
            # Create new user
            if intVal == 2:
                newUser = CliHelper.populateUser(User())
                
                #Email
                while newUser.email == None or newUser.email == "":
                    email = input("Email Address(): ")
                    if email != None and email != "":
                        newUser.email = email
                
                #password
                while newUser.password == None and newUser.password == "":
                    password = input("Password (): ")
                    if password != None and password != "":
                        newUser.password = password
                
                # User Type
                print("User Types: ")
                uts = User.userTypes.keys()
                for i in uts:
                    print("{} => {}".format(i, User.userTypes[i]))

                while True:
                    try:
                        utInput = input("User Type (): ")
                        if utInput == None or utInput == "":
                            break
                        ut = int(utInput)

                        if ut not in uts: raise Exception()

                        newUser.userType = ut
                        break
                    except:
                        print("Invalid gender input, must be {}".format(list(uts)))
                        
                try:
                    userService.createUser(newUser)
                except Exception as e:
                    print(colored(e, "red"))
                else: print(colored("User created successfully", "green"))
                    
            if intVal == 3:
                email = input("Enter Email Address: ")
                try:
                    print(userService.findByEmail(email))
                except Exception as e:
                    print(colored(e, "red"))
                    
            if intVal == 4:
                id = input("Enter User Id: ")
                try:
                    print(userService.findById(id))
                except Exception as e:
                    print(colored(e, "red"))
                    
            if intVal == 5:
                id = input("Enter User Id To Delete: ")
                try:
                    print(userService.delete(id))
                except Exception as e:
                    print(colored(e, "red"))
                else: print(colored("User deleted successfully", "green"))


# # Code for the interface
# <p>
#     Below is the code for the command line interface (cli)
# </p>

# In[ ]:


if __name__ == "__main__":
    welcomeBanner = """
     ____               _                         ____      _      _     
    |  _ \             | |                       / __ \    | |    | |    
    | |_) |_   _       | | ___  _   _  ___ ___  | |  | | __| | ___| |__  
    |  _ <| | | |  _   | |/ _ \| | | |/ __/ _ \ | |  | |/ _` |/ _ \ '_ \ 
    | |_) | |_| | | |__| | (_) | |_| | (_|  __/ | |__| | (_| |  __/ | | |
    |____/ \__, |  \____/ \___/ \__, |\___\___|  \____/ \__,_|\___|_| |_|
            __/ |                __/ |                                   
           |___/                |___/                                    

    Hello welcome to the user cli
    """
    print(welcomeBanner)
    
    
    print("========================================================================")
    print("A login is required, please fill your details below")
    
    userService = UserService()
    user = None
    
    #Log in
    CliHelper.login(userService)
    
    user = userService.authenticatedUser
    # User logged in successfully
    print(colored("Successful User log in, welcome {}".format(user.getName()), "green"))
    
    while True:
        if User.userTypes[user.userType] == "student":
            while True:
                commands = """
                1 => View my profile,
                0 => exit
                """
                
                print(colored(commands, "yellow"))
                intVal = 0
                try:
                    intVal = int(input("Enter command: "))
                    
                    if not (intVal >= 0 and intVal <= 1):
                        raise Exception("")
                except:
                    print(colored("Invalid input", "red"))
                    continue
                    
                if intVal == 0:
                    sys.exit("Logged out.")
                        
                if intVal == 1:
                    CliHelper.viewProfile(userService)
                    user = userService.authenticatedUser
        elif User.userTypes[user.userType] == "teacher":
            while True:
                commands = """
                1 => View my profile,
                2 => Work on the database
                0 => exit
                """
                
                print(colored(commands, "yellow"))
                intVal = 0
                try:
                    intVal = int(input("Enter command: "))
                    
                    if not (intVal >= 0 and intVal <= 3):
                        raise Exception("")
                except:
                    print(colored("Invalid input", "red"))
                    continue
                    
                if intVal == 0:
                    sys.exit("Logged out.")
                        
                if intVal == 1:
                    CliHelper.viewProfile(userService)
                    user = userService.authenticatedUser
                if intVal == 2:
                    CliHelper.teacherWorkOnDatabase(userService)
        # For admin users
        elif User.userTypes[user.userType] == "admin":
            while True:
                commands = """
                1 => View my profile,
                2 => Work on the database
                0 => exit
                """
                
                print(colored(commands, "yellow"))
                intVal = 0
                try:
                    intVal = int(input("Enter command: "))
                    
                    if not (intVal >= 0 and intVal <= 3):
                        raise Exception("")
                except:
                    print(colored("Invalid input", "red"))
                    continue
                    
                if intVal == 0:
                    sys.exit("Logged out.")
                        
                if intVal == 1:
                    CliHelper.viewProfile(userService)
                    user = userService.authenticatedUser
                if intVal == 2:
                    CliHelper.adminWorkOnDatabase(userService)


# In[ ]:





# In[ ]:




