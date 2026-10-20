import json
from datetime import date, timedelta


class BookNotAvailableError(Exception):
    pass


class BorrowLimitError(Exception):
    pass


class BookNotBorrowedError(Exception):
    pass


class Book:
    def __init__(self, book_id, title, author, is_available):
        self.book_id = book_id
        self.title = title
        self.author = author
        self.is_available = is_available

    def __str__(self):
        return f"Book-ID: {self.book_id}, Title: {self.title}, Author: {self.author}, Availability: {self.is_available}"

    def __repr__(self):
        return f"Book(ID: {self.book_id}, Title: {self.title}, Author: {self.author}, Availability: {self.is_available})"


class Member:
    def __init__(self, member_id, name):
        self.member_id = member_id
        self.name = name
        self.current_loan_list = []

    def __str__(self):
        return f"ID: {self.member_id}, Name: {self.name}, Current Loan: {self.current_loan_list}"

    def __repr__(self):
        return f"Member(ID: {self.member_id}, Name: {self.name}, Current Loan: {self.current_loan_list})"

    def can_borrow(self):
      return len(self.current_loan_list) < 3


class StudentMember(Member):
    def can_borrow(self):
        return len(self.current_loan_list) < 3


class StaffMember(Member):
    def can_borrow(self):
        return len(self.current_loan_list) < 10


