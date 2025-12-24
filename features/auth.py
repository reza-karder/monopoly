import re
import time
from utils.utils import print_alert, print_panel
from models.models import create_user, find_all_users
import bcrypt

def signin():
    print_panel("SIGN IN")

    def get_email():
        email = input("Enter Your Email: ").strip().lower()

        # is empty
        if (not email.strip()):
            print_alert("Please Enter Something", type="INFO", clear=False)
            return get_email()

        users = find_all_users()
        exists = bool(list(filter(lambda user: user["email"] == email, users)))

        # is there any user with this email
        if (not exists):
            print_alert("This Email Does Not Exists", type="INFO", clear=False)
            return get_email()

        return email

    def get_password():
        password = input("Enter Your Password: ").strip()

        # is empty
        if (not password.strip()):
            print_alert("Please Enter Something", type="INFO", clear=False)
            return get_password()

        return password

    # check if password and email are match
    email = get_email()
    password = get_password().encode("utf-8")
    users = find_all_users()
    user = list(filter(lambda user: user["email"] == email, users))[0]
    is_match = bcrypt.checkpw(password, user["password"].encode("utf-8"))

    if (not is_match):
        print_alert("Email Or Password Is Incorrect", type="INFO", clear=False)
        time.sleep(2)
        return signin()

    return user

def signup():
    print_panel("SIGN UP")

    def get_email():
        email = input("Enter Your Email: ").strip().lower()

        # is empty
        if (not email.strip()):
            print_alert("Please Enter Something", type="INFO", clear=False)
            return get_email()

        # is a correct form
        email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

        if (not re.match(email_regex, email)):
            print_alert("Please Enter an Correct Email", type="INFO", clear=False)
            return get_email()

        # is already used
        users = find_all_users()
        exists = bool(list(filter(lambda user: user["email"] == email, users)))

        if (exists):
            print_alert("This Email Already Exists", type="INFO", clear=False)
            return get_email()

        return email.strip()

    def get_password():
        password = input("Enter Your Password: ").strip()

        # is empty
        if (not password.strip()):
            print_alert("Please Enter Something", type="INFO", clear=False)
            return get_password()

        # is a correct form
        password_regex = r"^(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,}$"

        if (not re.match(password_regex, password)):
            print_alert(
                "Password Must Follow These Conditions \n1. At least 8 characters \n2. At least one uppercase letter \n3. At least one number \n4. At least one special character",
                type="INFO", 
                clear=False
            )
            return get_password()

        return password

    def get_name():
        name = input("Eenter Your Nick Name: ").strip()

        # is empty
        if (not name.strip()):
            print_alert("Please Enter Something", type="INFO", clear=False)
            return get_name()

        # contains space?
        if(" " in name):
            print_alert("Name Cannot Contain Space", clear=False)
            return get_name()

        users = find_all_users()
        is_unique = not bool(
            list(filter(lambda user: user["name"] == name, users)))

        if (not is_unique):
            print_alert("This Nick Name Has Been Choosen", type="INFO", clear=False)
            return get_name()

        return name

    # hash password and create the account
    email = get_email()
    password = get_password().encode("utf-8")
    name = get_name()
    hashed_password = bcrypt.hashpw(password, bcrypt.gensalt(14))

    user = create_user(
        email=email,
        password=hashed_password.decode("utf-8"),
        name=name
    )

    return user