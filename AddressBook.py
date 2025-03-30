from collections import UserDict
from datetime import datetime, timedelta

# Клас для обробки полів
class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

# Клас для імені
class Name(Field):
    pass

# Клас для номера телефону з валідацією
class Phone(Field):
    def __init__(self, value):
        if not (isinstance(value, str) and value.isdigit() and len(value) == 10):
            raise ValueError("Phone number must be a string of 10 digits")
        super().__init__(value)

# Клас для дати народження з валідацією формату DD.MM.YYYY
class Birthday(Field):
    def __init__(self, value):
        try:
            # Перевіряємо формат дати
            datetime.strptime(value, "%d.%m.%Y")
            super().__init__(value)
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

# Клас для запису контакту
class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None  # Додаємо поле для дня народження

    def add_phone(self, phone):
        new_phone = Phone(phone)  # Якщо phone невалідний, це викличе ValueError
        self.phones.append(new_phone)

    def remove_phone(self, phone):
        self.phones = [p for p in self.phones if p.value != phone]

    def edit_phone(self, old_phone, new_phone):
        Phone(new_phone)  # Якщо new_phone невалідний, це викличе ValueError
        for p in self.phones:
            if p.value == old_phone:
                p.value = new_phone
                break
        else:
            raise ValueError(f"Phone {old_phone} not found")

    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
        return None

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)  # Якщо birthday невалідний, це викличе ValueError

    def __str__(self):
        phones = ", ".join(p.value for p in self.phones) if self.phones else "No phones"
        birthday = f", birthday: {self.birthday}" if self.birthday else ""
        return f"Contact name: {self.name}, phones: {phones}{birthday}"

# Клас для адресної книги
class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def find(self, name):
        return self.data.get(name)

    def get_upcoming_birthdays(self):
        today = datetime.today()
        upcoming = []
        for record in self.data.values():
            if record.birthday:
                # Парсимо дату народження
                bday = datetime.strptime(record.birthday.value, "%d.%m.%Y")
                # Замінюємо рік на поточний, щоб порівняти з сьогоднішньою датою
                bday_this_year = bday.replace(year=today.year)
                # Якщо день народження вже був цього року, перевіряємо наступний рік
                if bday_this_year < today:
                    bday_this_year = bday_this_year.replace(year=today.year + 1)
                # Перевіряємо, чи день народження в межах 7 днів від сьогодні
                delta = (bday_this_year - today).days
                if 0 <= delta <= 7:
                    upcoming.append(record)
        return upcoming

# Декоратор для обробки помилок введення
def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (ValueError, KeyError, IndexError) as e:
            return f"Error: {str(e)}"
    return inner

# Функція для парсингу введення користувача
def parse_input(user_input):
    cmd, *args = user_input.strip().lower().split()
    return cmd, args

# Функція для додавання контакту
@input_error
def add_contact(args, book: AddressBook):
    name, phone = args
    record = book.find(name)
    message = "Contact added."
    if record is None:
        record = Record(name)
        book.add_record(record)
    record.add_phone(phone)
    return message

# Функція для зміни номера телефону
@input_error
def change_contact(args, book: AddressBook):
    name, old_phone, new_phone = args
    record = book.find(name)
    if record is None:
        return "Contact not found."
    record.edit_phone(old_phone, new_phone)
    return "Phone number updated."

# Функція для показу номера телефону
@input_error
def show_phone(args, book: AddressBook):
    name, = args
    record = book.find(name)
    if record is None:
        return "Contact not found."
    return str(record)

# Функція для показу всіх контактів
@input_error
def show_all(args, book: AddressBook):
    if not book.data:
        return "No contacts found."
    return "\n".join(str(record) for record in book.data.values())

# Функція для додавання дня народження
@input_error
def add_birthday(args, book: AddressBook):
    name, birthday = args
    record = book.find(name)
    if record is None:
        return "Contact not found."
    record.add_birthday(birthday)
    return "Birthday added."

# Функція для показу дня народження
@input_error
def show_birthday(args, book: AddressBook):
    name, = args
    record = book.find(name)
    if record is None:
        return "Contact not found."
    if record.birthday is None:
        return "Birthday not set."
    return f"{record.name}'s birthday: {record.birthday}"

# Функція для показу найближчих днів народження
@input_error
def birthdays(args, book: AddressBook):
    upcoming = book.get_upcoming_birthdays()
    if not upcoming:
        return "No upcoming birthdays in the next 7 days."
    return "\n".join(str(record) for record in upcoming)

# Головна функція
def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "phone":
            print(show_phone(args, book))
        elif command == "all":
            print(show_all(args, book))
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(birthdays(args, book))
        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()