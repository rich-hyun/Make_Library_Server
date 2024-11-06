from datetime import datetime, timedelta
import re

class MyDate(object):
    def __init__(self, year, month, day):
        assert type(year) is int
        assert type(month) is int
        assert type(day) is int

        assert 1852 < year, "년도는 1852보다 큰 정수여야 합니다."
        assert 1 <= month <= 12, "월은 1과 12사이의 정수여야 합니다."
        assert self.validate_day(year, month, day), "년도와 월에 대해 일이 올바른 범위를 벗어났습니다."

        self.year = year
        self.month = month
        self.day = day

    def __str__(self):
        return f"{self.year}-{self.month}-{self.day}"

    @classmethod
    def from_str(self, text: str) -> object:
        try:
            year, month, day = map(int, text.split("-"))

            assert 1852 < year, "년도는 1852보다 큰 정수여야 합니다."
            assert 1 <= month <= 12, "월은 1과 12사이의 정수여야 합니다."
            assert self.validate_day(year, month, day), "년도와 월에 대해 일이 올바른 범위를 벗어났습니다."

            return MyDate(year, month, day)

        except Exception as e:
            print(e)
            print("텍스트 " + text +"을(를) 날짜로 변환할 수 없습니다.")

            return None

    @classmethod
    def is_leap_year(self, year):
        if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
            return True
        return False

    @classmethod
    def validate_day(self, year, month, day):
        # 각 달의 일수 (평년 기준)
        days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

        # 2월의 일수를 윤년 여부에 따라 업데이트
        if self.is_leap_year(year):
            days_in_month[1] = 29

        # month와 day의 유효성을 체크
        if month < 1 or month > 12:
            return False
        if day < 1 or day > days_in_month[month - 1]:
            return False

        return True

    # 연산자 구현
    def __eq__(self, other):
        if not isinstance(other, MyDate):
            return False
        return (self.year, self.month, self.day) == (other.year, other.month, other.day)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __lt__(self, other):
        if not isinstance(other, MyDate):
            return False
        return (self.year, self.month, self.day) < (other.year, other.month, other.day)

    def __le__(self, other):
        if not isinstance(other, MyDate):
            return False
        return (self.year, self.month, self.day) <= (other.year, other.month, other.day)

    def __gt__(self, other):
        if not isinstance(other, MyDate):
            return False
        return (self.year, self.month, self.day) > (other.year, other.month, other.day)

    def __ge__(self, other):
        if not isinstance(other, MyDate):
            return False
        return (self.year, self.month, self.day) >= (other.year, other.month, other.day)
    
    def add_days(self, days):
        new_date = datetime(self.year, self.month, self.day) + timedelta(days=days)
        return MyDate(new_date.year, new_date.month, new_date.day)


