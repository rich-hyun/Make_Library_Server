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

    # 데이터 삽입 인터페이스
    def insert_record(self, BookRecord):
        self.book_data.append(BookRecord)
        self.increase_static_id(self)
        print("성공적으로 책을 추가하였습니다.")

    # 데이터 수정 (업데이트)
    def update_record(self) -> bool:
        print("수정하고자 하는 책의 ISBN을 입력해주세요: ", end="")
        try:
            isbn = input_isbn()
            if not isbn:
                return False  # 입력 실패 시 반환

            isbn = int(isbn)

            # 책 존재 여부 확인
            book_to_update = None
            for book in self.book_data:
                if book.isbn == isbn:
                    book_to_update = book
                    break

            if not book_to_update:
                print("ERROR: 해당 ISBN을 가진 책이 존재하지 않습니다.")
                return False

            # 기존 책 정보 출력
            print("\n책이 특정되었습니다.")
            print(book_to_update.to_str(today=self.today))

            # 새로운 정보 입력
            new_title = input_bookName()
            if not new_title:
                return False

            new_author = input_author()
            if not new_author:
                return False

            new_publisher = input_publisher()
            if not new_publisher:
                return False

            new_year = input_year(self.today.year)
            if not new_year:
                return False

            # 수정 여부 확인
            print("\n수정한 데이터는 복구할 수 없습니다. 정말로 수정하시겠습니까?(Y/N): ", end="")
            confirm = input().strip().upper()
            if confirm != "Y":
                print("수정을 취소하였습니다. 메인 프롬프트로 돌아갑니다.")
                return False

            # 수정 반영
            book_to_update.title = new_title
            book_to_update.writer = new_author
            book_to_update.publisher = new_publisher
            book_to_update.published_year = new_year

            print("수정이 완료되었습니다.")
            self.save_data_to_file()
            return True

        except Exception as e:
            print(f"ERROR: 예상하지 못한 오류가 발생했습니다. {str(e)}")
            return False



    # 데이터 삭제
    def delete_record(self) -> tuple[bool, str]:
        return (True, None)

    # 책 대출
    def borrow_book(self) -> tuple[bool, str]:
        return (True, None)

    # 책 반납
    def return_book(self) -> tuple[bool, str]:
        return (True, None)

    # 데이터 무결성 검사
    def check_data_integrity(self) -> tuple[bool, str]:
        return (True, None)

    # 데이터 저장
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

    def search_isbn(self, isbn: int) -> list:
        matching_books = [book for book in self.book_data if book.isbn == isbn]
        return matching_books


def input_isbn(input_message: str) -> str:
    isbn = input(input_message).strip()
    if not isbn.isdigit() or len(isbn) != 2:
        print("ERROR: 책의 ISBN은 2자리 숫자여야 합니다.")
        return None
    # if "/" in isbn or "\\" in isbn:
    #     print('ERROR: 책의 ISBN에는 특수문자 "/" 또는 "\\"을 입력할 수 없습니다.')
    #     return None
    if not isbn:
        print("ERROR: 책의 ISBN는 공백일 수 없습니다.")
        return None
    return isbn

def input_bookName(input_message: str) -> str:
    title = input(input_message).strip()
    if not title or "/" in title or "\\" in title:
        print('ERROR: 책의 제목에는 특수문자 "/" 또는 "\\"을 입력할 수 없으며, 공백일 수 없습니다.')
        return None
    return title

def input_author(input_message: str) -> str:
    author = input(input_message).strip()
    if not author or "/" in author or "\\" in author:
        print('ERROR: 저자 이름에는 특수문자 "/" 또는 "\\"을 입력할 수 없으며, 공백일 수 없습니다.')
        return None
    return author

def input_publisher(input_message: str) -> str:
    publisher = input(input_message).strip()
    if not publisher or "/" in publisher or "\\" in publisher:
        print('ERROR: 출판사 이름에는 특수문자 "/" 또는 "\\"을 입력할 수 없으며, 공백일 수 없습니다.')
        return None
    return publisher

def input_year(input_message: str) -> int:
    year = input(input_message).strip()
    today_year = str(today).split("-")
    today_year = int(today_year[0])
    if not year.isdigit() or int(year) < 1583 or int(year) > today_year:
        print("ERROR: 출판년도는 1583년 이상, 현재년도 이하의 값이어야 합니다.")
        return None
    return int(year)

def input_response(input_message: str) -> bool:
    response = input(input_message).strip()
    if response == 'Y':
        return True
    return False

def add_book() -> bool:
    if bookData.isFull():
        print("더 이상 추가할 수 없습니다.")
        return False
    
    isbn = input_isbn("추가할 책의 ISBN을 입력하세요: ")
    if not isbn:
        return False
    isbn = int(isbn)
    
    book_info = []
    books = bookData.search_isbn(isbn)
    if not books:
        messages_and_functions = [
            ("추가할 책의 제목을 입력하세요: ", input_bookName),
            ("추가할 책의 저자를 입력하세요: ", input_author),
            ("추가할 책의 출판사를 입력하세요: ", input_publisher),
            ("추가할 책의 출판년도를 입력하세요: ", input_year),
            ]
            
        for message, func in messages_and_functions:
            info = func(message)
            if not info:
                return False
            
            book_info.append(info)
    else:
        book_info = str(books[0]).split(" / ")
        book_info = book_info[2:6]

    print(BookRecord.get_header())
    print()
    if isbn:
        for book in books:
            print(book)
        print()
        print("여기에")
        print()

    book_record = BookRecord(
        bookData.get_static_id(), isbn, book_info[0], book_info[1], book_info[2], book_info[3], today
    )

    print(book_record)
    print()
    if input_response("해당 책을 추가하시겠습니까?(Y/N): "):
        bookData.insert_record(book_record)
        return True
    else:
        print("추가를 중단하며 메인 프롬프트로 돌아갑니다.")
        return False


def main_prompt(bookData) -> None:
    slc = 0

    main_prompt_text = """1. 추가
2. 삭제
3. 수정
4. 검색
5. 대출
6. 반납
7. 종료\n"""

    while slc != 7:
        print(main_prompt_text + "-"*20 + "\nLibsystem_Main > ", end="")

        try:
            slc = int(input())
            assert 0 < slc <= 7, "원하는 동작에 해당하는 번호(숫자)만 입력해주세요."
        except ValueError as e:
            print("원하는 동작에 해당하는 번호(숫자)만 입력해주세요.")
            continue
        except AssertionError as e:
            print(e)
            continue
        except Exception as e:
            print("예상하지 못한 오류 발생.", e)
            break

        if slc == 1:
            # bookData.insert_record()
            add_book()

        if slc == 2:
            pass

        if slc == 3:
            bookData.update_record()

        if slc == 4:
            bookData.delete_record()

        if slc == 5:
            bookData.borrow_book()

        if slc == 6:
            bookData.return_book()

    print("프로그램을 종료합니다.")


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

    main_prompt(bookData=bookData)
