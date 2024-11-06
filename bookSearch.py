from datetime import datetime, timedelta
import re
from check_validate import check_string_validate, check_year_validate, check_date_validate, check_isbn_validate, check_phone_number_validate

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
    
    def isFull(self) -> bool:
        if self.static_id > self.MAX_STATIC_ID:
            return True
        else:
            return False

    def increase_static_id(self) -> bool:
        if self.static_id <= self.MAX_STATIC_ID:
            self.static_id += 1
            return True
        # 99 초과
        else:
            return False
    
    # 책 검색
    def search_book(self):

        if not self.book_data:
            print("등록된 책이 존재하지 않습니다.")
            return False

        search_book = input("검색할 책의 제목이나 저자를 입력하세요: ")
        
        if "/" in search_book or "\\" in search_book:
            print('ERROR: 책의 제목 또는 저자에는 특수문자 "/" 또는 "\\"을 입력할 수 없습니다.')
            return False
        
        if search_book == "X":
            print("검색을 중단하며 메인 프롬프트로 돌아갑니다.")
            return False
        
        bookData.search_content_book(search_book)

    def search_content_book(self, search_book):
        search_results = [
            book for book in self.book_data 
            if search_book.lower() in book.title.lower() or search_book.lower() in book.writer.lower()
        ]

        if not search_results:
            answer = input("해당 책이 존재하지 않습니다. 다시 검색하시겠습니까?(Y/N) :")
            
            if answer == "Y":
                self.search_book()
            else:
                print("검색을 중단하며 메인 프롬프트로 돌아갑니다.")
                return False
        

        print(BookRecord.get_header())
        print("\n")
        for book in search_results:
            print(book.to_str(today=self.today, contain_borrow=True))
        print("\n")
        return True
    

    def check_string_validate(self, field_name, value):
        # 1. 문자열의 길이가 1 이상인지 확인
        if len(value) < 1:
            return False, f"{field_name}는 1자 이상이어야 합니다."
        # 2. 문자열이 공백인지 확인
        if value.strip() == "":
            return False, f"{field_name}는 공백만 포함할 수 없습니다."
        # 3. 허용되지 않는 특수 기호가 포함되어 있는지 확인
        if '/' in value or '\\' in value:
            return False, f"{field_name}에 '/' 또는 '\\' 특수 문자는 허용되지 않습니다."
        # 4. 문자열이 "X"와 일치하는지 확인
        if value == "X":
            return False, f"{field_name}에 'X'는 허용되지 않습니다."
        return True, ""

    def check_year_validate(self, year):
        # 1. 입력값이 숫자인지 확인
        if not year.isdigit():
            return False, "출판 연도는 숫자여야 합니다."
        year_int = int(year)
        # 2. 범위 확인
        current_year = datetime.now().year
        if year_int < 1583 or year_int > current_year:
            return False, f"출판 연도는 1583년부터 {current_year}년 사이여야 합니다."
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
        # ISBN이 두 자리 숫자(00~99)로 구성되어 있는지 확인
        if len(isbn) != 2 or not isbn.isdigit():
            return False, "ISBN은 두 자리 숫자 (00 ~ 99)여야 합니다."
        return True, ""

    def check_phone_number_validate(self, phone_number):
        # 정규표현식으로 010-XXXX-XXXX 형식 확인
        pattern = r'^010-\d{4}-\d{4}$'
        if re.fullmatch(pattern, phone_number):
            return True, ""
        return False, "전화번호는 010-XXXX-XXXX 형식이어야 합니다."

    def check_record_validate(self ,book):
        # ISBN, 책 제목, 저자, 출판사, 출판년도, 등록 날짜 유효성 검사
        is_valid, error_message = self.check_isbn_validate(book["ISBN"])
        if not is_valid:
            return False, f"ISBN 에러: {error_message}"
        
        is_valid, error_message = check_string_validate("제목", book["title"])
        if not is_valid:
            return False, f"제목 에러: {error_message}"
        
        is_valid, error_message = check_string_validate("저자", book["author"])
        if not is_valid:
            return False, f"저자 에러: {error_message}"
        
        is_valid, error_message = check_string_validate("출판사", book["publisher"])
        if not is_valid:
            return False, f"출판사 에러: {error_message}"
        
        is_valid, error_message = check_year_validate(book["year"])
        if not is_valid:
            return False, f"출판년도 에러: {error_message}"
        
        is_valid, error_message = check_date_validate(book["등록날짜"])
        if not is_valid:
            return False, f"등록 날짜 에러: {error_message}"

        # 대출 중인 경우 추가 유효성 검사
        if book.get("대출자") and book.get("대출자 전화번호"):
            # 대출자, 전화번호, 대출 날짜, 반납 예정일 검사
            is_valid, error_message = check_string_validate("대출자", book["대출자"])
            if not is_valid:
                return False, f"대출자 에러: {error_message}"
            
            is_valid, error_message = check_phone_number_validate(book["대출자 전화번호"])
            if not is_valid:
                return False, f"전화번호 에러: {error_message}"
            
            is_valid, error_message = check_date_validate(book["대출날짜"])
            if not is_valid:
                return False, f"대출 날짜 에러: {error_message}"
            
            is_valid, error_message = check_date_validate(book["반납 예정일"])
            if not is_valid:
                return False, f"반납 예정일 에러: {error_message}"
        else:
            # 대출자 정보가 없는 경우 대출 관련 필드가 비어있는지 확인
            if book.get("대출날짜") or book.get("반납 예정일") or book.get("대출자") or book.get("대출자 전화번호"):
                return False, "대출 관련 정보가 일부 누락되었습니다."

        return True, ""

    def check_book_id_validate(self, book_id, book_data):
        # 책 ID가 숫자로 구성되었는지 확인
        if not book_id.isdigit():
            return False, "책 ID는 숫자만 포함해야 합니다."
        
        # 책 ID가 음수가 아니고, 99 이하인지 확인
        book_id_int = int(book_id)
        if book_id_int < 0 or book_id_int > 99:
            return False, "책 ID는 0에서 99 사이여야 합니다."
        
        "중복된 책 ID가 존재합니다."
        
        return True, ""
    # 데이터 무결성 검사
    def check_data_integrity(self) -> tuple[bool, str]:
        # 데이터 무결성 검사를 수행하고 결과를 반환
        for book in self.book_data:
            is_valid, message = self.check_record_validate(book)
            if not is_valid:
                return (False, f"도서 '{book.title}'의 무결성 오류: {message}")
        return (True, None)



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

    bookData.search_book()
    