class BookRecord(object):
    def __init__(self, book_id: int,
                 isbn: int, title: str,
                 writer: str, publisher: str,
                 published_year: int, register_date: MyDate,
                 borrower_name: str=None,
                 borrower_phone_number: str=None,
                 borrow_date: MyDate=None,
                 return_date: MyDate=None):

        self.book_id = book_id
        self.isbn = isbn
        self.title = title
        self.writer = writer
        self.publisher = publisher
        self.published_year = published_year
        self.register_date = register_date
        self.borrower_name = borrower_name
        self.borrower_phone_number = borrower_phone_number
        self.borrow_date = borrow_date
        self.return_date = return_date

        self.is_borrowing: bool = borrower_name is not None

    def __str__(self) -> str:
        return f"{self.book_id} / {self.isbn} / {self.title} \
/ {self.writer} / {self.publisher} \
/ {self.published_year} / {str(self.register_date)}"


    def borrow_book(self, borrower_name: str, borrower_phone_number: str, current_date: MyDate) -> None:
        assert not self.is_borrowing, "이미 대출중인 도서입니다."

        # 대출 process
        self.borrower_name = borrower_name
        self.borrower_phone_number = borrower_phone_number
        self.is_borrowing = True

    def return_book(self) -> None:
        assert self.is_borrowing, "대출 정보가 없는 도서입니다."

        # 반납 process
        self.is_borrowing = False
        self.borrower_name = None
        self.borrower_phone_number = None

    def to_str(self, today: MyDate, contain_borrow=True) -> str:
        """_summary_
        Returns the corresponding book record as a string in printable form

        Args:
            contain_borrow (bool, optional): Whether to include loan/return information when converting strings. Defaults to True.
        """
        return f"{self.book_id} / {self.isbn} \
/ {self.title} / {self.writer} \
/ {self.publisher} / {self.published_year} \
/ {str(self.register_date)}" \
+ (f" / {self.borrower_phone_number} {self.borrower_name} \
/ {str(self.borrow_date)} ~ {str(self.return_date)}" if self.is_borrowing and contain_borrow else "") \
+ (" *" if self.return_date < today else "")


    @classmethod
    def get_header(contain_id: bool=True,
                   contain_isbn: bool=True,
                   contain_register_date: bool=True,
                   contain_borrow_info: bool=True) -> str:
        """_summary_
        Return a header string
        Args:
            contain_id (bool): Whether to include Book ID
            contain_isbn (bool): Whether to include Book ISBN
            contain_register_date (bool): Whether to include Book Registration Date
            contain_borrow_info (bool): Whether to include information about the book's borrower

        Returns:
            str: A generated header string
        """
        return f"<{'고유번호 / ' if contain_id else ''}{'ISBN / ' if contain_isbn else ''}제목 / 저자 / 출판사 / 출판년도{' / 등록날짜' if contain_register_date else ''}{' / 대출기간' if contain_borrow_info else ''}>"