class Library:
    def __init__(self):
        self.books = []
        self.members = []
        self.loans = []

    def add_book(self, book):
        self.books.append(book)
        print("Book added successfully!")
        return self.books

    def add_member(self, member):
        self.members.append(member)
        print("Member added successfully!")
        return self.members

    def borrow(self, member_id, book_id):
        for member in self.members:
            if member.member_id == member_id:
                print("Member_ID Found!")
                break
        else:
            return "Member not Found!"

        for book in self.books:
            if book.book_id == book_id and book.is_available:
                print("Book_ID Found and book is available!")
                if member.can_borrow() == True:
                    borrowed_on = date.today()
                    due_on = borrowed_on + timedelta(days=14)
                    returned_on = None
                    loan = Loan(book, member, borrowed_on, due_on, returned_on)
                    book.is_available = False
                    self.loans.append(loan)
                    member.current_loan_list.append(loan)
                    print(
                        f"Book borrowed successfully! on {borrowed_on} date and due date is {due_on}"
                    )
                    break
                elif member.can_borrow() == False:
                    raise BorrowLimitError("You are exceeding your borrowing limit!")
                    break
            elif book.book_id == book_id and book.is_available == False:
                raise BookNotAvailableError("Book is already borrowed!")
                break
        else:
            raise BookNotAvailableError("Book is not available in Library!")

    def return_book(self, book_id):
        for book in self.books:
            if book.book_id == book_id:
                for loan in self.loans:
                    if loan.book.book_id == book_id and loan.returned_on is None:
                        loan.member.current_loan_list.remove(loan)
                        loan.returned_on = date.today()
                        book.is_available = True
                        print("Book returned successfully!")
                        return

                raise BookNotBorrowedError("This book is not currently checked out!")

        raise ValueError("Book ID not found in the Library.")

    def overdue_loans(self):
        today = date.today()
        found = False
        for loan in self.loans:
            if loan.is_overdue(today):
                found = True
                print(
                    f"Book: {loan.book.title} | Member: {loan.member.name} | Days Late: {loan.days_late(today)} | Fine: {loan.fine(today)}"
                )
        if not found:
            print("No overdue loan found!")

    def list_books(self):
        print("==========Library Books==========")
        for index, book in enumerate(self.books):
            print(f"Book NO: {index + 1}")
            print(f"Book Title: {book.title}")
            print(f"Book ID: {book.book_id}")
            print(f"Book Author: {book.author}")
            print(f"Book Availability: {book.is_available}")
            print()

    def save_to_json(self):
        books_list = []
        for book in self.books:
            books_list.append({
                "book_id" : book.book_id,
                "title" : book.title,
                "author" : book.author,
                "is_available" : book.is_available
            })

        members_list = []
        for member in self.members:
            if isinstance(member, StudentMember):
                member_type = "student"
            elif isinstance(member, StaffMember):
                member_type = "staff"
            else:
                member_type = "regular"

            members_list.append({
                "member_id" : member.member_id,
                "name" : member.name,
                "member_type" : member_type
                })

        loans_list = []
        for loan in self.loans:
            loans_list.append({
                "member_id" : loan.member.member_id,
                "book_id" : loan.book.book_id,
                "borrowed_on" : loan.borrowed_on.isoformat()
                if loan.borrowed_on
                else None,
                "due_on" : loan.due_on.isoformat()
                if loan.due_on
                else None,
                "returned_on" : loan.returned_on.isoformat()
                if loan.returned_on
                else None
            })

        data = {"books" : books_list, "members" : members_list, "loans" : loans_list}

        with open("library_data.json", "w") as f:
            json.dump(data, f, indent=4)
            print("Data saved successfully!")

    def load_data(self):
        try:
            with open("library_data.json", "r") as f:
                data = json.load(f)

            # Clear existing data before loading
            self.books = []
            self.members = []
            self.loans = []

            # Dictionaries to find objects using their IDs
            books_dict = {}
            members_dict = {}

            # 1. Load books
            for book_data in data["books"]:
                book = Book(
                    book_data["book_id"],
                    book_data["title"],
                    book_data["author"],
                    book_data["is_available"],
                )

                self.books.append(book)
                books_dict[book.book_id] = book

            # 2. Load members
            for member_data in data["members"]:
                member_id = member_data["member_id"]
                name = member_data["name"]
                member_type = member_data["member_type"]

                if member_type == "student":
                    member = StudentMember(member_id, name)

                elif member_type == "staff":
                    member = StaffMember(member_id, name)

                else:
                    member = Member(member_id, name)

                self.members.append(member)
                members_dict[member.member_id] = member

            # 3. Load loans
            for loan_data in data["loans"]:
                book_id = loan_data["book_id"]
                member_id = loan_data["member_id"]

                book = books_dict[book_id]
                member = members_dict[member_id]

                borrowed_on = (
                    date.fromisoformat(loan_data["borrowed_on"])
                    if loan_data["borrowed_on"] is not None
                    else None
                )

                due_on = (
                    date.fromisoformat(loan_data["due_on"])
                    if loan_data["due_on"] is not None
                    else None
                )

                returned_on = (
                    date.fromisoformat(loan_data["returned_on"])
                    if loan_data["returned_on"] is not None
                    else None
                )

                loan = Loan(book, member, borrowed_on, due_on, returned_on)

                self.loans.append(loan)

                # Restore only active loans to the member
                if returned_on is None:
                    member.current_loan_list.append(loan)

            print("Library data loaded successfully!")

        except FileNotFoundError:
            print("No saved library data found.")

        except (json.JSONDecodeError, KeyError, TypeError) as e:
            print(f"Error loading library data: {e}")

    def menu(self):
        while True:
            print("\n===== Library Management System =====")
            print("1) Add book")
            print("2) Add member")
            print("3) Borrowing")
            print("4) Returning")
            print("5) List books")
            print("6) Overdue")
            print("7) Save")

            choice = input("Please enter what you want: ")
            try:
                if choice == "1":
                    book_id = input("Enter book ID: ")
                    title = input("Enter book title: ")
                    author = input("Enter author: ")
                    is_available = input("Enter availability: ")

                    book = Book(book_id, title, author, is_available)
                    self.add_book(book)

                elif choice == "2":
                    member_id = input("Enter ID:")
                    name = input("Please enter name: ")
                    member_type = input("Choose member type (student/staff/regular): ").strip().lower()

                    if member_type == "student":
                        member = StudentMember(member_id, name)
                    elif member_type == "staff":
                        member = StaffMember(member_id, name)
                    elif member_type == "regular":
                        member = Member(member_id, name)
                    else:
                        print("Invalid member type! Please try again.")
                        continue

                    self.add_member(member)

                elif choice == "3":
                    member_id = input("Please enter member id: ")
                    book_id = input("Please enter book id: ")
                    self.borrow(member_id, book_id)

                elif choice == "4":
                    book_id = input("Please enter book id: ")
                    self.return_book(book_id)

                elif choice == "5":
                    self.list_books()

                elif choice == "6":
                    self.overdue_loans()

                elif choice == "7":
                    self.save_to_json()
                    print("Saving and quitting...")
                    break

                else:
                    print("Invalid choice. Please try again.")
                    continue

            except ValueError:
                print("Please enter correct input!")

            except BorrowLimitError:
                print("You are exceeding your borrow limit!")

            except BookNotAvailableError:
                print("Book is not available in library!")

            except BookNotBorrowedError:
                print("This book is not checked out yet!")


class Loan:
    def __init__(self, book, member, borrowed_on, due_on, returned_on):
        self.book = book
        self.member = member
        self.borrowed_on = borrowed_on
        self.due_on = due_on
        self.returned_on = returned_on

    def is_overdue(self, today):
        if (self.returned_on is not None) and (self.returned_on > self.due_on):
            return True
        elif (self.returned_on is None) and (today > self.due_on):
            return True
        else:
            return False

    def days_late(self, today):
        if (self.returned_on is not None) and (self.returned_on > self.due_on):
            over_due_days = self.returned_on - self.due_on
            return over_due_days.days
        elif (self.returned_on is None) and (today > self.due_on):
            over_due_days = today - self.due_on
            return over_due_days.days
        else:
            return 0

    def fine(self, today):
        if (self.returned_on is not None) and (self.returned_on > self.due_on):
            over_due_days = self.returned_on - self.due_on
            fine = over_due_days.days * 10
            return fine
        elif (self.returned_on is None) and (today > self.due_on):
            over_due_days = today - self.due_on
            fine = over_due_days.days * 10
            return fine
        else:
            return 0


if __name__ == "__main__":
    library = Library()
    library.load_data()
    library.menu()
