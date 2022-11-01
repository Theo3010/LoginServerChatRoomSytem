import json
from random import randint
from LoginSystem.number import num


class encryptDecrypt(object):
    def __init__(self) -> None:
        super().__init__()
        self.encrytcode = num

    def encryptUsername(self, username):
        encrytedUsername = ""
        for letterNumber in range(0, len(username)):
            if len(self.encrytcode) > letterNumber:
                character = ord(username[letterNumber]) + self.encrytcode[letterNumber]
                if character < 0:
                    character += 255
                encrytedUsername += chr(character)
            else:
                character = ord(username[letterNumber]) + 5
                if character < 0:
                    character += 255
                encrytedUsername += chr(character)
        return encrytedUsername

    def encryptPassword(self, password):
        characters = []
        code = ""
        encrytedPassword = ""

        for i in range(0, randint(8, 16)):
            characters.append((randint(0, 255)))

        for character in characters:
            code += str(chr(character))
            for letter in password:
                encrytedPassword += chr(ord(letter) + character)

        return encrytedPassword, code

    def decryptPassword(self, username, Password):
        encryptedPassword = ""
        filePassword = ""
        encryptcode = None
        Users = json.load(open("Users.json", "r"))["Users"]
        encryptUsername = self.encryptUsername(username)

        for user in Users:
            if encryptUsername == user:
                encryptcode, filePassword = Users[user][0], Users[user][1]

        if not encryptcode:  # username not correct
            return False, ""

        for character in encryptcode:
            for letter in Password:
                encryptedPassword += chr(ord(letter) + ord(character))

        return encryptedPassword, filePassword


class loginSystem(object):
    def __init__(self) -> None:
        super().__init__()
        self.encrytcode = [2, 10, -5, 12, -20, -1, 9, 31, -50]

    def VaildUsername(self, encrytedUsername):
        # retrun if the username is vailded
        Users = json.load(open("Users.json", "r"))["Users"]
        for user in Users:
            if encrytedUsername == user:
                return False
        return True

    def login(self, InputUsername, InputPassword):
        # Check if the username and password matched
        InputPasswordEncrypted, CorrectPassword = encryptDecrypt().decryptPassword(InputUsername, InputPassword)
        if InputPasswordEncrypted == CorrectPassword:
            return True
        else:
            return False

    def signin(self, username, password):
        # Create an account
        encrytedUsername = encryptDecrypt().encryptUsername(username)
        encrytedPassword, encryptCode = encryptDecrypt().encryptPassword(password)

        if not self.VaildUsername(encrytedUsername):
            return False

        user = {encrytedUsername: [encryptCode, encrytedPassword]}

        with open("Users.json", "r+") as file:
            data = json.load(file)
            data["Users"].update(user)
            file.seek(0)
            json.dump(data, file, indent=4)
        return True

    def main(self):
        # login or signin
        logsign = input("Login or signin [l/s]: ").lower()

        if logsign == "l" or logsign == "login":
            username = input("Username: ")
            password = input("Password: ")
            if self.login(username, password):
                print("You are now loggged in")
            else:
                print("You username or password was incorrect")

        elif logsign == "s" or logsign == "signin":
            username = input("Username: ")
            password = input("Password: ")
            if self.signin(username, password):
                print("You are now signed in")
            else:
                print("Username allready used")

        else:
            self.main()


if __name__ == "__main__":
    loginSystem().main()


# TODO: encrypt number.py (mabye dont needed when made to .exe)