class BookData(object):
    def __init__(self, file_path, today: MyDate):
        self.file_path = file_path
        self.today = today
        # 파일 읽어서 book_data 리스트 생성 (임시)
        self.book_data = []
        # 파일 읽어서 가장 큰 ID 저장
        self.static_id = 0

        # constant
        self.MAX_STATIC_ID = 99

    def read_data_file(self):
        """
        데이터 파일 읽음
        """
        book_records = []

        with open(self.file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

            # static id
            self.static_id = int(lines[0].strip())

            for line in lines[1:]:
                data = line.strip().split("/")

                book_id = int(data[0])
                isbn = int(data[1])
                title = data[2]
                writer = data[3]
                publisher = data[4]
                published_year = int(data[5])
                register_date = MyDate.from_str(data[6])

                borrower_name = data[7] if len(data[7]) > 0 else None
                borrower_phone_number = data[8] if len(data[7]) > 0 else None
                borrow_date = MyDate.from_str(data[9]) if len(data[7]) > 0 else None
                return_date = MyDate.from_str(data[10]) if len(data[7]) > 0 else None

                book_record = BookRecord(
                    book_id, isbn, title, writer, publisher, published_year,
                    register_date, borrower_name, borrower_phone_number,
                    borrow_date, return_date
                )

                book_records.append(book_record)

            self.book_data = book_records

    def check_data_file(self):
        """
        파일 무결성 검사
        """
        pass

    def get_data(self):
        return self.book_data

    def get_static_id(self):
        return self.static_id

    def increase_static_id(self) -> bool:
        if self.static_id <= self.MAX_STATIC_ID:
            self.static_id += 1
            return True
        # 99 초과
        else:
            return False


    def borrow_book(self):
        name = input("대출자의 이름을 입력해주세요: ")
        validation_info, message = self.check_string_validate("대출자 이름",name)
        if not validation_info:
            print(message)
            return False
        
        phone = input("대출자의 전화번호를 입력해주세요: ")
        validation_info, message = self.check_phone_number_validate(phone)
        if not validation_info:
            print(message)
            return False

        overdue_books = self.check_overdue_books(name, phone)
        if overdue_books:
            print("연체중인 책을 보유하고 있어 대출이 불가능합니다.")
            print("아래 목록은 대출자가 현재 연체중인 책입니다.")
            print(BookRecord.get_header(contain_borrow_info=True))
            for book in overdue_books:
                print(book.to_str(self.today, contain_borrow=True))
            return False

        borrowed_count = self.count_borrowed_books(name, phone)
        max_limit = 3
        if borrowed_count >= max_limit:
            print(f"대출 중인 책이 {borrowed_count}권 있으며 더 이상 대출이 불가능합니다.")
            print(BookRecord.get_header(contain_borrow_info=True)) 
            for book in self.book_data:
                if book.borrower_name == name and book.borrower_phone_number == phone:
                    print(book.to_str(self.today, contain_borrow=True))
            return False 
        else:
            print(f"대출중인 책이 {borrowed_count}권 있으며, {max_limit - borrowed_count}권 대출이 가능합니다.")


        book_id = input("대출할 책의 고유번호를 입력해주세요: ")
        if book_id == 'X':
            print("대출이 취소되었습니다. 메인프롬프트로 돌아갑니다.")
            return False 
        validation_info, message = self.check_book_id_validate(book_id, self.book_data)
        if not validation_info:
            print(message)
            return False
        
        book = next((b for b in self.book_data if str(b.book_id) == book_id), None)
        
        if book is None:
            print("ERROR: 해당 고유번호를 가진 책이 존재하지 않습니다.")
            return False

        print("책이 특정되었습니다.")
        print(BookRecord.get_header(contain_borrow_info=False))
        print(book.to_str(self.today, contain_borrow=False)) 
        
        if book.borrower_name:
            print("이미 다른 사용자에 의해 대출 중이므로 대출이 불가능합니다.")
            return False

        confirm = input("위 책을 대출할까요? (Y/N): ")
        if confirm == "Y":
            borrow_date = self.today
            due_date = self.today.add_days(7)
            book.borrower_name = name
            book.borrower_phone_number = phone
            book.borrow_date = borrow_date
            book.return_date = due_date
            print(f"대출이 완료되었습니다. 반납 예정일은 {due_date} 입니다.")
            self.save_data_to_file()
            return True
        else:
            print("대출이 취소되었습니다.")
            return False

    def check_overdue_books(self, name, phone):
        overdue_books = []
        for book in self.book_data:
            if book.borrower_name == name and book.borrower_phone_number == phone:
                if book.return_date and book.return_date < self.today:
                    overdue_books.append(book)
        return overdue_books

    def count_borrowed_books(self, name, phone):
        return sum(1 for book in self.book_data if book.borrower_name == name and book.borrower_phone_number == phone)
    

###############################################################################################################################

    def delete_book(self):
        del_book_id = input("삭제하고자 하는 책의 고유번호를 입력해주세요: ")
        if del_book_id == 'X':
            print("삭제를 취소하였습니다. 메인프롬프트로 돌아갑니다.")
            return False
        
        if len(del_book_id) < 1:
            print("ERROR: 1글자 이상 입력해주세요.")
            return False
        
        if del_book_id.strip() == "":
            print("ERROR: 책의 고유번호는 공백일 수 없습니다.")
            return False

        validation_info, message = self.check_book_id_validate(del_book_id,self.book_data)
        if not validation_info:
            print(message)
            return False

        del_book_id = int(del_book_id)
        del_book_data = next((b for b in self.book_data if b.book_id == del_book_id), None)
        if del_book_data is None:
            print("ERROR: 해당 고유번호를 가진 책이 존재하지 않습니다.")
            return False
        elif self.check_overdue_delete(del_book_id):
            print("ERROR: 해당 책은 대출중이므로 삭제할 수 없습니다.")
            return False
        else:
            print("책이 특정되었습니다.")
            print(BookRecord.get_header(contain_borrow_info=False))
            print(del_book_data.to_str(self.today, contain_borrow=False)) 

            if self.confirm_delete(del_book_data):
                self.save_data_to_file()
                return True
            else:
                return False

    def check_overdue_delete(self, book_id):
        for book in self.book_data:
            if book.book_id == book_id and book.return_date:
                return True
        return False

    def confirm_delete(self, del_book_data):
        confirm = input("삭제하면 되돌릴 수 없습니다. 정말로 삭제하시겠습니까?(Y/N): ")
        if confirm == "Y":
            self.book_data.remove(del_book_data)
            print("삭제가 완료되었습니다. 메인프롬프트로 돌아갑니다.")
            return True
        else:
            print("삭제를 취소하였습니다. 메인프롬프트로 돌아갑니다.")
            return False

################################################################################################################



    def check_string_validate(self, field_name, value):
        # 1. 문자열의 길이가 1 이상인지 확인
        if len(value) < 1:
            return False, f"책의 {field_name}은 1글자 이상이어야 합니다."
        # 2. 문자열이 공백인지 확인
        if value.strip() == "":
            return False, f"책의 {field_name}은 공백일 수 없습니다."
        # 3. 허용되지 않는 특수 기호가 포함되어 있는지 확인
        if '/' in value or '\\' in value:
            return False, f"책의 {field_name}에 특수문자 \"/\" 또는 \"\\\"는 허용되지 않습니다."

    def check_year_validate(self, year):
        # 1. 입력값이 숫자인지 확인
        if not year.isdigit():
            return False, "ERROR: 책의 출판년도는 오로지 숫자로만 구성되어야 합니다."
    
        # 2. 출판년도는 4자리 숫자여야 함을 확인
        if len(year) != 4:
            return False, "ERROR: 책의 출판년도는 4자리 양의 정수여야 합니다."
        
        year_int = int(year)
        current_year = today.year  # 현재 연도를 확인하는 변수

        # 3. 출판년도 범위 확인
        if year_int < 1583:
            return False, "ERROR: 책의 출판년도는 1583년 이후인 4자리 양의 정수여야 합니다."
        elif year_int > current_year:
            return False, f"ERROR: 책의 출판년도는 현재연도({current_year}년)보다 미래일 수 없습니다."
        
        return True, ""

    def check_date_validate(self, date_str):
        try:
            # 날짜 형식이 유효한지 확인 (YYYY-MM-DD 형식으로 가정)
            date = datetime.strptime(date_str, "%Y-%m-%d")
            # 연도가 1583 이상 9999 이하인지 확인
            if not (1583 <= date.year <= 9999):
                return False, "날짜는 1583년부터 9999년 사이여야 합니다."
            return True, ""
        except ValueError:
            return False, "날짜 형식이 올바르지 않습니다. (예: YYYY-MM-DD)"

    def check_isbn_validate(self, isbn):
        # ISBN이 1글자 이상인지 확인
        if len(isbn) < 1:
            return False, "1글자 이상 입력해주세요."

        # ISBN이 공백인지 확인
        if not isbn.strip():  # 공백을 제거한 후 빈 문자열인지 확인
            return False, "책의 ISBN은 공백일 수 없습니다."
        # ISBN이 두 자리 숫자(00~99)로 구성되어 있는지 확인
        if len(isbn) != 2 or not isbn.isdigit():
            return False, "ISBN은 두 자리 숫자여야 합니다."
        return True, ""

    def check_phone_number_validate(self, phone_number):
        # 정규표현식으로 010-XXXX-XXXX 형식 확인
        pattern = r'^010-\d{4}-\d{4}$'
        if re.fullmatch(pattern, phone_number):
            return True, ""
        return False, "전화번호는 010-XXXX-XXXX 형식이어야 합니다."

    def check_record_validate(self, book: BookRecord):
        # ISBN 유효성 검사
        is_valid, error_message = self.check_isbn_validate(str(book.isbn))
        if not is_valid:
            return False, f"ISBN 에러: {error_message}"

        # 책 제목 유효성 검사
        is_valid, error_message = self.check_string_validate("제목", book.title)
        if not is_valid:
            return False, f"제목 에러: {error_message}"

        # 저자 유효성 검사
        is_valid, error_message = self.check_string_validate("저자", book.writer)
        if not is_valid:
            return False, f"저자 에러: {error_message}"

        # 출판사 유효성 검사
        is_valid, error_message = self.check_string_validate("출판사", book.publisher)
        if not is_valid:
            return False, f"출판사 에러: {error_message}"

        # 출판년도 유효성 검사
        is_valid, error_message = self.check_year_validate(str(book.published_year))
        if not is_valid:
            return False, f"출판년도 에러: {error_message}"

        # 등록 날짜 유효성 검사
        is_valid, error_message = self.check_date_validate(str(book.register_date))
        if not is_valid:
            return False, f"등록 날짜 에러: {error_message}"

        # 대출 중인 경우 추가 유효성 검사
        if book.is_borrowing:
            # 대출자 유효성 검사
            is_valid, error_message = self.check_string_validate("대출자", book.borrower_name)
            if not is_valid:
                return False, f"대출자 에러: {error_message}"

            # 전화번호 유효성 검사
            is_valid, error_message = self.check_phone_number_validate(book.borrower_phone_number)
            if not is_valid:
                return False, f"전화번호 에러: {error_message}"

            # 대출 날짜 유효성 검사
            is_valid, error_message = self.check_date_validate(str(book.borrow_date))
            if not is_valid:
                return False, f"대출 날짜 에러: {error_message}"

            # 반납 예정일 유효성 검사
            is_valid, error_message = self.check_date_validate(str(book.return_date))
            if not is_valid:
                return False, f"반납 예정일 에러: {error_message}"
        else:
            # 대출 중이 아닌 경우, 대출 관련 필드가 모두 None인지 확인
            if book.borrower_name or book.borrower_phone_number or book.borrow_date or book.return_date:
                return False, "대출 중이 아닌데 대출 관련 정보가 존재합니다."

        return True, ""
       

    def check_book_id_validate(self, book_id, book_data):
        # 1. 입력값이 있는지 확인
        if len(book_id) == 0:
            return False, "1글자 이상 입력해주세요."
        
        # 2. 입력값이 공백으로만 구성되지 않았는지 확인
        if book_id.isspace():
            return False, "책의 고유번호는 공백일 수 없습니다."
        
        # 3. 고유번호에 허용되지 않는 특수문자가 포함되어 있는지 확인
        if "/" in book_id or "\\" in book_id:
            return False, "책의 고유번호에는 특수문자 \"/\" 또는 \"\\\"을 입력할 수 없습니다."
        
        # 4. 고유번호가 숫자로만 구성되어 있는지 확인
        if not book_id.isdigit():
            return False, "고유번호는 숫자여야 합니다."
        
        # 5. 고유번호가 0에서 99 사이인지 확인
        book_id_int = int(book_id)
        if book_id_int < 0 or book_id_int > self.MAX_STATIC_ID:
            return False, "고유번호는 0에서 99 사이여야 합니다."
        
        return True, ""    
    # 데이터 무결성 검사
    def check_data_integrity(self) -> tuple[bool, str]:
        # 데이터 무결성 검사를 수행하고 결과를 반환
        for book in self.book_data:
            is_valid, message = self.check_record_validate(book)
            if not is_valid:
                return (False, f"도서 '{book.title}'의 무결성 오류: {message}")
        return (True, None)
    
    def input_isbn(self) -> str:
        isbn = input("책의 ISBN을 입력해주세요: ").strip()
        is_valid, error_message = self.check_isbn_validate(isbn)
        if is_valid:
            return isbn
        else:
            print(f"ERROR: {error_message}")
            return None

    def input_bookName(self) -> str:
        title = input("책의 제목을 입력해주세요: ").strip()
        is_valid, error_message = self.check_string_validate("제목", title)
        if is_valid:
            return title
        else:
            print(f"ERROR: {error_message}")
            return None

    def input_author(self) -> str:
        author = input("책의 저자를 입력해주세요: ").strip()
        is_valid, error_message = self.check_string_validate("저자", author)
        if is_valid:
            return author
        else:
            print(f"ERROR: {error_message}")
            return None

    def input_publisher(self) -> str:
        publisher = input("출판사를 입력해주세요: ").strip()
        is_valid, error_message = self.check_string_validate("출판사", publisher)
        if is_valid:
            return publisher
        else:
            print(f"ERROR: {error_message}")
            return None

    def input_year(self) -> int:
        year = input("출판년도를 입력해주세요: ").strip()
        is_valid, error_message = self.check_year_validate(year, self.today.year)
        if is_valid:
            return int(year)
        else:
            print(f"ERROR: {error_message}")
            return None
    


    def input_book_id() -> str:
        book_id = input("책의 고유번호를 입력해주세요").strip()

        # 공백 확인
        if not book_id:
            print("ERROR: 책의 고유번호는 공백일 수 없습니다.")
            return None

        # 길이 확인
        if len(book_id) < 1:
            print("ERROR: 1글자 이상 입력해주세요.")
            return None

        # 숫자 여부 확인
        if not book_id.isdigit():
            print("ERROR: 고유번호는 숫자여야 합니다.")
            return None

        # 특수문자 검사
        if "/" in book_id or "\\" in book_id:
            print('ERROR: 책의 고유번호에는 특수문자 "/" 또는 "\\"을 입력할 수 없습니다.')
            return None

        return book_id
    
    def input_borrower_name(self) -> str:
        borrower_name = input("대출자 이름을 입력해주세요: ").strip()
        is_valid, error_message = self.check_string_validate("대출자 이름", borrower_name)
        if is_valid:
            return borrower_name
        else:
            print(f"ERROR: {error_message}")
    def input_phone_number(self) -> str:
        phone_number = input("대출자 전화번호를 입력해주세요: ").strip()
        is_valid, error_message = self.check_phone_number_validate(phone_number)
        if is_valid:
            return phone_number
        else:
            print(f"ERROR: {error_message}")

    




    def save_data_to_file(self) -> None:
        """파일에 현재 book_data 리스트를 저장합니다."""
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                # 첫 줄에 static_id 저장
                f.write(f"{self.static_id}\n")

                # 각 BookRecord 객체를 파일에 저장
                for book in self.book_data:
                    f.write(f"{book.book_id}/{book.isbn}/{book.title}/{book.writer}/{book.publisher}/"
                            f"{book.published_year}/{str(book.register_date)}/"
                            f"{book.borrower_name if book.borrower_name else ''}/"
                            f"{book.borrower_phone_number if book.borrower_phone_number else ''}/"
                            f"{str(book.borrow_date) if book.borrow_date else ''}/"
                            f"{str(book.return_date) if book.return_date else ''}\n")
            print("데이터가 파일에 성공적으로 저장되었습니다.")
        except Exception as e:
            print(f"ERROR: 데이터를 파일에 저장하는 중 오류가 발생했습니다. {str(e)}")

    # 디버깅용 책 데이터 출력
    def print_book_debug(self) -> None:
        print("="*10, "BOOK DATA", "="*10)
        print(BookRecord.get_header())
        for book in self.book_data:
            print(book.to_str(today=self.today, contain_borrow=True))
        print("="*30)

def get_today_temp() -> MyDate:
    print("현재 함수는 임시 구현이므로 예외 처리 없음.")
    try:
        year = int(input("year: "))
        month = int(input("month: "))
        day = int(input("day: "))
    except Exception as e:
        print(e)
        return None
    return MyDate(year, month, day)




        

        


if __name__ == "__main__":
    # 현재 날짜 입력
    today = get_today_temp()

    bookData = BookData(file_path="./book_data_temp.txt", today=today)

    # 데이터 파일 읽기
    bookData.read_data_file()

    # 데이터 파일 무결성 검사 (구현 전)
    # 파일 오류나도 알아서 처리, 성공 여부 알 필요 X
    bookData.check_data_file()

    bookData.print_book_debug()

    bookData.borrow_book()