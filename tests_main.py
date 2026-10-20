import json
from datetime import date, timedelta
import pytest

from main import (
    Book,
    Member,
    StudentMember,
    StaffMember,
    Loan,
    Library,
    BookNotAvailableError,
    BorrowLimitError,
    BookNotBorrowedError,
)


@pytest.fixture
def setup_library():
    library = Library()

    book1 = Book("B1", "Python Basics", "John Smith", True)
    book2 = Book("B2", "Learn OOP", "Jane Doe", True)

    member = StudentMember("M1", "Ali")

    library.add_book(book1)
    library.add_book(book2)
    library.add_member(member)

    return library, book1, book2, member


# Test 1: A member can borrow an available book
def test_borrow_book_success(setup_library):
    library, book1, book2, member = setup_library

    library.borrow("M1", "B1")

    assert book1.is_available is False
    assert len(member.current_loan_list) == 1
    assert member.current_loan_list[0].book == book1


# Test 2: A member cannot borrow an already borrowed book
def test_borrow_unavailable_book(setup_library):
    library, book1, book2, member = setup_library

    library.borrow("M1", "B1")

    with pytest.raises(BookNotAvailableError):
        library.borrow("M1", "B1")


# Test 3: A member cannot exceed their borrowing limit
def test_borrow_limit(setup_library):
    library, book1, book2, member = setup_library

    member.current_loan_list = [
        Loan(
            Book(f"X{i}", f"Book {i}", "Author", True),
            member,
            date.today(),
            date.today() + timedelta(days=14),
            None,
        )
        for i in range(3)
    ]

    with pytest.raises(BorrowLimitError):
        library.borrow("M1", "B1")


# Test 4: Returning a borrowed book works
def test_return_book_success(setup_library):
    library, book1, book2, member = setup_library

    library.borrow("M1", "B1")
    library.return_book("B1")

    assert book1.is_available is True
    assert len(member.current_loan_list) == 0
    assert library.loans[0].returned_on == date.today()


# Test 5: Returning a book that was not borrowed raises an error
def test_return_unborrowed_book(setup_library):
    library, book1, book2, member = setup_library

    with pytest.raises(BookNotBorrowedError):
        library.return_book("B1")


# Test 6: An overdue loan is detected correctly
def test_overdue_detection():
    member = Member("M1", "Ali")
    book = Book("B1", "Python Basics", "John Smith", True)

    loan = Loan(
        book,
        member,
        date.today() - timedelta(days=20),
        date.today() - timedelta(days=6),
        None,
    )

    assert loan.is_overdue(date.today()) is True


# Test 7: Fine is calculated at Rs 10 per late day
def test_fine_calculation():
    member = Member("M1", "Ali")
    book = Book("B1", "Python Basics", "John Smith", True)

    loan = Loan(
        book,
        member,
        date.today() - timedelta(days=20),
        date.today() - timedelta(days=5),
        None,
    )

    assert loan.fine(date.today()) == 50


# Test 8: Student and staff borrowing limits differ
def test_member_borrowing_limits():
    student = StudentMember("S1", "Ali")
    staff = StaffMember("T1", "Sara")

    assert student.can_borrow() is True
    assert staff.can_borrow() is True

    student.current_loan_list = [object(), object(), object()]
    staff.current_loan_list = [
        object() for _ in range(10)
    ]

    assert student.can_borrow() is False
    assert staff.can_borrow() is False


# Test 9: Library data can be saved to JSON
def test_save_to_json(setup_library, tmp_path, monkeypatch):
    library, book1, book2, member = setup_library
    monkeypatch.chdir(tmp_path)

    library.save_to_json()

    file_path = tmp_path / "library_data.json"

    assert file_path.exists()

    with open(file_path, "r") as file:
        data = json.load(file)

    assert len(data["Books"]) == 2
    assert len(data["Members"]) == 1
    assert "Loans" in data


# Test 10: Saved library data can be loaded again
def test_load_from_json(setup_library, tmp_path, monkeypatch):
    library, book1, book2, member = setup_library
    monkeypatch.chdir(tmp_path)

    library.borrow("M1", "B1")
    library.save_to_json()

    new_library = Library()
    new_library.load_books()

    assert len(new_library.books) == 2
    assert len(new_library.members) == 1
    assert len(new_library.loans) == 1

    loaded_book = next(
        book for book in new_library.books
        if book.book_id == "B1"
    )

    loaded_member = new_library.members[0]

    assert loaded_book.is_available is False
    assert len(loaded_member.current_loan_list) == 1
