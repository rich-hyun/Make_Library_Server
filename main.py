import os
import datetime
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
    
    # 덧셈 연산자 구현 (날짜 더하기)
    def __add__(self, days):
        if not isinstance(days, int):
            raise TypeError("날짜에 더할 일수는 정수여야 합니다.")
        
        day = self.day
        month = self.month
        year = self.year
        
        while days > 0:
            days_in_current_month = 29 if (month == 2 and self.is_leap_year(year)) else [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1]
            
            if day + days <= days_in_current_month:
                day += days
                days = 0
            else:
                days -= (days_in_current_month - day + 1)
                day = 1
                month += 1
                if month > 12:
                    month = 1
                    year += 1
        
        return MyDate(year, month, day)


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

    # 데이터 삽입 인터페이스
    def insert_record(self) -> tuple[bool, str]:
        return (True, None)

    # 데이터 수정 (업데이트)
    def update_record(self) -> tuple[bool, str]:
        return (True, None)

    # 데이터 삭제
    def delete_record(self) -> tuple[bool, str]:
        return (True, None)
    
    
    
    # 책 대출
    def borrow_book(self) -> tuple[bool, str]:
        return (True, None)
    
    # 책 반납
    def return_book(self) -> tuple[bool, str]:
        return (True, None)
    
    # 책 검색
    def search_book(self):

        if not self.book_data:
            print("등록된 책이 존재하지 않습니다.")
            return False

        search_book = input("검색할 책의 제목이나 저자를 입력하세요: ")
        
        if "/" in search_book or "\\" in search_book:
            print('ERROR: 책의 제목 또는 저자에는 특수문자 "/" 또는 "\\"을 입력할 수 없습니다.')
        
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
        

        print(BookRecord.get_header())
        print("\n")
        for book in search_results:
            print(book.to_str(today=self.today, contain_borrow=True))
        print("\n")
        return True

    # 데이터 무결성 검사
    def check_data_integrity(self) -> tuple[bool, str]:
        return (True, None)

    # 데이터 저장
    def save_data_to_file(self) -> tuple[bool, str]:
        return (True, None)
    
    # 디버깅용 책 데이터 출력
    def print_book_debug(self) -> None:
        print("="*10, "BOOK DATA", "="*10)
        print(BookRecord.get_header())
        for book in self.book_data:
            print(book.to_str(today=self.today, contain_borrow=True))
        print("="*30)

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
            bookData.insert_record()
            
        if slc == 2:
            bookData.update_record()
            
        if slc == 3:
            # 검색 및 조회
            pass
        
        if slc == 4:
            bookData.search_book()
            
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
