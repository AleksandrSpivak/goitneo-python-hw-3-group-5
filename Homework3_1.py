# after the first launch of the bot address book is saved in "dz3_data.bin" file
# starting from the second launch of the bot adress book is read from the file "dz3_data.bin"
# functions excessive to bot logic commented but not deleted yet

from collections import UserDict
from datetime import datetime, timedelta
import re
import pickle
import os


class WrongCommandError(Exception):
    pass


class ContactAlreadyExistsError(Exception):
    pass


class ContactDoesNotExistError(Exception):
    pass


class NotPhoneNumberError(Exception):
    pass


class ContactListIsEmptyError(Exception):
    pass


class BirthdayDoesNotDefinedYetError(Exception):
    pass


class BirthdayInputError(Exception):
    pass


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    def __init__(self, value):
        self.value = value


class Phone(Field):
    def __init__(self, value):
        if self.__is_phone_number(value):
            self.value = value
        else:
            raise NotPhoneNumberError

    def __is_phone_number(self, value):
        self.value = value
        digits = re.findall(r"\d+", self.value)
        number = ""
        for digit in digits:
            number += digit
        if len(number) == len(self.value) and len(number) == 10:
            return True
        else:
            return False

    def __str__(self):
        return str(self.value)


class Birthday:
    def __init__(self, value):
        if self.__is_birthday(value):
            self.value = datetime.strptime(value, "%d.%m.%Y")
        else:
            raise BirthdayInputError

    def __is_birthday(self, value):
        try:
            self.value = datetime.strptime(value, "%d.%m.%Y")
            return True
        except ValueError:
            return False

    def __str__(self):
        return self.value.strftime("%d.%m.%Y")


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, numbers):
        for n in numbers:
            self.phones.append(Phone(n))

    # def remove_phone(self, number):
    #     for phone in self.phones:
    #         if phone.value == number:
    #             self.phones.remove(phone)

    def edit_phone(self, old_number, new_number):
        for phone in self.phones:
            if phone.value == old_number:
                self.phones[self.phones.index(phone)] = Phone(new_number)

    #       self.phones[0] = Phone(new_number)

    # def find_phone(self, number):
    #     for phone in self.phones:
    #         if phone.value == number:
    #             return phone

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def show_birthday(self):
        print(f"{self.name.value} birthday: {self.birthday}")

    def __str__(self):
        if self.birthday:
            return f"Contact name: {self.name.value}, birthday: {self.birthday}, phones: {'; '.join(p.value for p in self.phones)}"
        else:
            return f"Contact name: {self.name.value}, birthday: ----------, phones: {'; '.join(p.value for p in self.phones)}"


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    # def find(self, name):
    #     for key, val in self.data.items():
    #         if key == name:
    #             return val

    # def delete(self, name):
    #     for key in self.data:
    #         if key == name:
    #             store = key
    #     self.data.pop(store)

    def get_birthdays_per_week(self):
        congrats = {
            "Monday": "",
            "Tuesday": "",
            "Wednesday": "",
            "Thursday": "",
            "Friday": "",
        }

        today_is = datetime.now().date()
        day_of_week = today_is.weekday()
        next_monday = today_is + timedelta(7 - day_of_week)
        next_friday = next_monday + timedelta(4)
        saturday = next_monday - timedelta(2)

        for key in self.data:
            name = key
            birthday = self.data[key].birthday.value.date()
            birthday_this_year = birthday.replace(year=today_is.year)

            if (birthday_this_year < today_is) and (
                (today_is - birthday_this_year).days > 7
            ):
                birthday_this_year = birthday.replace(year=today_is.year + 1)

            if birthday_this_year >= saturday and birthday_this_year <= next_friday:
                if birthday_this_year.weekday() in [0, 5, 6]:
                    congrats["Monday"] += f"{name}, "
                if birthday_this_year.weekday() == 1:
                    congrats["Tuesday"] += f"{name}, "
                if birthday_this_year.weekday() == 2:
                    congrats["Wednesday"] += f"{name}, "
                if birthday_this_year.weekday() == 3:
                    congrats["Thursday"] += f"{name}, "
                if birthday_this_year.weekday() == 4:
                    congrats["Friday"] += f"{name}, "
        for c in congrats:
            print(f"{c}: {congrats[c][:-2]}")

    def __str__(self):
        s = ""
        for rec in self.data.values():
            s += f"{rec}\n"
        return s


def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (FileNotFoundError, pickle.PickleError):
            return f"File {file_name} is not found or damaged"
        except WrongCommandError:
            return "Invalid command."
        except ContactAlreadyExistsError:
            return "Such contact already exists"
        except NotPhoneNumberError:
            return "Number should consist of 10 digits"
        except ContactListIsEmptyError:
            return "Empty contact list"
        except BirthdayDoesNotDefinedYetError:
            return "Input the birthday first"
        except BirthdayInputError:
            return "Input birthday in a format dd.mm.YYYY"
        except (ContactDoesNotExistError, IndexError):
            return "Contact not found"
        except ValueError:
            return "Give me name and phone please."

    return inner


@input_error
def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    if cmd == "":
        raise WrongCommandError
    return cmd, *args


@input_error
def add_contact(args, contacts):
    name = args[0]
    if name in contacts:
        raise ContactAlreadyExistsError

    phone = list()
    for a in range(1, len(args)):
        phone.append(args[a])

    new_record = Record(name)
    new_record.add_phone(phone)
    contacts.add_record(new_record)
    return "Contact added."


@input_error
def change_contact(args, contacts):
    name, old_phone, new_phone = args
    if name not in contacts:
        raise ContactDoesNotExistError
    record = contacts[name]
    record.edit_phone(old_phone, new_phone)
    return "Contact updated."


@input_error
def show_phone(args, contacts):
    name = args[0]
    if name not in contacts:
        raise ContactDoesNotExistError
    return f"{name} phone: {'; '.join(p.value for p in contacts[name].phones )}"


@input_error
def show_all(contacts):
    if len(contacts) == 0:
        raise ContactListIsEmptyError
    return contacts


@input_error
def add_birthday(args, contacts):
    name, dob = args
    if name not in contacts:
        raise ContactDoesNotExistError
    contact = contacts[name]
    contact.add_birthday(dob)
    return "Birthday added."


@input_error
def show_birthday(args, contacts):
    name = args[0]
    if name not in contacts:
        raise ContactDoesNotExistError
    if contacts[name].birthday == None:
        raise BirthdayDoesNotDefinedYetError
    return f"{name} birthday: {contacts[name].birthday}"


@input_error
def load_address_book(file_name):
    global contacts
    if os.path.getsize(file_name) > 0:
        with open(file_name, "rb") as fh:
            contacts = pickle.load(fh)
    return f"Address book is loaded from {file_name} file"


@input_error
def save_address_book(file_name, contacts):
    with open(file_name, "wb") as fh:
        if len(contacts) > 0:
            pickle.dump(contacts, fh)
    return f"Address book is saved into {file_name} file"


if __name__ == "__main__":
    print("Welcome to the assistant bot!")

    contacts = AddressBook()
    file_name = "dz3_data.bin"
    print(load_address_book(file_name))

    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, contacts))
        elif command == "change":
            print(change_contact(args, contacts))
        elif command == "phone":
            print(show_phone(args, contacts))
        elif command == "add-birthday":
            print(add_birthday(args, contacts))
        elif command == "show-birthday":
            print(show_birthday(args, contacts))
        elif command == "birthdays":
            print(contacts.get_birthdays_per_week())
        elif command == "all":
            print(show_all(contacts))
        else:
            print("Invalid command.")

    print(save_address_book(file_name, contacts))
