import os
from datetime import datetime
import re
import json

opj = os.path.join


""" ========== 날짜 클래스 구현 ========== """
class MyDate(object):
    def __init__(self, year, month, day):
        assert type(year) is int
        assert type(month) is int
        assert type(day) is int

        assert 1582 < year, "년도는 1582보다 큰 정수여야 합니다."
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
            
            assert 1582 < year, "년도는 1582보다 큰 정수여야 합니다."
            assert 1 <= month <= 12, "월은 1과 12사이의 정수여야 합니다."
            assert self.validate_day(year, month, day), "���도와 월에 대해 일이 올바른 범위를 벗어났습니다."
            
            return MyDate(year, month, day)
            
        except Exception as e:
            # print(e)
            # print("텍스트 " + text +"을(를) 날짜로 변환할 수 없습니다.")

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
    
    def to_ordinal(self):
        # 1583년 1월 1일을 기준으로 일수 계산
        days = 0
        for y in range(1583, self.year):
            days += 366 if self.is_leap_year(y) else 365

        days_in_month = [31, 29 if self.is_leap_year(self.year) else 28, 31, 30, 31, 30, 
                         31, 31, 30, 31, 30, 31]
        days += sum(days_in_month[:self.month - 1])
        days += self.day - 1  # 1월 1일을 0으로 시작하기 위해 -1
        
        return days

    @classmethod
    def from_ordinal(cls, days):
        # 1583년 1월 1일을 기준으로 날짜 생성
        year = 1583
        while True:
            days_in_year = 366 if cls.is_leap_year(year) else 365
            if days < days_in_year:
                break
            days -= days_in_year
            year += 1

        days_in_month = [31, 29 if cls.is_leap_year(year) else 28, 31, 30, 31, 30, 
                         31, 31, 30, 31, 30, 31]

        month = 1
        for dim in days_in_month:
            if days < dim:
                break
            days -= dim
            month += 1

        day = days + 1  # 1월 1일부터 시작하기 위해 +1

        return cls(year, month, day)

    def __add__(self, days):
        if not isinstance(days, int):
            raise TypeError("날짜에 더할 일수는 정수여야 합니다.")
        total_days = self.to_ordinal() + days
        return MyDate.from_ordinal(total_days)

    def __sub__(self, other):
        if isinstance(other, int):
            total_days = self.to_ordinal() - other
            return MyDate.from_ordinal(total_days)
        elif isinstance(other, MyDate):
            return self.to_ordinal() - other.to_ordinal()
        else:
            raise TypeError("빼기 연산은 정수 또는 MyDate 객체여야 합니다.")

""" ========== 데이터 테이블 구현 ========== """
# Book
class BookRecord(object):
    def __init__(self, book_id: int, isbn: int, register_date: MyDate, delete_date: MyDate, deleted: bool=False):
        self.book_id = book_id
        self.isbn = isbn
        self.register_date = register_date
        self.deleted = deleted
        self.delete_date = delete_date

# ISBN
class ISBNRecord(object):
    def __init__(self, isbn: int, title: str, publisher_id: int, published_year: int, isbn_register_date: MyDate):
        self.isbn = isbn
        self.title = title
        self.publisher_id = publisher_id
        self.published_year = published_year
        self.isbn_register_date = isbn_register_date
        
# Author
class AuthorRecord(object):
    def __init__(self, author_id: int, name: str, deleted: bool=False):
        self.author_id = author_id
        self.name = name
        self.deleted = deleted

    def __str__(self):
        return f"{self.name} #{self.author_id}"

# Isbn - Author
class IsbnAuthorRecord(object):
    def __init__(self, isbn: int, author_id: int):
        self.isbn = isbn
        self.author_id = author_id
        
# Book Edit Log
class BookEditLogRecord(object):
    def __init__(self, log_id: int, isbn: int, edit_date: MyDate):
        self.log_id = log_id
        self.isbn = isbn
        self.edit_date = edit_date
        
# Borrow
class BorrowRecord(object):
    def __init__(self, borrow_id: int, book_id: int, user_id: int, borrow_date: MyDate, return_date: MyDate, actual_return_date: MyDate=None, deleted: bool=False):
        self.borrow_id = borrow_id
        self.book_id = book_id
        self.user_id = user_id
        self.borrow_date = borrow_date
        self.return_date = return_date
        self.actual_return_date = actual_return_date
        self.deleted = deleted

# User
class UserRecord(object):
    def __init__(self, user_id: int, phone_number: str, name: str, deleted: bool=False):
        self.user_id = user_id
        self.phone_number = phone_number
        self.name = name
        self.deleted = deleted
        
# Publisher
class PublisherRecord(object):
    def __init__(self, publisher_id: int, name: str, deleted: bool=False):
        self.publisher_id = publisher_id
        self.name = name
        self.deleted = deleted
    
# Overdue Penalty
class OverduePenaltyRecord(object):
    def __init__(self, penalty_id: int, user_id: int, penalty_start_date: MyDate, penalty_end_date: MyDate):
        self.penalty_id = penalty_id
        self.user_id = user_id
        self.penalty_start_date = penalty_start_date
        self.penalty_end_date = penalty_end_date

""" ========== 도서 관리 클래스 구현 ========== """
class DataManager(object):
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.book_table = []
        self.isbn_table = []
        self.author_table = []
        self.isbn_author_table = []
        self.book_edit_log_table = []
        self.borrow_table = []
        self.user_table = []
        self.publisher_table = []
        self.overdue_penalty_table = []
        self.today = None
        self.config = dict()
        self.static_id = 0  # default is 0

        # auto increment id
        self.static_author_id = 0
        self.static_book_edit_log_id = 0
        self.static_borrow_id = 0
        self.static_user_id = 0
        self.static_publisher_id = 0
        self.static_overdue_penalty_id = 0

        # Load configuration and ensure "cancel" key exists
        self.load_configuration()

        # 디버깅 및 기본값 보장
        if "cancel" not in self.config:
            print("ERROR: 'cancel' 키가 설정에 없습니다. 기본값 'X'를 추가합니다.")
            self.config["cancel"] = "X"


    
    # 오늘 날짜 설정
    def set_today(self, today: MyDate):
        self.today = today
        
    # 데이터 파일 읽기
    def read_data_files(self, sep: str="/", verbose=True):

        if verbose: print("="*10, "Start Reading Data Files", "="*10)
        
        # 1. Book Data
         # 파일이 존재하지 않으면 생성
        if not os.path.exists(opj(self.file_path, "data", "Libsystem_Data_Book.txt")):
            with open(opj(self.file_path, "data", "Libsystem_Data_Book.txt"), "w", encoding='utf-8') as f:
                f.write("0\n")
            
        
        # 파일이 비어있으면 생성
        if os.stat(self.file_path).st_size == 0:
            with open(opj(self.file_path, "data", "Libsystem_Data_Book.txt"), "w", encoding='utf-8') as f:
                f.write("0\n")
            
        
        # 무결성 검사(데이터가 올바르지 않을경우 파일명 변경(Libsystem_Data_{테이블명}-yyyyMMdd_hhmmss.bak) 후 새 Libsystem_Data_Book.txt 파일 생성)
        # yyyyMMdd-hhmmss는 컴퓨터 운영체제 시스템 시간을 기준으로 함
        if not self.check_data_book_files(self.file_path):
            now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            os.rename(opj(self.file_path, "data", "Libsystem_Data_Book.txt"), opj(self.file_path, "data", f"Libsystem_Data_Book-{now}.bak"))
            with open(opj(self.file_path, "data", "Libsystem_Data_Book.txt"), "w", encoding='utf-8') as f:
                f.write("0\n")

        with open(opj(self.file_path, "data", "Libsystem_Data_Book.txt"), "r",encoding='utf-8') as f:
            lines = f.readlines()
            
            self.static_id = int(lines[0])
            
            for line in lines[1:]:
                book_id, isbn, register_date, deleted, delete_date = line.strip().split(sep)
                self.book_table.append(BookRecord(int(book_id), int(isbn), MyDate.from_str(register_date), MyDate.from_str(delete_date), bool(int(deleted))))
          
        if verbose:      
            print(f"{len(self.book_table)} Book Data Loaded")
            print(f"max_book_id: {self.static_id}")
                
        # 2. ISBN Data
        # 파일이 존재하지 않으면 생성(아무 데이터 없음)
        if not os.path.exists(opj(self.file_path, "data", "Libsystem_Data_Isbn.txt")):
            with open(opj(self.file_path, "data", "Libsystem_Data_Isbn.txt"), "w", encoding='utf-8') as f:
                pass
        
        # 무결성 검사(데이터가 올바르지 않을경우 파일명 변경(Libsystem_Data_{테이블명}-yyyyMMdd_hhmmss.bak) 후 새 Libsystem_Data_Isbn.txt 파일 생성)
        # yyyyMMdd-hhmmss는 컴퓨터 운영체제 시스템 시간을 기준으로 함
        if not self.check_data_isbn_files(self.file_path):
            now = datetime.now().strftime("%Y%m%d_%H%M%S")
            os.rename(opj(self.file_path, "data", "Libsystem_Data_Isbn.txt"), opj(self.file_path, "data", f"Libsystem_Data_Isbn-{now}.bak"))
            with open(opj(self.file_path, "data", "Libsystem_Data_Isbn.txt"), "w", encoding='utf-8') as f:
                pass

        with open(opj(self.file_path, "data", "Libsystem_Data_Isbn.txt"), "r",encoding='utf-8') as f:
            for line in f:
                isbn, title, publisher_id, published_year, isbn_register_date = line.strip().split(sep)
                self.isbn_table.append(ISBNRecord(int(isbn), title, int(publisher_id), int(published_year), MyDate.from_str(isbn_register_date)))
                
        if verbose: print(f"{len(self.isbn_table)} ISBN Data Loaded")
                
        # 3. Author Data

        # 파일이 존재하지 않으면 생성(아무 데이터 없음)
        if not os.path.exists(opj(self.file_path, "data", "Libsystem_Data_Author.txt")):
            with open(opj(self.file_path, "data", "Libsystem_Data_Author.txt"), "w", encoding='utf-8') as f:
                 pass
            
        
        # 무결성 검사(데이터가 올바르지 않을경우 파일명 변경(Libsystem_Data_{테이블명}-yyyyMMdd_hhmmss.bak) 후 새 Libsystem_Data_Author.txt 파일 생성)
        # yyyyMMdd-hhmmss는 컴퓨터 운영체제 시스템 시간을 기준으로 함
        if not self.check_data_author_files(self.file_path):
            now = datetime.now().strftime("%Y%m%d_%H%M%S")
            os.rename(opj(self.file_path, "data", "Libsystem_Data_Author.txt"), opj(self.file_path, "data", f"Libsystem_Data_Author-{now}.bak"))
            with open(opj(self.file_path, "data", "Libsystem_Data_Author.txt"), "w", encoding='utf-8') as f:
                 pass
            
        with open(opj(self.file_path, "data", "Libsystem_Data_Author.txt"), "r",encoding='utf-8') as f:
            for line in f:
                author_id, name, deleted = line.strip().split(sep)
                self.author_table.append(AuthorRecord(int(author_id), name, bool(int(deleted))))
                
        if verbose: print(f"{len(self.author_table)} Author Data Loaded")
                
        # 4. ISBN - Author Data
        # 파일이 존재하지 않으면 생성
        if not os.path.exists(opj(self.file_path, "data", "Libsystem_Data_IsbnAuthor.txt")):
            with open(opj(self.file_path, "data", "Libsystem_Data_IsbnAuthor.txt"), "w", encoding='utf-8') as f:
                 pass
            
        
        # 무결성 검사(데이터가 올바르지 않을경우 파일명 변경(Libsystem_Data_{테이블명}-yyyyMMdd_hhmmss.bak) 후 새 Libsystem_Data_IsbnAuthor.txt 파일 생성)
        # yyyyMMdd-hhmmss는 컴퓨터 운영체제 시스템 시간을 기준으로 함
        if not self.check_data_isbn_author_files(self.file_path):
            now = datetime.now().strftime("%Y%m%d_%H%M%S")
            os.rename(opj(self.file_path, "data", "Libsystem_Data_IsbnAuthor.txt"), opj(self.file_path, "data", f"Libsystem_Data_IsbnAuthor-{now}.bak"))
            with open(opj(self.file_path, "data", "Libsystem_Data_IsbnAuthor.txt"), "w",encoding='utf-8') as f:
                 pass

        with open(opj(self.file_path, "data", "Libsystem_Data_IsbnAuthor.txt"), "r",encoding='utf-8') as f:
            for line in f:
                isbn, author_id = line.strip().split(sep)
                self.isbn_author_table.append(IsbnAuthorRecord(int(isbn), int(author_id)))
                
        if verbose: print(f"{len(self.isbn_author_table)} ISBN - Author Data Loaded")
                
        # 5. Book Edit Log Data
        # 파일이 존재하지 않으면 생성
        if not os.path.exists(opj(self.file_path, "data", "Libsystem_Data_BookEditLog.txt")):
            with open(opj(self.file_path, "data", "Libsystem_Data_BookEditLog.txt"), "w", encoding='utf-8') as f:
                pass
            
        
        # 무결성 검사(데이터가 올바르지 않을경우 파일명 변경(Libsystem_Data_{테이블명}-yyyyMMdd_hhmmss.bak) 후 새 Libsystem_Data_BookEditLog.txt 파일 생성)
        # yyyyMMdd-hhmmss는 컴퓨터 운영체제 시스템 시간을 기준으로 함
        if not self.check_data_book_edit_log_files(self.file_path):
            now = datetime.now().strftime("%Y%m%d_%H%M%S")
            os.rename(opj(self.file_path, "data", "Libsystem_Data_BookEditLog.txt"), opj(self.file_path, "data", f"Libsystem_Data_BookEditLog-{now}.bak"))
            with open(opj(self.file_path, "data", "Libsystem_Data_BookEditLog.txt"), "w", encoding='utf-8') as f:
                pass

        with open(opj(self.file_path, "data", "Libsystem_Data_BookEditLog.txt"), "r",encoding='utf-8') as f:
            for line in f:
                log_id, isbn, edit_date = line.strip().split(sep)
                self.book_edit_log_table.append(BookEditLogRecord(int(log_id), int(isbn), MyDate.from_str(edit_date)))
                
        if verbose: print(f"{len(self.book_edit_log_table)} Book Edit Log Data Loaded")
                
        # 6. Borrow Data
        # 파일이 존재하지 않으면 생성
        if not os.path.exists(opj(self.file_path, "data", "Libsystem_Data_Borrow.txt")):
            with open(opj(self.file_path, "data", "Libsystem_Data_Borrow.txt"), "w", encoding='utf-8') as f:
                pass
            
        
        # 무결성 검사(데이터가 올바르지 않을경우 파일명 변경(Libsystem_Data_{테이블명}-yyyyMMdd_hhmmss.bak) 후 새 Libsystem_Data_Borrow.txt 파일 생성)
        # yyyyMMdd-hhmmss는 컴퓨터 운영체제 시스템 시간을 기준으로 함
        if not self.check_data_borrow_files(self.file_path):
            now = datetime.now().strftime("%Y%m%d_%H%M%S")
            os.rename(opj(self.file_path, "data", "Libsystem_Data_Borrow.txt"), opj(self.file_path, "data", f"Libsystem_Data_Borrow-{now}.bak"))
            with open(opj(self.file_path, "data", "Libsystem_Data_Borrow.txt"), "w", encoding='utf-8') as f:
                pass

        with open(opj(self.file_path, "data", "Libsystem_Data_Borrow.txt"), "r",encoding='utf-8') as f:
            for line in f:
                borrow_id, book_id, user_id, borrow_date, return_date, actual_return_date, deleted = line.strip().split(sep)
                self.borrow_table.append(BorrowRecord(int(borrow_id), int(book_id), int(user_id), MyDate.from_str(borrow_date), MyDate.from_str(return_date), MyDate.from_str(actual_return_date), bool(int(deleted))))
                
        if verbose: print(f"{len(self.borrow_table)} Borrow Data Loaded")            
    
        # 7. User Data
        # 파일이 존재하지 않으면 생성
        if not os.path.exists(opj(self.file_path, "data", "Libsystem_Data_User.txt")):
            with open(opj(self.file_path, "data", "Libsystem_Data_User.txt"), "w", encoding='utf-8') as f:
                pass
            
        
        # 무결성 검사(데이터가 올바르지 않을경우 파일명 변경(Libsystem_Data_{테이블명}-yyyyMMdd_hhmmss.bak) 후 새 Libsystem_Data_User.txt 파일 생성)
        # yyyyMMdd-hhmmss는 컴퓨터 운영체제 시스템 시간을 기준으로 함
        if not self.check_data_user_files(self.file_path):
            now = datetime.now().strftime("%Y%m%d_%H%M%S")
            os.rename(opj(self.file_path, "data", "Libsystem_Data_User.txt"), opj(self.file_path, "data", f"Libsystem_Data_User-{now}.bak"))
            with open(opj(self.file_path, "data", "Libsystem_Data_User.txt"), "w", encoding='utf-8') as f:
                pass

        with open(opj(self.file_path, "data", "Libsystem_Data_User.txt"), "r",encoding='utf-8') as f:
            for line in f:
                user_id, phone_number, name, deleted = line.strip().split(sep)
                self.user_table.append(UserRecord(int(user_id), phone_number, name, bool(int(deleted))))
        
        if verbose: print(f"{len(self.user_table)} User Data Loaded")
        
        # 8. Publisher Data
         # 파일이 존재하지 않으면 생성
        if not os.path.exists(opj(self.file_path, "data", "Libsystem_Data_Publisher.txt")):
            with open(opj(self.file_path, "data", "Libsystem_Data_Publisher.txt"), "w", encoding='utf-8') as f:
                pass
           
        
        # 무결성 검사(데이터가 올바르지 않을경우 파일명 변경(Libsystem_Data_{테이블명}-yyyyMMdd_hhmmss.bak) 후 새 Libsystem_Data_Publisher.txt 파일 생성)
        # yyyyMMdd-hhmmss는 컴퓨터 운영체제 시스템 시간을 기준으로 함
        if not self.check_data_publisher_files(self.file_path):
            now = datetime.now().strftime("%Y%m%d_%H%M%S")
            os.rename(opj(self.file_path, "data", "Libsystem_Data_Publisher.txt"), opj(self.file_path, "data", f"Libsystem_Data_Publisher-{now}.bak"))
            with open(opj(self.file_path, "data", "Libsystem_Data_Publisher.txt"), "w", encoding='utf-8') as f:
                pass

        with open(opj(self.file_path, "data", "Libsystem_Data_Publisher.txt"), "r",encoding='utf-8') as f:
            for line in f:
                publisher_id, name, deleted = line.strip().split(sep)
                self.publisher_table.append(PublisherRecord(int(publisher_id), name, bool(int((deleted)))))

        if verbose: print(f"{len(self.publisher_table)} Publisher Data Loaded")

        # 9. Overdue Penalty Data
        # 파일이 존재하지 않으면 생성
        if not os.path.exists(opj(self.file_path, "data", "Libsystem_Data_OverduePenalty.txt")):
            with open(opj(self.file_path, "data", "Libsystem_Data_OverduePenalty.txt"), "w", encoding='utf-8') as f:
                pass
            
        
        # 무결성 검사(데이터가 올바르지 않을경우 파일명 변경(Libsystem_Data_{테이블명}-yyyyMMdd_hhmmss.bak) 후 새 Libsystem_Data_OverduePenalty.txt 파일 생성)
        # yyyyMMdd-hhmmss는 컴퓨터 운영체제 시스템 시간을 기준으로 함
        if not self.check_data_overdue_penalty_files(self.file_path):
            now = datetime.now().strftime("%Y%m%d_%H%M%S")
            os.rename(opj(self.file_path, "data", "Libsystem_Data_OverduePenalty.txt"), opj(self.file_path, "data", f"Libsystem_Data_OverduePenalty-{now}.bak"))
            with open(opj(self.file_path, "data", "Libsystem_Data_OverduePenalty.txt"), "w", encoding='utf-8') as f:
                pass

        with open(opj(self.file_path, "data", "Libsystem_Data_OverduePenalty.txt"), "r",encoding='utf-8') as f:
            for line in f:
                penalty_id, user_id, penalty_start_date, penalty_end_date = line.strip().split(sep)
                self.overdue_penalty_table.append(OverduePenaltyRecord(int(penalty_id), int(user_id), MyDate.from_str(penalty_start_date), MyDate.from_str(penalty_end_date)))

        if verbose: 
            print(f"{len(self.overdue_penalty_table)} Overdue Penalty Data Loaded")
            print("="*10, "End Reading Data Files", "="*10)
        
    
    # ========== 데이터 파일 저장 (임시) ========== #
    def write_data_files(self):
        # 1. Book Data
        with open(opj(self.file_path, "data", "Libsystem_Data_Book.txt"), "w",encoding='utf-8') as f:
            for book in self.book_table:
                f.write(f"{book.book_id}/{book.isbn}/{str(book.register_date)}/{int(book.deleted)}/{str(book.delete_date)}\n")
                
        # 2. ISBN Data
        with open(opj(self.file_path, "data", "Libsystem_Data_Isbn.txt"), "w",encoding='utf-8') as f:
            for isbn in self.isbn_table:
                f.write(f"{isbn.isbn}/{isbn.title}/{isbn.publisher_id}/{isbn.published_year}/{str(isbn.isbn_register_date)}\n")
                
        # 3. Author Data
        with open(opj(self.file_path, "data", "Libsystem_Data_Author.txt"), "w",encoding='utf-8') as f:
            for author in self.author_table:
                f.write(f"{author.author_id}/{author.name}/{int(author.deleted)}\n")
                
        # 4. ISBN - Author Data
        with open(opj(self.file_path, "data", "Libsystem_Data_IsbnAuthor.txt"), "w",encoding='utf-8') as f:
            for isbn_author in self.isbn_author_table:
                f.write(f"{isbn_author.isbn}/{isbn_author.author_id}\n")
                
        # 5. Book Edit Log Data
        with open(opj(self.file_path, "data", "Libsystem_Data_BookEditLog.txt"), "w",encoding='utf-8') as f:
            for log in self.book_edit_log_table:
                f.write(f"{log.log_id}/{log.isbn}/{str(log.edit_date)}\n")
                
        # 6. Borrow Data
        with open(opj(self.file_path, "data", "Libsystem_Data_Borrow.txt"), "w",encoding='utf-8') as f:
            for borrow in self.borrow_table:
                f.write(f"{borrow.borrow_id}/{borrow.book_id}/{borrow.user_id}/{str(borrow.borrow_date)}/{str(borrow.return_date)}/{str(borrow.actual_return_date)}/{int(borrow.deleted)}\n")
                
        # 7. User Data
        with open(opj(self.file_path, "data", "Libsystem_Data_User.txt"), "w",encoding='utf-8') as f:
            for user in self.user_table:
                f.write(f"{user.user_id}/{user.phone_number}/{user.name}/{int(user.deleted)}\n")
                
        # 8. Publisher Data
        with open(opj(self.file_path, "data", "Libsystem_Data_Publisher.txt"), "w",encoding='utf-8') as f:
            for publisher in self.publisher_table:
                f.write(f"{publisher.publisher_id}/{publisher.name}/{int(publisher.deleted)}\n")
                
        # 9. Overdue Penalty Data
        with open(opj(self.file_path, "data", "Libsystem_Data_OverduePenalty.txt"), "w",encoding='utf-8') as f:
            for penalty in self.overdue_penalty_table:
                f.write(f"{penalty.penalty_id}/{penalty.user_id}/{str(penalty.penalty_start_date)}/{str(penalty.penalty_end_date)}\n")
    
    # ========== 데이터 파일 메모리 -> 파일 동기화 (fetch) ========== #
    def fetch_data_file(self):
        pass
    
    # ========== 데이터 파일 무결성 검사 ========== #
    # 오류 발생 시 오류 발생한 줄과 오류 메세지 출력
    def check_data_book_files(self,file_path: str):
        # 오류 발생한 줄과 오류 메세지 파일의 마지막 줄에 추가
        line_num = 1
        def add_error(line_num, error_message):
            with open(opj(file_path, "data", "Libsystem_Data_Book.txt"), "a", encoding='utf-8') as f:
                f.write(f"데이터 파일 무결성 검사에 실패했습니다. 오류 발생 위치 : {line_num}번째 줄 - {error_message}\n")

        with open(opj(file_path, "data", "Libsystem_Data_Book.txt"), "r", encoding='utf-8') as f:
            lines = f.readlines()
        first_line = lines[0].strip()
        
        # 첫 줄이 숫자인지 확인
        if not first_line.isdigit():
            add_error(line_num, "첫 줄이 숫자가 아닙니다.")
            return False
        
        # 범위 검사
        first_line = int(first_line)
        if  first_line < 0 or first_line > 99:
            add_error(line_num, "첫 줄이 0에서 99 사이의 정수가 아닙니다.")
            return False
        
        # 구분자가 4개인지 확인
        for line in lines[1:]:
            line_num += 1
            line = line.strip()
            if line_num == 2 and line == "":
                return True
            if len(line.strip().split("/")) != 5:
                add_error(line_num, "구분자가 4개가 아닙니다")
                return False
            
        line_num = 1
            
        # 모든 레코드의 앞 4개 항목 비어있지 않는 지 확인
        for line in lines[1:]:
            line_num += 1
            book_id, isbn, register_date, deleted, delete_date = line.strip().split("/")
            if book_id == "" or isbn == "" or register_date == "" or deleted == "":
                add_error(line_num, "모든 레코드의 앞 4개 항목이 비어있습니다.")
                return False
        
        line_num = 1
            
        # 고유번호 검사
        for line in lines[1:]:
            line_num += 1
            book_id, isbn, register_date, deleted, delete_date = line.strip().split("/")
            # 고유번호가 숫자인지 확인
            if not book_id.isdigit():
                add_error(line_num, "고유번호가 숫자가 아닙니다.")
                return False
            
            # 고유번호가 0에서 첫 줄의 값 사이의 정수인지 확인
            if int(book_id) < 0 or int(book_id) > first_line:
                add_error(line_num, "고유번호가 0에서 첫 줄의 값 사이의 정수가 아닙니다.")
                return False
            
            # 고유번호 중복 검사
            if lines[1:].count(book_id) > 1:
                add_error(line_num, "고유번호가 중복됩니다.")
                return False
            
            # ISBN 검사(길이가 2이며, 정수로 변환 가능한지)
            if len(isbn) != 2 or not isbn.isdigit():
                add_error(line_num, "ISBN이 2자리 숫자가 아닙니다.")
                return False
            
            # 등록 날짜 검사
            if not MyDate.from_str(register_date):
                add_error(line_num, "등록 날짜가 날짜 형식이 아닙니다.")
                return False
            
            # 삭제 여부 검사
            if deleted not in ["0", "1"]:
                add_error(line_num, "삭제 여부가 0 또는 1이 아닙니다.")
                return False
            
            # 삭제 날짜 검사(날짜 검사 및 삭제 여부가 1일 때만 검사)
            if deleted == "1" and not MyDate.from_str(delete_date):
                add_error(line_num, "삭제 날짜가 날짜 형식이 아닙니다.")
                return False
            
        return True
    
    def check_data_isbn_files(self,file_path: str):
        # 오류 발생한 줄과 오류 메세지 파일의 마지막 줄에 추가
        def add_error(line_num, error_message):
            with open(opj(file_path, "data", "Libsystem_Data_Isbn.txt"), "a", encoding='utf-8') as f:
                f.write(f"데이터 파일 무결성 검사에 실패했습니다. 오류 발생 위치 : {line_num}번째 줄 - {error_message}\n")

        with open(opj(file_path, "data", "Libsystem_Data_Isbn.txt"), "r", encoding='utf-8') as f:
            lines = f.readlines()
            
        line_num = 0
        
        # 구분자가 4개인지 확인
        for line in lines:
            line_num += 1
            line = line.strip()
            if line_num ==1 and line == "":
                return True
            
            if len(line.strip().split("/")) != 5:
                add_error(line_num, "구분자가 4개가 아닙니다")
                return False
            
        line_num = 0
            
        # 모든 레코드의 앞 5개 항목 비어있지 않는 지 확인
        for line in lines:
            line_num += 1
            isbn, title, publisher_id, published_year, isbn_register_date = line.strip().split("/")
            if isbn == "" or title == "" or publisher_id == "" or published_year == "" or isbn_register_date == "":
                add_error(line_num, "모든 레코드의 앞 5개 항목이 비어있습니다.")
                return False
        
        line_num = 0
            
        # ISBN 검사
        for line in lines:
            line_num += 1
            isbn, title, publisher_id, published_year, isbn_register_date = line.strip().split("/")
            # ISBN이 숫자인지 확인
            if not isbn.isdigit():
                add_error(line_num, "ISBN이 숫자가 아닙니다.")
                return False
            
            # ISBN이 0에서 99 사이의 정수인지 확인
            if int(isbn) < 0 or int(isbn) > 99:
                add_error(line_num, "ISBN이 0에서 99 사이의 정수가 아닙니다.")
                return False
            
            # ISBN 중복 검사
            if lines.count(isbn) > 1:
                add_error(line_num, "ISBN이 중복됩니다.")
                return False
            
            # 출판사 ID 검사
            if not publisher_id.isdigit():
                add_error(line_num, "출판사 ID가 숫자가 아닙니다.")
                return False
            
            # 출판사 ID 범위
            if int(publisher_id) < 0:
                add_error(line_num, "출판사 ID가 0 이상이 아닙니다.")
                return False
            
            # 책 제목에 '/'나 '\'가 포함되어 있는지 확인
            if "/" in title or "\\" in title:
                add_error(line_num, "책 제목에 '/'나 '\\'가 포함되어 있습니다.")
                return False
            
            # 출판년도 검사
            if not published_year.isdigit():
                add_error(line_num, "출판년도가 숫자가 아닙니다.")
                return False
            
            # 출판년도가 1583에서 9999 사이의 정수인지 확인
            if int(published_year) < 1583 or int(published_year) > 9999:
                add_error(line_num, "출판년도가 1583에서 9999 사이의 정수가 아닙니다.")
                return False
            
            # ISBN 등록 날짜 검사
            if not MyDate.from_str(isbn_register_date):
                add_error(line_num, "ISBN 등록 날짜가 날짜 형식이 아닙니다.")
                return False
            
        return True

    def check_data_author_files(self,file_path: str):
        # 오류 발생한 줄과 오류 메세지 파일의 마지막 줄에 추가
        def add_error(line_num, error_message):
            with open(opj(file_path, "data", "Libsystem_Data_Author.txt"), "a",encoding='utf-8') as f:
                f.write(f"데이터 파일 무결성 검사에 실패했습니다. 오류 발생 위치 : {line_num}번째 줄 - {error_message}\n")

        with open(opj(file_path, "data", "Libsystem_Data_Author.txt"), "r", encoding='utf-8') as f:
            lines = f.readlines()
            
        line_num = 0
        
        # 구분자가 2개인지 확인
        for line in lines:
            line_num += 1
            line = line.strip()
            if line_num ==1 and line == "":
                return True
            if len(line.strip().split("/")) != 3:
                add_error(line_num, "구분자가 2개가 아닙니다")
                return False
            
        line_num = 0

        # 모든 레코드의 앞 3개 항목 비어있지 않는 지 확인
        for line in lines:
            line_num += 1
            author_id, name, deleted = line.strip().split("/")
            if author_id == "" or name == "" or deleted == "":
                add_error(line_num, "필수항목 중 비어있는 항목이 있습니다.")
                return False
            
        line_num = 0

        # 저자 ID 검사
        for line in lines:
            line_num += 1
            author_id, name, deleted = line.strip().split("/")
            # 저자 ID가 숫자인지 확인
            if not author_id.isdigit():
                add_error(line_num, "저자 ID가 숫자가 아닙니다.")
                return False
            
            # 저자 ID 범위
            if int(author_id) < 1:
                add_error(line_num, "저자 ID가 1 이상이 아닙니다.")
                return False
            
            # 저자 ID 중복 검사
            if lines.count(author_id) > 1:
                add_error(line_num, "저자 ID가 중복됩니다.")
                return False
            
            # 저자 이름에 '/'나 '\'가 포함되어 있는지 확인
            if "/" in name or "\\" in name:
                add_error(line_num, "저자 이름에 '/'나 '\\'가 포함되어 있습니다.")
            
            # 삭제 여부 검사
            if deleted not in ["0", "1"]:
                add_error(line_num, "삭제 여부가 0 또는 1이 아닙니다.")
                return False
            
        return True


    def check_data_isbn_author_files(self,file_path: str):
        # 오류 발생한 줄과 오류 메세지 파일의 마지막 줄에 추가
        def add_error(line_num, error_message):
            with open(opj(file_path, "data", "Libsystem_Data_IsbnAuthor.txt"), "a", encoding='utf-8') as f:
                f.write(f"데이터 파일 무결성 검사에 실패했습니다. 오류 발생 위치 : {line_num}번째 줄 - {error_message}\n")

        with open(opj(file_path, "data", "Libsystem_Data_IsbnAuthor.txt"), "r", encoding='utf-8') as f:
            lines = f.readlines()
            
        line_num = 0
        
        # 구분자가 1개인지 확인
        for line in lines:
            line_num += 1
            line = line.strip()
            if line_num ==1 and line == "":
                return True
            
            if len(line.strip().split("/")) != 2:
                add_error(line_num, "구분자가 1개가 아닙니다")
                return False

            
        line_num = 0

        # 모든 레코드의 앞 2개 항목 비어있지 않는 지 확인
        for line in lines:
            line_num += 1
            isbn, author_id = line.strip().split("/")
            if isbn == "" or author_id == "":
                add_error(line_num, "필수항목 중 비어있는 항목이 있습니다.")
                return False
            
        line_num = 0

        # ISBN 검사
        for line in lines:
            line_num += 1
            isbn, author_id = line.strip().split("/")
            # ISBN이 숫자인지 확인
            if not isbn.isdigit():
                add_error(line_num, "ISBN이 숫자가 아닙니다.")
                return False
            
            # ISBN이 0에서 99 사이의 정수인지 확인
            if int(isbn) < 0 or int(isbn) > 99:
                add_error(line_num, "ISBN이 0에서 99 사이의 정수가 아닙니다.")
                return False
            
            # ISBN 중복 검사
            if lines.count(isbn) > 1:
                add_error(line_num, "ISBN이 중복됩니다.")
                return False
            
            # 저자 ID 검사
            if not author_id.isdigit():
                add_error(line_num, "저자 ID가 숫자가 아닙니다.")
                return False
            
            # 저자 ID 범위
            if int(author_id) < 1:
                add_error(line_num, "저자 ID가 1 이상이 아닙니다.")
                return False
            
        return True

    def check_data_book_edit_log_files(self,file_path: str):
        # 오류 발생한 줄과 오류 메세지 파일의 마지막 줄에 추가
        def add_error(line_num, error_message):
            with open(opj(file_path, "data", "Libsystem_Data_BookEditLog.txt"), "a", encoding='utf-8') as f:
                f.write(f"데이터 파일 무결성 검사에 실패했습니다. 오류 발생 위치 : {line_num}번째 줄 - {error_message}\n")

        with open(opj(file_path, "data", "Libsystem_Data_BookEditLog.txt"), "r", encoding='utf-8') as f:
            lines = f.readlines()
            
        line_num = 0
        
        # 구분자가 2개인지 확인
        for line in lines:
            line_num += 1
            line = line.strip()
            if line_num ==1 and line == "":
                return True
            if len(line.strip().split("/")) != 3:
                add_error(line_num, "구분자가 2개가 아닙니다")
                return False
            
        line_num = 0

        # 모든 레코드의 앞 3개 항목 비어있지 않는 지 확인
        for line in lines:
            line_num += 1
            log_id, isbn, edit_date = line.strip().split("/")
            if log_id == "" or isbn == "" or edit_date == "":
                add_error(line_num, "필수항목 중 비어있는 항목이 있습니다.")
                return False
            
        line_num = 0

        # 로그 ID 검사
        for line in lines:
            line_num += 1
            log_id, isbn, edit_date = line.strip().split("/")
            # 로그 ID가 숫자인지 확인
            if not log_id.isdigit():
                add_error(line_num, "로그 ID가 숫자가 아닙니다.")
                return False
            
            # 로그 ID 중복 검사
            if lines.count(log_id) > 1:
                add_error(line_num, "로그 ID가 중복됩니다.")
                return False
            
            # 로그 ID가 0 이상인지 확인
            if int(log_id) < 0:
                add_error(line_num, "로그 ID가 0 이상이 아닙니다.")
                return False
            
            # ISBN 검사
            if not isbn.isdigit():
                add_error(line_num, "ISBN이 숫자가 아닙니다.")
                return False
            
            #ISBN 범위
            if int(isbn) < 0 or int(isbn) > 99:
                add_error(line_num, "ISBN이 0에서 99 사이의 정수가 아닙니다.")
                return False
            
            # 로그 날짜 검사
            if not MyDate.from_str(edit_date):
                add_error(line_num, "로그 날짜가 날짜 형식이 아닙니다.")
                return False
            
        return True

    def check_data_borrow_files(self,file_path: str):
        # 오류 발생한 줄과 오류 메세지 파일의 마지막 줄에 추가
        def add_error(line_num, error_message):
            with open(opj(file_path, "data", "Libsystem_Data_Borrow.txt"), "a", encoding='utf-8') as f:
                f.write(f"데이터 파일 무결성 검사에 실패했습니다. 오류 발생 위치 : {line_num}번째 줄 - {error_message}\n")

        with open(opj(file_path, "data", "Libsystem_Data_Borrow.txt"), "r", encoding='utf-8') as f:
            lines = f.readlines()
            
        line_num = 0
        
        # 구분자가 6개인지 확인
        for line in lines:
            line_num += 1
            line = line.strip()
            if line_num ==1 and line == "":
                return True
            if len(line.strip().split("/")) != 7:
                add_error(line_num, "구분자가 6개가 아닙니다")
                return False
            
        line_num = 0

        # 모든 레코드의 앞 6개 항목 비어있지 않는 지 확인
        for line in lines:
            line_num += 1
            borrow_id,book_id, user_id, borrow_date, return_date, actual_return_date, deleted = line.strip().split("/")
            if borrow_id=="" or book_id == "" or user_id == "" or borrow_date == "" or return_date == "" or deleted == "":
                add_error(line_num, "필수항목 중 비어있는 항목이 있습니다.")
                return False
            
        line_num = 0

        for line in lines:
            line_num += 1
            borrow_id,book_id, user_id, borrow_date, return_date, actual_return_date, deleted = line.strip().split("/")
            # 대출 ID가 숫자인지 확인
            if not borrow_id.isdigit():
                add_error(line_num, "대출 ID가 숫자가 아닙니다.")
                return False
            
            # 대출 ID가 0 이상인지 확인
            if int(borrow_id) < 0:
                add_error(line_num, "대출 ID가 0 이상이 아닙니다.")
                return False
            
            # 대출 ID 중복 검사
            if lines.count(borrow_id) > 1:
                add_error(line_num, "대출 ID가 중복됩니다.")
                return False
             
            # 책 ID가 숫자인지 확인
            if not book_id.isdigit():
                add_error(line_num, "책 ID가 숫자가 아닙니다.")
                return False
            
            # 책 ID가 0 이상인지 확인
            if int(book_id) < 0:
                add_error(line_num, "책 ID가 0 이상이 아닙니다.")
                return False
            
            # 책 ID 중복 검사
            if lines.count(book_id) > 1:
                add_error(line_num, "책 ID가 중복됩니다.")
                return False
            
            # 사용자 ID 검사
            if not user_id.isdigit():
                add_error(line_num, "사용자 ID가 숫자가 아닙니다.")
                return False
            
            # 사용자 ID가 0 이상인지 확인
            if int(user_id) < 0:
                add_error(line_num, "사용자 ID가 0 이상이 아닙니다.")
                return False
            
            # 대출 날짜 검사
            if not MyDate.from_str(borrow_date):
                add_error(line_num, "대출 날짜가 날짜 형식이 아닙니다.")
                return False
            
            # 반납 날짜 검사
            if not MyDate.from_str(return_date):
                add_error(line_num, "반납 날짜가 날짜 형식이 아닙니다.")
                return False
            
            # 실제 반납 날짜 검사(실제 반납 존재 시)
            if actual_return_date != "" and not MyDate.from_str(actual_return_date):
                add_error(line_num, "실제 반납 날짜가 날짜 형식이 아닙니다.")
                return False
            
            # 실제 반납 날짜가 대출 날짜 이후인지 확인(실제 반납 존재 시)
            if actual_return_date != "" and MyDate.from_str(actual_return_date) < MyDate.from_str(borrow_date):
                add_error(line_num, "실제 반납 날짜가 대출 날짜 이전입니다.")
                return False
            
            # 반납 날짜가 대출 날짜 이후인지 확인
            if MyDate.from_str(return_date) < MyDate.from_str(borrow_date):
                add_error(line_num, "반납 날짜가 대출 날짜 이전입니다.")
                return False
            
            # 삭제 여부 검사
            if deleted not in ["0", "1"]:
                add_error(line_num, "삭제 여부가 0 또는 1이 아닙니다.")
                return False
            
        return True

    def check_data_user_files(self,file_path: str):
        # 오류 발생한 줄과 오류 메세지 파일의 마지막 줄에 추가
        def add_error(line_num, error_message):
            with open(opj(file_path, "data", "Libsystem_Data_User.txt"), "a", encoding='utf-8') as f:
                f.write(f"데이터 파일 무결성 검사에 실패했습니다. 오류 발생 위치 : {line_num}번째 줄 - {error_message}\n")

        with open(opj(file_path, "data", "Libsystem_Data_User.txt"), "r", encoding='utf-8') as f:
            lines = f.readlines()
            
        line_num = 0
        
        # 구분자가 3개인지 확인
        for line in lines:
            line_num += 1
            line = line.strip()
            if line_num ==1 and line == "":
                return True
            if len(line.strip().split("/")) != 4:
                add_error(line_num, "구분자가 3개가 아닙니다")
                return False
            
        line_num = 0

        # 모든 레코드의 앞 4개 항목 비어있지 않는 지 확인
        for line in lines:
            line_num += 1
            user_id, phone_number, name, deleted = line.strip().split("/")
            if user_id == "" or phone_number == "" or name == "" or deleted == "":
                add_error(line_num, "필수항목 중 비어있는 항목이 있습니다.")
                return False
            
        line_num = 0

        # 사용자 ID 검사
        for line in lines:
            line_num += 1
            user_id, phone_number, name, deleted = line.strip().split("/")
            # 사용자 ID가 숫자인지 확인
            if not user_id.isdigit():
                add_error(line_num, "사용자 ID가 숫자가 아닙니다.")
                return False
            
            # 사용자 ID가 0 이상인지 확인
            if int(user_id) < 0:
                add_error(line_num, "사용자 ID가 0 이상이 아닙니다.")
                return False
            
            # 사용자 ID 중복 검사
            if lines.count(user_id) > 1:
                add_error(line_num, "사용자 ID가 중복됩니다.")
                return False
            
            # 전화번호 검사
            if not self.check_phone_number_validate(phone_number):
                add_error(line_num, "전화번호가 숫자가 아닙니다.")
                return False
            
            # 이름에 '/'나 '\'가 포함되어 있는지 확인
            if "/" in name or "\\" in name:
                add_error(line_num, "이름에 '/'나 '\\'가 포함되어 있습니다.")
                return False
            
            # 삭제 여부 검사
            if deleted not in ["0", "1"]:
                add_error(line_num, "삭제 여부가 0 또는 1이 아닙니다.")
                return False
            
        return True

    def check_data_publisher_files(self,file_path: str):
        # 오류 발생한 줄과 오류 메세지 파일의 마지막 줄에 추가
        def add_error(line_num, error_message):
            with open(opj(file_path, "data", "Libsystem_Data_Publisher.txt"), "a", encoding='utf-8') as f:
                f.write(f"데이터 파일 무결성 검사에 실패했습니다. 오류 발생 위치 : {line_num}번째 줄 - {error_message}\n")

        with open(opj(file_path, "data", "Libsystem_Data_Publisher.txt"), "r", encoding='utf-8') as f:
            lines = f.readlines()
            
        line_num = 0

        # 구분자가 2개인지 확인
        for line in lines:
            line_num += 1
            line = line.strip()
            if line_num ==1 and line == "":
                return True
            if len(line.strip().split("/")) != 3:
                add_error(line_num, "구분자가 2개가 아닙니다")
                return False
            
        line_num = 0

        # 모든 레코드의 앞 3개 항목 비어있지 않는 지 확인
        for line in lines:
            line_num += 1
            publisher_id, name, deleted = line.strip().split("/")
            if publisher_id == "" or name == "" or deleted == "":
                add_error(line_num, "필수항목 중 비어있는 항목이 있습니다.")
                return False
            
        line_num = 0

        # 출판사 ID 검사
        for line in lines:
            line_num += 1
            publisher_id, name, deleted = line.strip().split("/")
            # 출판사 ID가 숫자인지 확인
            if not publisher_id.isdigit():
                add_error(line_num, "출판사 ID가 숫자가 아닙니다.")
                return False
            
            # 출판사 ID가 0 이상인지 확인
            if int(publisher_id) < 0:
                add_error(line_num, "출판사 ID가 0 이상이 아닙니다.")
                return False
            
            # 출판사 ID 중복 검사
            if lines.count(publisher_id) > 1:
                add_error(line_num, "출판사 ID가 중복됩니다.")
                return False
            
            # 이름에 '/'나 '\'가 포함되어 있는지 확인
            if "/" in name or "\\" in name:
                add_error(line_num, "출판사 이름에 '/'나 '\\'가 포함되어 있습니다.")
                return False
            
            # 삭제 여부 검사
            if deleted not in ["0", "1"]:
                add_error(line_num, "삭제 여부가 0 또는 1이 아닙니다.")
                return False
            
        return True
    
    def check_data_overdue_penalty_files(self,file_path: str):
        # 오류 발생한 줄과 오류 메세지 파일의 마지막 줄에 추가
        def add_error(line_num, error_message):
            with open(opj(file_path, "data", "Libsystem_Data_OverduePenalty.txt"), "a", encoding='utf-8') as f:
                f.write(f"데이터 파일 무결성 검사에 실패했습니다. 오류 발생 위치 : {line_num}번째 줄 - {error_message}\n")

        with open(opj(file_path, "data", "Libsystem_Data_OverduePenalty.txt"), "r", encoding='utf-8') as f:
            lines = f.readlines()

        line_num = 0

        # 모든 레코드의 앞 4개 항목 비어있지 않는 지 확인
        for line in lines:
            line_num += 1
            line = line.strip()
            if line_num ==1 and line == "":
                return True
            # 구분자가 3개인지 확인
            if len(line.strip().split("/")) != 4:
                add_error(line_num, "구분자가 3개가 아닙니다")
                return False

            panalty_id, user_id, panalty_start_date, panalty_end_date = line.strip().split("/")
            if panalty_id == "" or user_id == "" or panalty_start_date == "" or panalty_end_date == "":
                add_error(line_num, "필수항목 중 비어있는 항목이 있습니다.")
                return False
            
            # 패널티 ID가 숫자인지 확인
            if not panalty_id.isdigit():
                add_error(line_num, "패널티 ID가 숫자가 아닙니다.")
                return False
            
            # 패널티 ID가 0 이상인지 확인
            if int(panalty_id) < 0:
                add_error(line_num, "패널티 ID가 0 이상이 아닙니다.")
                return False
            
            # 패널티 ID 중복 검사
            if lines.count(panalty_id) > 1:
                add_error(line_num, "패널티 ID가 중복됩니다.")
                return False
            
            # 사용자 ID가 숫자인지 확인
            if not user_id.isdigit():
                add_error(line_num, "사용자 ID가 숫자가 아닙니다.")
                return False
            
            # 사용자 ID가 0 이상인지 확인
            if int(user_id) < 0:
                add_error(line_num, "사용자 ID가 0 이상이 아닙니다.")
                return False
            
            # 패널티 시작 날짜 검사
            if not MyDate.from_str(panalty_start_date):
                add_error(line_num, "패널티 시작 날짜가 날짜 형식이 아닙니다.")
                return False
            
            # 패널티 종료 날짜 검사
            if not MyDate.from_str(panalty_end_date):
                add_error(line_num, "패널티 종료 날짜가 날짜 형식이 아닙니다.")
                return False
            
            # 패널티 종료 날짜가 패널티 시작 날짜 이후인지 확인
            if MyDate.from_str(panalty_end_date) < MyDate.from_str(panalty_start_date):
                add_error(line_num, "패널티 종료 날짜가 패널티 시작 날짜 이전입니다.")
                return False
            
        return True
    
    # =========== 책 레코드를 문자열로 반환 ========== #
    def print_book(self, book_id: int, include_borrow: bool=False):        
        # find book
        book_data = None
        for book in self.book_table:
            if book.book_id == book_id:
                book_data = book
                break
            
        if book_data is None:
            raise NotImplementedError("해당 고유번호를 가진 책이 존재하지 않습니다.")
        
        # find isbn
        isbn_data = None
        for isbn in self.isbn_table:
            if isbn.isbn == book.isbn:
                isbn_data = isbn
                break
            
        # find author isbn relationship
        author_isbn_data = []
        for isbn_author in self.isbn_author_table:
            if isbn_author.isbn == isbn_data.isbn:
                author_isbn_data.append(isbn_author)
        
        author_data = []
        for author in self.author_table:
            for author_isbn in author_isbn_data:
                if author.author_id == author_isbn.author_id:
                    author_data.append(author)
            
        # find publisher
        publisher_data = None
        for publisher in self.publisher_table:
            if publisher.publisher_id == isbn_data.publisher_id:
                publisher_data = publisher
                break
            
        # find borrow info
        borrow_data = None
        if include_borrow:
            for borrow in self.borrow_table:
                if borrow.book_id == book_id:
                    borrow_data = borrow
                    break
        
        # find borrow user info
        user_data = None
        if include_borrow and borrow_data is not None:
            for user in self.user_table:
                if user.user_id == borrow_data.user_id:
                    user_data = user
                    break
                
        return_str = f"{book_id}/"
        return_str += str(isbn_data.isbn).zfill(2) + "/"
        return_str += f"{isbn_data.title}/"
        return_str += f"{' & '.join(list(map(lambda x: f'{x.name} #{x.author_id}', author_data)))}/"
        return_str += f"{publisher_data.name}/"
        return_str += f"{isbn_data.published_year}/"
        return_str += str(book_data.register_date)
        
        if include_borrow and borrow_data is not None:
            return_str += f"/{user_data.phone_number} {user_data.name}"
            return_str += f"/{str(borrow_data.borrow_date)} ~ {str(borrow_data.return_date)}"
            
            if borrow_data.actual_return_date is None and borrow_data.return_date < self.today:
                return_str += f" *"
        
        return return_str
    
    # =========== 헤더 출력 ========== #
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

    # =========== 전체 책 출력 ========== #
    def print_book_all(self):
        print(DataManager.get_header())
        for book in self.book_table:
            print(self.print_book(book.book_id, include_borrow=True))

    def load_configuration(self) -> dict:
        config_dict = dict()
        
        try:
            # 설정 파일 읽기
            with open(opj(self.file_path, "Libsystem_Config.json"), "r") as f:
                config = json.load(f)
            
            # 설정 값 처리
            for c in config['configuration']:
                if c['value_type'] == 'int':
                    config_dict[c['constant_name']] = int(c['value'])
                elif c['value_type'] == 'float':
                    config_dict[c['constant_name']] = float(c['value'])
                else:
                    config_dict[c['constant_name']] = c['value']
            
            # config 설정
            self.config = config_dict

        except FileNotFoundError:
            print("설정 파일을 찾을 수 없습니다. 기본값으로 새로 생성합니다.")
            self.create_default_configuration()
        
        except json.JSONDecodeError:
            print("설정 파일이 손상되었습니다. 기본값으로 복구합니다.")
            self.create_default_configuration()
        
        except Exception as e:
            print(f"알 수 없는 오류가 발생했습니다: {e}. 기본값으로 복구합니다.")
            self.create_default_configuration()
        
        # 디버깅 및 기본값 보장
        if "cancel" not in self.config:
            print("ERROR: 'cancel' 키가 설정에 없습니다. 기본값 'X'를 추가합니다.")
            self.config["cancel"] = "X"
    def create_default_configuration(self):
        # 기본 설정값
        default_config = {
            "configuration": [
                {
                    "constant_name": "borrow_date",
                    "value_type": "int",
                    "value": 7
                },
                {
                    "constant_name": "cancel",
                    "value_type": "str",
                    "value": "X"
                },
                {
                    "constant_name": "max_static_id",
                    "value_type": "int",
                    "value": 99
                },
                {
                    "constant_name": "max_isbn",
                    "value_type": "int",
                    "value": 99
                },
                {
                    "constant_name": "max_borrow_count",
                    "value_type": "int",
                    "value": 3
                },
                {
                    "constant_name": "overdue_penalty_scale",
                    "value_type": "float",
                    "value": 1.0
                }
            ]
        }
        
        # 기본값으로 설정
        config_dict = {
            "borrow_date": 7,
            "cancel": "X",
            "max_static_id": 99,
            "max_isbn": 99,
            "max_borrow_count": 3,
            "overdue_penalty_scale": 1.0
        }
        
        self.config = config_dict
        
        # 설정 파일 저장
        with open(opj(self.file_path, "Libsystem_Config.json"), "w", encoding="utf-8") as f:
            json.dump(default_config, f, indent=4)
        print("기본 설정 파일이 생성되었습니다.")


    # ========== 검사 함수 ========== #
    def check_book_id_validate(self, book_id, flag): # flag == 0 -> 있으면 False 없으면 True, flag == 1 -> 없으면 False 있으면 True
        if book_id == self.config["cancel"]:
            return True, ""

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
        if book_id_int < 0 or book_id_int > self.config['max_static_id']:
            return False, f"고유번호는 0에서 {config['max_static_id']} 사이여야 합니다."
        
        if flag == 0 and self.search_book_by_id(book_id_int):
            return False, "중복된 고유번호가 존재합니다."
        
        if flag == 1 and self.search_book_by_id(book_id_int) is None:
            return False, "해당 고유번호를 가진 책이 존재하지 않습니다."
        
        return True, ""

    def check_string_validate(self, field_name, value):
        # "cancel" 키가 없을 경우 기본값 "X"를 반환
        if value == self.config.get("cancel", "X"):  
            return True, ""
        # 1. 문자열의 길이가 1 이상인지 확인
        if len(value) < 1:
            return False, f"책의 {field_name}은 1글자 이상이어야 합니다."
        # 2. 문자열이 공백인지 확인
        if value.strip() == "":
            return False, f"책의 {field_name}은 공백일 수 없습니다."
        # 3. 허용되지 않는 특수 기호가 포함되어 있는지 확인
        if '/' in value or '\\' in value:
            return False, f"책의 {field_name}에 특수문자 \"/\" 또는 \"\\\"는 허용되지 않습니다."
        
        return True, ""

    def check_year_validate(self, year):
        cancel_value = self.config.get("cancel", "X")  # 기본값 "X" 설정
        if year == cancel_value:
            return True, ""
        # 1. 입력값이 숫자인지 확인
        if not year.isdigit():
            return False, "책의 출판년도는 오로지 숫자로만 구성되어야 합니다."
        
        # 2. 출판년도는 4자리 숫자여야 함을 확인
        if len(year) != 4:
            return False, "책의 출판년도는 4자리 양의 정수여야 합니다."
        
        year_int = int(year)
        current_year = self.today.year  # 현재 연도를 확인하는 변수

        # 3. 출판년도 범위 확인
        if year_int < 1583:
            return False, "책의 출판년도는 1583년 이후인 4자리 양의 정수여야 합니다."
        elif year_int > current_year:
            return False, f"책의 출판년도는 현재연도({current_year}년)보다 미래일 수 없습니다."
        
        return True, ""

    @classmethod
    def check_date_validate(self, date_str):
        date_pattern = r'^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$'
        
        try:
            assert type(date_str) == str, "문자열이 아님"
            
            if not re.match(date_pattern, date_str):
                raise ValueError
            
            year, month, day = map(int, date_str.split("-"))
            
            # 연도가 1583 이��� 9999 이하인지 확인
            if not (1583 <= year <= 9999):
                return False, "날짜는 1583년부터 9999년 사이여야 합니다."
            
            if not MyDate.validate_day(year, month, day):
                raise ValueError
            
            return True, ""
        
        except:
            return False, "날짜 형식이 올바르지 않습니다. (예: YYYY-MM-DD)"

    def check_isbn_validate(self, isbn):
        cancel_value = self.config.get("cancel", "X")  # 기본값 "X" 설정
        if isbn == cancel_value:
            return True, ""
        # ISBN이 공백인지 확인
        if not isbn.strip():  # 공백을 제거한 후 빈 문자열인지 확인
            return False, "책의 ISBN은 공백일 수 없습니다."
        # ISBN이 두 자리 숫자(00~99)로 구성되어 있는지 확인
        if len(isbn) != 2 or not isbn.isdigit():
            return False, "ISBN은 두 자리 숫자여야 합니다."
        return True, ""
    
    def check_author_id_validate(self, author_id):
        if not author_id.isdigit():
            return False, "저자 식별번호는 숫자여야 합니다."
        
        if author_id.startswith('0'):
            return False, "저자 식별번호는 0으로 시작할 수 없습니다."
            
        return True, ""

    def check_phone_number_validate(self, phone_number):
        if phone_number == self.config["cancel"]:
            return True, ""
        # 정규표현식으로 010-XXXX-XXXX 형식 확인
        pattern = r'^010-\d{4}-\d{4}$'
        if re.fullmatch(pattern, phone_number):
            return True, ""
        return False, "전화번호는 010-XXXX-XXXX 형식이어야 합니다."
    
    # def get_author_by_name(self, author_name): # 저자 이름으로 저자 정보 조회
    #     for author in self.author_table:
    #         if author.name == author_name:
    #             return author
    #     return None

    # def get_author_by_id(self, author_id): # 저자 ID로 저자 정보 조회
    #     for author in self.author_table:
    #         if author.author_id == author_id:
    #             return author
    #     return None

    def check_author_validate(self, parts_used,value):
        valid_author = None
        error_messages = ""
        
        # 입력값이 뒤로가기 문자와 일치하는지 확인
        if value == self.config["cancel"]:
            return True, ""
        
        authors = [author.strip() for author in value.split("&") if author.strip()]

        # authors에 등록된 저자가 0명일 경우 True 반환
        if len(authors) == 0:
            return True, ""
        
        for author in authors:
            # "/","\"가 포함되어 있는지 확인
            if "/" in author or "\\" in author:
                error_messages += f"[{author}] ERROR: 책의 저자에 특수문자 \"/\" 또는 \"\"을 입력할 수 없습니다.\n"

            # 저자에 "#"이 한 개 이하로 있는지 확인
            if author.count("#") > 1:
                error_messages += f"[{author}] ERROR: 저자의 형식은 \"이름\" 또는 \"이름 #식별번호\" 둘 중 하나여야 합니다.\n"
            
            if '#' in author:
                # '#'이 있다면 왼쪽이 저자의 이름이고, 오른쪽이 식별번호
                author_name, author_id = author.split("#")
            else:
                author_name = author
                author_id = None

            # 저자의 이름이 1글자 이상인지 확인
            if not author_name.strip():
                error_messages += f"[{author}] ERROR: 저자의 형식은 \"이름\" 또는 \"이름 #식별번호\" 둘 중 하나여야 합니다.\n"

            # 저자의 이름이 공백인지 확인
            if not author_name.strip():
               error_messages += f"[{author}] ERROR: 저자의 형식은 \"이름\" 또는 \"이름 #식별번호\" 둘 중 하나여야 합니다.\n"
            
            # 저자의 식별번호가 숫자로만 구성되어 있는지 확인
            if author_id is not None and not author_id.isdigit():
                error_messages += f"[{author}] ERROR: 특수문자 \"#\"의 오른쪽에는 식별번호만 허용됩니다.\n"
        
            # 저자의 식별번호가 1 이상인지 확인
            if author_id is not None and int(author_id) < 1:
                error_messages += f"[{author}] ERROR: 저자의 식별번호는 1 이상이어야 합니다.\n"
        
            # # 저자의 식별번호가 존재하는 경우, 실제로 유효한지 확인
            # if author_id is not None:
            #     valid_author = self.get_author_by_id(author_id)  # 가정: 이 메서드는 저자 ID로 저자 정보를 조회하는 함수
            
            # if author_id is not None and valid_author is None:
            #     error_messages += f"[{author}] ERROR: {author_id}번 저자는 없습니다.\n"
            
            # elif author_id is not None and valid_author.name != author_name.strip():
            #     error_messages += f"[{author}] ERROR: {author_id}번 저자의 이름은 \"{valid_author.name}\"가 아닙니다.\n"     
                
            # # 저자의 이름만 존재하고, 사용 파트가 "수정"인 경우 해당 저자가 존재하는지 확인
            # if author_id is None and parts_used == "수정":
            #     valid_author = self.get_author_by_name(author_name)  # 가정: 이 메서드는 저자 이름으로 저자 정보를 조회하는 함수
            #     if not valid_author:
            #         error_messages += f"[{author}] ERROR: 입력한 저자의 식별번호가 없습니다.\n"
                
            
        # 저자가 5명 이상인지 확인
        if len(authors) > 5:
            error_messages += "\nERROR: 책의 저자는 최대 5명입니다.\n"
        
        # 오류 메시지가 있다면 반환
        if error_messages:
            return False, error_messages.strip()
    
        return True, ""
    
    def check_author_id_validate(self, author_id): 
        if author_id == self.config["cancel"]:
            return True, ""
        # 1. 입력값이 있는지 확인
        if len(author_id) == 0:
            return False, "1글자 이상 입력해주세요."
        
        # 2. 입력값이 공백으로만 구성되지 않았는지 확인
        if author_id.isspace():
            return False, "저자의 식별번호는 공백일 수 없습니다."
        
        # 3. 저자의 식별번호가 숫자로만 구성되어 있는지 확인
        if not author_id.isdigit():
            return False, "저자의 식별번호는 숫자여야 합니다."
        
        # 4. 저자의 식별번호가 1 이상인지 확인
        if int(author_id) < 1:
            return False, "저자의 식별번호는 1 이상이어야 합니다."
        
        return True, ""

    def check_return_day_validate(self, return_day):
        if return_day == self.config["cancel"]:
            return True, ""
        # 입력값이 있는지 확인
        if len(return_day) == 0:
            return False, "1글자 이상 입력해주세요."
            
        # 값이 0보다 작은지 확인
        if int(return_day) < 0:
            return False, "0 이상의 올바른 정수를 입력해주세요."
        
        return True, ""

    def check_overdue_delete(self, book_id):
        for book in self.book_table:
            for borrow in self.borrow_table:
                if borrow.book_id == book_id and borrow.actual_return_date is None:
                    return True
        return False

    # def check_record_validate(self, book: BookRecord) -> tuple[bool, str]:
    #     # ISBN, 책 제목, 저자, 출판사, 출판년도, 등록 날짜 유효성 검사
    #     is_valid, error_message = self.check_isbn_validate(str(book.isbn))
    #     if not is_valid:
    #         return False, f"ISBN 에러: {error_message}"
        
    #     is_valid, error_message = self.check_string_validate("제목", book.title)
    #     if not is_valid:
    #         return False, f"제목 에러: {error_message}"
        
    #     is_valid, error_message = self.check_string_validate("저자", book.author)
    #     if not is_valid:
    #         return False, f"저자 에러: {error_message}"
        
    #     is_valid, error_message = self.check_string_validate("출판사", book.publisher)
    #     if not is_valid:
    #         return False, f"출판사 에러: {error_message}"
        
    #     is_valid, error_message = self.check_year_validate(str(book.published_year))
    #     if not is_valid:
    #         return False, f"출판년도 에러: {error_message}"
        
    #     is_valid, error_message = self.check_date_validate(str(book.register_date))
    #     if not is_valid:
    #         return False, f"등록 날짜 에러: {error_message}"

    #      # 대출 중인 경우 대출자 이름, 대출자 전화번호, 대출 날짜, 반납 예정일에 대한 추가 유효성 검사
    #     if book.is_borrowing:

    #         is_valid, error_message = self.check_string_validate("대출자", book.borrower_name)
    #         if not is_valid:
    #             return False, f"대출자 에러: {error_message}"
        
    #         is_valid, error_message = self.check_phone_number_validate(book.borrower_phone_number)
    #         if not is_valid:
    #             return False, f"전화번호 에러: {error_message}"
        
    #         is_valid, error_message = self.check_date_validate(str(book.borrow_date))
    #         if not is_valid:
    #             return False, f"대출 날짜 에러: {error_message}"
        
    #         is_valid, error_message = self.check_date_validate(str(book.return_date))
    #         if not is_valid:
    #             return False, f"반납 예정일 에러: {error_message}"
    #     else:
    #         # 대출자 정보가 없는 경우 대출 관련 필드가 비어있는지 확인
    #         if book.borrower_name or book.borrower_phone_number or book.borrow_date or book.return_date:
    #             return False, "대출 중이 아닌 도서에 대출 정보가 있습니다."

    #     return True, ""

    # def check_overdue_delete(self, book_id):
    #     for book in self.book_data:
    #         if book.book_id == book_id and book.return_date:
    #             return True
    #     return False

    def check_overdue_delete(self, book_id):
        for borrow in self.borrow_table:
            if borrow.book_id == book_id and borrow.return_date < self.today:
                return True
        return False        

    # ========== 검색 함수 ========== #
    # 고유번호로 검색
    def search_book_by_id(self, book_id) -> BookRecord:
        """_summary_ 
        책 고유번호로 책 인스턴스 반환
        """
        for book in self.book_table:
            if book.book_id == book_id:
                return book
    
    # isbn 정보 검색 (제목, 저자, 출판사 등)
    def search_isbn_data(self, isbn) -> ISBNRecord:
        """_summary_
        ISBN으로 ISBN 인스턴스 반환
        """
        for i in self.isbn_table:
            if i.isbn == isbn:
                return i
            
        return None
    
    # Book 테이블 내 isbn을 갖는 모든 책 검색
    def search_books_by_isbn(self, isbn) -> list[int]:
        """_summary_
        ISBN을 가지는 모든 책 인스턴스 반환
        """
        books = []
        for book in self.book_table:
            if book.isbn == isbn:
                books.append(book)
                
        return books
    
    # Author ID로 검색
    def search_author_by_id(self, author_id) -> AuthorRecord:
        """_summary_
        Author ID로 Author 인스턴스 반환
        """
        if author_id < 1:
            return None
        
        for author in self.author_table:
            if author.author_id == author_id:
                return author
            
        return None
    
    def search_author_by_name(self, name) -> list[AuthorRecord]:
        authors = []
        for author in self.author_table:
            if author.name == name:
                authors.append(author)
                
        return authors
    
    # Publisher ID로 검색
    def search_publisher_by_id(self, publisher_id) -> PublisherRecord:
        """_summary_
        Publisher ID로 Publisher 인스턴스 반환
        """
        if publisher_id < 0:
            return None
        
        for publisher in self.publisher_table:
            if publisher.publisher_id == publisher_id:
                return publisher
            
        return None
    
    # 저자가 작성한 책 ISBN 검색
    def search_isbns_by_author_id(self, author_id) -> list[int]:
        """_summary_
        저자 ID를 가지는 저자가 작성한 모든 책의 ISBN 반환
        """
        isbns = []
        for isbn_author in self.isbn_author_table:
            if isbn_author.author_id == author_id:
                isbns.append(isbn_author.isbn)
                
        return isbns
    
    # ISBN의 저자 모두 검색
    def search_author_ids_by_isbn(self, isbn) -> list[int]:
        """_summary_
        ISBN 책을 작성한 모든 저자 ID 반환
        """
        author_ids = []
        for isbn_author in self.isbn_author_table:
            if isbn_author.isbn == isbn:
                author_ids.append(isbn_author.author_id)
                
        return author_ids

    # 전화번호로 유저 검색 (전화번호는 unique)
    def search_user_by_phone_number(self, phone_number) -> UserRecord:
        """_summary_
        전화번호로 유저 인스턴스 반환
        """
        for user in self.user_table:
            if user.phone_number == phone_number:
                return user
            
    # 이름으로 유저 검색
    def search_users_by_name(self, name) -> list[UserRecord]:
        """_summary_
        이름으로 일치하는 모든 유저 인스턴스 반환
        """
        users = []
        for user in self.user_table:
            if user.name == name:
                users.append(user)
                
        return users
    
    # 유저 ID로 검색
    def search_user_by_id(self, user_id) -> UserRecord:
        """_summary_
        User ID로 일치하는 유저 인스턴스 반환
        """
        for user in self.user_table:
            if user.user_id == user_id:
                return user
            
        return None
    
    # 대출중인 책 검색
    def search_borrowing_book_ids_by_user_id(self, user_id, overdue_only:bool=False) -> list[int]:
        """_summary_
        유저 ID를 갖는 사용자가 대출중인 책의 고유번호 반환
        overdue_only=False -> 대출중인 책 모두 검색 (연체중 포함)
        overdue_only=True -> 연체중인 책만 검색
        """
        book_ids = []
        
        for borrow in self.borrow_table:
            if borrow.user_id == user_id and borrow.actual_return_date is None:
                # 대출중인 책 모두 검색 (연체중 포함)
                if not overdue_only:
                    book_ids.append(borrow.book_id)
                    
                # 연체중인 책만 검색
                else:
                    if borrow.return_date < self.today:
                        book_ids.append(borrow.book_id)
        
        return book_ids
    
    def search_borrow_dates_by_book_id(self, book_id):
        book_dates = []
        for borrow in self.borrow_table:
            if borrow.book_id == book_id: # (대출일, user_id, 반납일) 튜플 반환
                book_dates.append((borrow.borrow_date,borrow.user_id,borrow.return_date))
        
        return book_dates
    
    def search_return_dates_by_book_id(self, book_id):
        book_dates=[]
        for borrow in self.borrow_table:
            if borrow.book_id == book_id and borrow.actual_return_date is not None: # (반납일, 연체일) 튜플 반환
                book_dates.append((borrow.actual_return_date,borrow.actual_return_date - borrow.return_date))
        
        return book_dates
        
    # 해당 책을 대출한 유저 ID 반환
    def search_borrower_id_by_book_id(self, book_id) -> int:
        """_summary_
        해당 book id 책을 대출한 유저 ID 반환
        """
        for borrow in self.borrow_table:
            if borrow.book_id == book_id and borrow.actual_return_date is None:
                return borrow.user_id
            
        return None
        
    # 연체 패널티 user id로 검색
    def search_overdue_penalty_by_user_id(self, user_id) -> bool:
        """_summary_
        해당 User ID를 가진 사용자가 연체 패널티를 받고 있는지 확인
        """
        for penalty in self.overdue_penalty_table:
            if penalty.user_id == user_id and penalty.penalty_end_date >= self.today >= penalty.penalty_start_date:
                return True
        
        return False
            
    def search_borrow_by_user_id(self, book_id, user_id) -> BorrowRecord:
        """_summary_
        해당 유저가 해당 책을 대출한 대출 Borrow 인스턴스 반환
        """
        for borrow in self.borrow_table:
            if borrow.book_id == book_id and borrow.user_id == user_id:
                return borrow
            
        return None
    
    # 출판사 이름으로 검색
    def search_publisher_by_name(self, name) -> PublisherRecord:
        """_summary_
        출판사 이름으로 출판사 인스턴스 반환 (출판사 이름은 unique함)
        """
        for publisher in self.publisher_table:
            if publisher.name == name:
                return publisher
            
        return None
    
    # ========== 1. 추가 ========== #
    def add_book(self):
        if self.is_full():
            print("더 이상 추가할 수 없습니다.")
            return False
        
        isbn = self.input_isbn("추가할 책의 ISBN을 입력하세요: ")
        if not isbn:
            return False

        if isbn == self.config["cancel"]:
            print("추가를 중단하며 메인 프롬프트로 돌아갑니다.")
            return False
        
        isbn = int(isbn)
        book_info = []
        books = self.search_books_by_isbn(isbn)
        
        # ISBN 최초 등록
        if not books:
            messages_and_functions = [
                ("추가할 책의 제목을 입력하세요: ", self.input_bookName),
                ("추가할 책의 저자를 입력하세요: ", self.input_author),
                ("추가할 책의 출판사를 입력하세요: ", self.input_publisher),
                ("추가할 책의 출판년도를 입력하세요: ", self.input_year),
            ]
            
            for message, func in messages_and_functions:
                info = func(message)
                if not info:
                    return False

                if info == self.config["cancel"]:
                    print("추가를 중단하며 메인 프롬프트로 돌아갑니다.")
                    return False
                    
                book_info.append(info)
        
            
            # 출판사 있는지 검색, 없으면 추가
            publisher = self.search_publisher_by_name(book_info[2])
            
            if not publisher:
                publisher_flag = False
                publisher_id = len(self.publisher_table) + 1
                publisher = PublisherRecord(len(self.publisher_table) + 1, book_info[2], False)
            else:
                publisher_flag = True
                publisher_id = publisher.publisher_id
                
            # isbn 데이터
            new_isbn = ISBNRecord(isbn, book_info[0], publisher_id, book_info[3], self.today)

            # book 데이터
            book_id = len(self.book_table)
            new_book = BookRecord(book_id, isbn, self.today, None, False)
            
            author_string = ""
            if not book_info[1]:
                author_string = "-"
            else:
                for i, author in enumerate(book_info[1]):
                    if i == len(book_info[1]) - 1:
                        author_string += author
                    else:
                        author_string += f"{author} & "
            
            print(f"{book_id}/{new_isbn.isbn}/{new_isbn.title}/{author_string}/{publisher.name}/{new_isbn.published_year}/{new_isbn.isbn_register_date}")
            print()
            
            if self.input_response("해당 책을 추가하시겠습니까?(Y/N): "):
                if not publisher_flag:
                    self.publisher_table.append(publisher)
                
                for author in book_info[1]:
                    if not isinstance(author, AuthorRecord):
                        self.author_table.append(AuthorRecord(len(self.author_table) + 1, author, False))
                self.isbn_table.append(new_isbn)
                self.book_table.append(new_book)    
                
                self.write_data_files()
                return True
            else:
                print("추가를 중단하며 메인 프롬프트로 돌아갑니다.")
                return False
                
        # 이미 ISBN이 존재하는 경우
        else:
            print(f"ISBN이 {isbn}인 책이 이미 {len(books)}권이 있습니다.")
            
            print(self.get_header())
            print()
            
            for book in books:
                print(self.print_book(book.book_id, include_borrow=True))
            print("\n여기에\n")
            
            isbn_data = self.search_isbn_data(isbn)
            publisher = self.search_publisher_by_id(isbn_data.publisher_id)
            author_ids = self.search_author_ids_by_isbn(isbn)
            
            print(f"{len(self.book_table)}/{isbn_data.isbn}/{isbn_data.title}/", end="")
                
            author_data = []
            for author_id in author_ids:
                author = self.search_author_by_id(author_id)
                author_data.append(f"{author.name} #{author.author_id}")
                
            print(" & ".join(author_data), end="")
                  
            print(f"/{publisher.name}/{isbn_data.published_year}/{self.today}")
            print()
            
            if self.input_response("해당 책을 추가하시겠습니까?(Y/N): "):
                new_book = BookRecord(len(self.book_table), isbn, self.today, None, False)
                self.book_table.append(new_book)
                self.fetch_data_file()
                return True
            else:
                print("추가를 중단하며 메인 프롬프트로 돌아갑니다.")
                return False
    
    # ========== 2. 삭제 ========== #
    def delete_book(self):
        del_book_id = self.input_book_id("삭제할 책의 고유번호를 입력해주세요: ", 1)
        
        if (del_book_id == None):
            return False
        
        if del_book_id == self.config["cancel"]:
            print("삭제를 중단하며 메인 프롬프트로 돌아갑니다.")
            return False
        
        del_book_id = int(del_book_id)
        
        if self.check_overdue_delete(del_book_id):
            print("ERROR: 해당 책은 대출중이므로 삭제할 수 없습니다.")
            return False
        else:
            print("책이 특정되었습니다.")
            print(self.get_header(contain_borrow_info=False))
            print()
            print(self.print_book(del_book_id, include_borrow=False))
            print()
            
            if self.confirm_delete(del_book_id):
                self.fetch_data_file()
        
    def confirm_delete(self, del_book_id):
        if self.input_response("삭제하면 되돌릴 수 없습니다. 정말로 삭제하시겠습니까?(Y/N): "):
            self.book_table = [book for book in self.book_table if book.book_id != del_book_id]
            print("삭제가 완료되었습니다. 메인프롬프트로 돌아갑니다.")
            return True
        else:
            print("삭제를 취소하였습니다. 메인프롬프트로 돌아갑니다.")
            return False
        
    def check_author_validate(self, authors_input: str):
        """
        입력받은 저자 문자열을 검증하고 유효성과 오류 메세지를 반환합니다.
        """
        input_author_list = [author.strip() for author in authors_input.split("&") if author.strip()]

        if not input_author_list:
            return True, None
        
        if len(input_author_list) > 5:
            return False, "저자 입력이 5명을 초과합니다."
        
        for author in input_author_list:
            if "#" in author:
                name, number = author.split("#")
                name = name.strip()
                number = number.strip()
            else:
                name = author.strip()
                number = None

            is_valid, error_message = self.check_string_validate("저자", name)
            if not is_valid:
                return False, error_message

            if number:
                is_valid, error_message = self.check_author_id_validate(number)
                if not is_valid:
                    return False, error_message

                author_data = self.search_author_by_id(int(number))
                if not author_data:
                    return False, f"{int(number)}번 저자가 존재하지 않습니다."
                elif author_data.name != name:
                    return False, f"{int(number)}번 저자의 이름은 '{name}'이 아닙니다."
        
        return True, None
        
    
    
    def validate_publisher(self, publisher_name: str) -> int:
        """
        입력받은 출판사를 검증하고, 유효한 출판사의 ID를 반환합니다.
        """
        publisher = self.search_publisher_by_name(publisher_name.strip())
        if not publisher:
            print(f"[ERROR] 출판사 '{publisher_name}'가 존재하지 않습니다.")
            return None
        return publisher.publisher_id

    # ========== 3. 수정 ========== #
    def update_book(self):
        isbn = self.input_isbn("수정할 책의 ISBN을 입력하세요: ")
        if not isbn or not self.check_isbn_validate(isbn):
            print("ERROR: 입력한 ISBN이 유효하지 않습니다.")
            return False

        cancel_value = self.config.get("cancel", "X")  # 기본값 "X" 설정
        if isbn == cancel_value:
            print("수정을 중단하며 메인 프롬프트로 돌아갑니다.")
            return False
        
        isbn = int(isbn)
        books = self.search_books_by_isbn(isbn)
        if not books:
            print("ERROR: 해당 ISBN을 가진 책이 존재하지 않습니다.")
            return False
        else:
            print(f"ISBN이 {isbn}인 책 데이터가 {len(books)}권 있습니다.")
            print()
            print(self.get_header(contain_borrow_info=False))
            for book in books:
                print(self.print_book(book.book_id, include_borrow=False))
        
        # 1. 책 제목 입력
        new_title = self.input_bookName("수정할 책의 제목을 입력해주세요: ")
        if not new_title or not self.check_string_validate("제목", new_title):
            return False

        # 2. 책 저자 입력
        while True:
            new_authors = input("수정할 책의 저자를 입력해주세요 (이름 #번호 & ...): ").strip()
            if new_authors == cancel_value:
                print("수정을 중단하며 메인 프롬프트로 돌아갑니다.")
                return False

            # "&"로 구분하여 입력 분리 및 공백 제거
            author_list = [author.strip() for author in new_authors.split("&") if author.strip()]
            if not author_list:
                print("저자가 없는 책으로 처리됩니다.")
                valid_authors = []
                break

            if len(author_list) > 5:
                print("ERROR: 저자 입력이 5명을 초과합니다. 다시 입력해주세요.")
                continue

            valid_authors = []
            errors = []
            unresolved_authors = []

            for author in author_list:
                if "#" in author:  # 이름과 식별번호 형식
                    name, _, number = author.partition("#")
                    name = name.strip()
                    if not name or not number.isdigit():
                        errors.append(f"[{author}] ERROR: 입력 형식이 잘못되었습니다.")
                        continue

                    author_record = self.search_author_by_id(int(number))
                    if not author_record or author_record.name != name:
                        errors.append(f"[{author}] ERROR: 존재하지 않는 저자입니다.")
                    else:
                        valid_authors.append((name, int(number)))
                else:  # 이름만 입력된 경우
                    unresolved_authors.append(author)

            # 보조 프롬프트로 미해결 저자 처리
            for unresolved in unresolved_authors:
                matching_authors = [
                    author for author in self.author_table if author.name == unresolved
                ]
                if not matching_authors:
                    print(f"[{unresolved}] 해당 이름의 저자가 없습니다. 새로 추가합니다.")
                    new_author_id = len(self.author_table) + 1
                    self.author_table.append(AuthorRecord(new_author_id, unresolved, False))
                    valid_authors.append((unresolved, new_author_id))
                elif len(matching_authors) == 1:
                    valid_authors.append((unresolved, matching_authors[0].author_id))
                else:
                    print(f"저자 '{unresolved}'에 대한 후보가 여러 명 존재합니다.")
                    for idx, author in enumerate(matching_authors):
                        print(f"{idx + 1}. {author.name} #{author.author_id}")
                    try:
                        choice = int(input("해당 저자의 번호를 입력해주세요: ")) - 1
                        if 0 <= choice < len(matching_authors):
                            selected_author = matching_authors[choice]
                            valid_authors.append((selected_author.name, selected_author.author_id))
                        else:
                            errors.append(f"[{unresolved}] ERROR: 잘못된 선택입니다.")
                    except ValueError:
                        errors.append(f"[{unresolved}] ERROR: 입력값이 유효하지 않습니다.")

            if errors:
                print("\n".join(errors))
                print("모든 저자의 이름과 식별번호를 다시 입력해주세요.")
            else:
                break

        # 3. 출판사 입력
        while True:
            new_publisher = input("수정할 책의 출판사를 입력해주세요: ").strip()
            if not new_publisher or not self.check_string_validate("출판사", new_publisher):
                print("ERROR: 입력한 출판사가 유효하지 않습니다.")
                continue
            new_publisher_id = self.validate_publisher(new_publisher)
            if new_publisher_id is not None:
                break

        # 4. 출판년도 입력
        new_year = self.input_year("수정할 책의 출판년도를 입력해주세요: ")
        if not new_year or not self.check_year_validate(new_year):
            print("ERROR: 입력한 출판년도가 유효하지 않습니다.")
            return False

        # 수정 여부 확인
        if not self.input_response("수정한 데이터는 복구할 수 없습니다. 정말로 수정하시겠습니까?(Y/N): "):
            print("수정을 취소하였습니다. 메인 프롬프트로 돌아갑니다.")
            return False

        # 수정 반영
        for isbn_data in self.isbn_table:
            if isbn_data.isbn == isbn:
                isbn_data.title = new_title
                isbn_data.published_year = new_year
                break

       # 출판사 수정
        publisher_found = False
        for publisher in self.publisher_table:
            if publisher.name == new_publisher:  # 입력된 출판사가 이미 존재하면
                isbn_data.publisher_id = publisher.publisher_id  # 해당 출판사의 ID�� 반영
                publisher_found = True
                break

        if not publisher_found:  # 입력된 출판사가 존재하지 않으면
            new_publisher_id = len(self.publisher_table)
            self.publisher_table.append(PublisherRecord(new_publisher_id, new_publisher, False))  # 새 출판사 추가
            isbn_data.publisher_id = new_publisher_id  # 새 출판사의 ID를 반영

        # 저자 수정
        # 기존 저자-ISBN 관계 삭제
        self.isbn_author_table = [ia for ia in self.isbn_author_table if ia.isbn != isbn]
        # 새 저자-ISBN 관계 추가
        for name, number in valid_authors:
            self.isbn_author_table.append(IsbnAuthorRecord(isbn, number))

        print("수정이 완료되었습니다.")
        self.fetch_data_file()
        return True


    
    # ========== 4. 검색 ========== #
    def search_book(self):
        if not self.book_table:
            print("등록된 책이 존재하지 않습니다.")
            return False
        
        search_book = input("검색할 책의 제목 또는 저자를 입력하세요: ").strip()
        
        if search_book == self.config["cancel"]:
            print("검색을 중단하며 메인 프롬프트로 돌아갑니다.")
            return False
        
        if len(search_book) == 0:
            bookData.print_book_all()
            return True
        
        is_valid, error_message = self.check_string_validate("제목 또는 저자", search_book)
        if not is_valid:
            print(f"ERROR: {error_message}")
            return False
        
        bookData.search_content_book(search_book)
    
    def search_content_book(self, search_book):
        search_results = []
        
        for book in self.book_table:
            # find isbn
            isbn_data = None
            for isbn in self.isbn_table:
                if isbn.isbn == book.isbn:
                    isbn_data = isbn
                    break
                
            # find author isbn relationship
            author_isbn_data = None
            for isbn_author in self.isbn_author_table:
                if isbn_author.isbn == isbn_data.isbn:
                    author_isbn_data = isbn_author
                    break
                
            author_data = None
            for author in self.author_table:
                if author.author_id == author_isbn_data.author_id:
                    author_data = author
                    break
            
            if search_book in isbn_data.title or search_book in author_data.name:
                search_results.append(book)
            
        if not search_results:
        
            if self.input_response("해당 책이 존재하지 않습니다. 다시 검색하시겠습니까?(Y/N): "):
                self.search_book()
            else:
                print("검색을 중단하며 메인 프롬프트로 돌아갑니다.")
                return False
            
        print(DataManager.get_header())
        print()
        for book in search_results:
            print(self.print_book(book.book_id, include_borrow=True))
        print()
        return True
    
    # ========== 5. 대출 ========== #
    def borrow_book(self):
        name = self.input_borrower_name()
        if not name:
            return False
        
        if name == self.config["cancel"]:
            print("대출이 취소되었습니다. 메인 프롬프트로 돌아갑니다.")
            return False
        
        phone = self.input_phone_number()
        if not phone:
            return False
        
        if phone == self.config["cancel"]:
            print("대출이 취소되었습니다. 메인 프롬프트로 돌아갑니다.")
            return False
        
        borrower = self.search_user_by_phone_number(phone)
        if borrower is None:
            # 새로운 사용자 생성
            borrower_id = len(self.user_table)
            borrower = UserRecord(borrower_id, phone, name, False)
            self.user_table.append(borrower)
        else:
            borrower_id = borrower.user_id
        
        overdue_books = self.search_borrowing_book_ids_by_user_id(borrower_id, overdue_only=True)
        
        if overdue_books:
            print("연체중인 책을 1권 이상 보유하고 있어 대출이 불가능합니다.")
            #print("아래 목록은 대출자가 현재 연체중인 책입니다.")
            #print(self.get_header(contain_borrow_info=True))
            #print()
            #for book_id in overdue_books:
            #    print(self.print_book(book_id, include_borrow=True))
            return False
        
        # 연체 페널티 확인
        if self.search_overdue_penalty_by_user_id(borrower_id):
            penalty_end_date = max(
                penalty.penalty_end_date
                for penalty in self.overdue_penalty_table
                if penalty.user_id == borrower_id and penalty.penalty_start_date <= self.today
            )
            print(f"연체 페널티가 진행 중입니다. {penalty_end_date} 이후에 대출이 가능합니다.")
            return False
        
        borrowed_books = self.search_borrowing_book_ids_by_user_id(borrower_id, overdue_only=False)
        borrowed_count = len(borrowed_books)
        if borrowed_count >= self.config["max_borrow_count"]:
            print(f"대출 중인 책이 {borrowed_count}권 있으며 더 이상 대출이 불가능합니다.")
            print(BookRecord.get_header(contain_borrow_info=True))
            print()
            for book_id in borrowed_books:
                print(self.print_book(book_id, include_borrow=True))  
            return False
        else:
            print(f"대출중인 책이 {borrowed_count}권 있으며, {self.config['max_borrow_count'] - borrowed_count}권 대출이 가능합니다.")

        book_id = self.input_book_id("대출할 책의 고유번호를 입력해주세요: ", 1)
        
        if (book_id==None):
            return False
        
        if book_id == self.config["cancel"]:
            print("대출이 취소되었습니다. 메인 프롬프트로 돌아갑니다.")
            return False

        book_id = int(book_id)
        
        book = self.search_book_by_id(book_id)
        print("책이 특정되었습니다.")
        print(self.get_header(contain_borrow_info=False))
        print()
        print(self.print_book(book_id, include_borrow=False))
        
        if self.search_borrower_id_by_book_id(book_id):
            print("이미 다른 사용자에 의해 대출 중이므로 대출이 불가능합니다.")
            return False
        
        if self.input_response("위 책을 대출할까요? (Y/N): "):
            borrow_date = self.today
            due_date = self.today + self.config["borrow_date"]
            
            borrow = BorrowRecord(len(self.borrow_table), book_id, borrower_id, borrow_date, due_date, None, False)
            self.borrow_table.append(borrow)
            
            print(f"대출이 완료되었습니다. 반납 예정일은 {due_date} 입니다.")
            self.fetch_data_file()
            return True
        
        else:
            print("대출이 취소되었습니다. 메인 프롬프트로 돌아갑니다.")
            return False

    # ========== 6. 반납 ========== #
    def return_book(self):
        # try:
        rtn_book_id = self.input_book_id("반납할 책의 고유번호를 입력해주세요: ", 1)

        if (rtn_book_id==None):
            return False  # 입력 실패 시 반환

        if rtn_book_id == self.config["cancel"]:
            print("반납을 취소했습니다. 메인 프롬프트로 돌아갑니다.")
            return False
        
        rtn_book_id = int(rtn_book_id)
        
        # 고유번��에 해당하는 책 존재 여부 확인
        book_to_return = self.search_book_by_id(rtn_book_id)
        
        if not book_to_return:
            print("ERROR: 해당 고유번호의 책이 존재하지 않습니다.")
            return False
        
        # 대출 여부 확인
        borrow_info = None
        for borrow in self.borrow_table:
            if borrow.book_id == rtn_book_id and borrow.actual_return_date is None:
                borrow_info = borrow
                break

        if not borrow_info:
            print("ERROR: 현재 대출 중인 책이 아닙니다.")
            return False

        borrower_id = borrow_info.user_id
        rtn_user = self.search_user_by_id(borrower_id)

        if not rtn_user:
            print(f"ERROR: 대출자 ID {borrower_id}에 해당하는 사용자가 존재하지 않습니다.")
            return False
            
        # 책 정보 및 대출자 정보 출력
        rtn_isbn = self.search_isbn_data(book_to_return.isbn)
        author_ids = self.search_author_ids_by_isbn(rtn_isbn.isbn)
        
        # TODO: 임시로 저자 1명만 해두었습니다 수정 바람
        if len(author_ids) == 0:
            author_name = ""
        else:
            author_name = self.search_author_by_id(author_ids[0]).name
        
        rtn_publisher = self.search_publisher_by_id(rtn_isbn.publisher_id)
        print(f"{rtn_book_id} / {book_to_return.isbn} / {rtn_isbn.title} / {author_name} / {rtn_publisher.name} / {rtn_isbn.published_year} / {book_to_return.register_date}")
        
        borrower_id = self.search_borrower_id_by_book_id(rtn_book_id)
        rtn_user = self.search_user_by_id(borrower_id)
        borrow_info = self.search_borrow_by_user_id(rtn_book_id, borrower_id)
        print(f"대출자: {rtn_user.name} {rtn_user.phone_number} / 대출일: {borrow_info.borrow_date}")
        
        # 반납 여부 확인
        if not self.input_response("위 책을 반납할까요? (Y/N): "):
            print("반납을 취소했습니다. 메인 프롬프트로 돌아갑니다.")
            return False
        
        # 반납 처리
        borrow_info.actual_return_date = self.today
            
        # TODO: 연체 패널티 추가 
        overdue_days = 0
        if borrow_info.return_date is not None:
            overdue_days = (self.today - borrow_info.return_date)
            overdue_days = max(0, overdue_days)

        if overdue_days > 0:
            penalty_days = int(overdue_days * self.config['overdue_penalty_scale'])  # 연체일에 스케일 적용
            penalty_start_date = self.today
            penalty_end_date = self.today + penalty_days

            # 기존 페널티 확인 및 병합
            existing_penalty = None
            for penalty in self.overdue_penalty_table:
                if penalty.user_id == borrower_id and penalty.penalty_end_date >= self.today:
                    existing_penalty = penalty
                    break

            if existing_penalty:
                # 기존 페널티 종료일에 새로운 페널티 일수를 추가하여 연장
                existing_penalty.penalty_end_date = existing_penalty.penalty_end_date + penalty_days
                print(f"[페널티 연장] 기존 페널티 종료일이 {existing_penalty.penalty_end_date}로 연장되었습니다.")
            else:
                # 새로운 페널티 생성
                penalty_id = len(self.overdue_penalty_table)
                self.overdue_penalty_table.append(
                    OverduePenaltyRecord(
                        penalty_id, borrower_id, penalty_start_date, penalty_end_date
                    )
                )
                print(f"[새로운 페널티 부여] 페널티 시작: {penalty_start_date}, 종료: {penalty_end_date}")
        print("반납이 완료되었습니다. 메인 프롬프트로 돌아갑니다.")
        self.fetch_data_file()
        return True
            
        # except Exception as e:
        #     print(f"ERROR: 예상하지 못한 오류가 발생했습니다. {str(e)}")
        #     return False
            
    # ========== 7. 설정 ========== #
    def system_setting(self):
        while True:
            print("\n원하는 설정에 해당하는 번호를 입력하세요.")
            print("1. 반납 기한(대출 일수)")
            print("-------------")
            user_input = self.input_setting_option()

            if user_input == self.config["cancel"]:
                print("설정을 취소하였습니다. 메인 프롬프트로 돌아갑니다.")
                return

            if user_input == "1":
                self.change_return_period()
                return


    def change_return_period(self):
        while True:
            print(f"\n현재 반납 기한(대출 일수)은 {self.config['borrow_date']}일입니다.")
            new_period = self.input_return_period("변경할 반납 기한을 입력하세요 : ")

            if new_period == self.config["cancel"]:
                print("설정을 취소하였습니다. 메인 프롬프트로 돌아갑니다.")
                return

            if new_period is not None:
                self.confirm_return_period_change(new_period)
                return


    def confirm_return_period_change(self, new_period):
        message = f"\n반납 기한을 {new_period}일로 변경하겠습니까?(Y/N): "
        if self.input_response(message):
            self.config['borrow_date'] = new_period

            config_data = {
                "configuration": [
                    {"constant_name": k,
                     "value_type": "int" if isinstance(v, int) else "float" if isinstance(v, float) else "str",
                      "value": v}
                    for k, v in self.config.items()
                ]
            }
            with open(os.path.join(self.file_path, "Libsystem_Config.json"), "w") as f:
                json.dump(config_data, f, indent=4)

            print("변경이 완료되었습니다. 메인 프롬프트로 돌아갑니다.")
        else:
            print("변경을 취소하였습니다. 메인 프롬프트로 돌아갑니다.")
        
    
    # ========== 8. 연혁(로그) 조회 ========== #
    def history(self):
        history_book_id = self.input_book_id("연혁(조회)를 할 책의 고유번호를 입력해주세요: ", 1)

        if (history_book_id==None):
            return False  # 입력 실패 시 반환

        if history_book_id == self.config["cancel"]:
            print("연혁(조회)를 취소했습니다. 메인 프롬프트로 돌아갑니다.")
            return False
        
        history_book_id = int(history_book_id)
        
        # 고유번호에 해당하는 책 존재 여부 확인
        book_history = self.search_book_by_id(history_book_id)
        
        if not book_history:
            print("ERROR: 해당 고유번호의 책이 존재하지 않습니다.")
            return False
        
        history_isbn = self.search_isbn_data(book_history.isbn)
        author_ids = self.search_author_ids_by_isbn(history_isbn.isbn)
        
        # TODO: 임시로 저자 1명만 해두었습니다 수정 바람
        if len(author_ids) == 0:
            author_name = ""
        else:
            author_name = self.search_author_by_id(author_ids[0]).name
        
        history_publisher = self.search_publisher_by_id(history_isbn.publisher_id)
        print(f"{history_book_id} / {book_history.isbn} / {history_isbn.title} / {author_name} / {history_publisher.name} / {history_isbn.published_year} / {book_history.register_date}")

        log_list=[]
        log_list.append((history_isbn.isbn_register_date,1))
        log_list.append((book_history.register_date,2))
        if book_history.delete_date:
            log_list.append((book_history.delete_date,5))

        borrow_loglist=self.search_borrow_dates_by_book_id(history_book_id)
        for borrow_ll in borrow_loglist:
            log_list.append((borrow_ll[0],3,borrow_ll[1],borrow_ll[2])) # 대출날짜, 대출, user_id, 반납날짜

        return_loglist=self.search_return_dates_by_book_id(history_book_id)
        for return_ll in return_loglist:
            log_list.append((return_ll[0],4,return_ll[1]))  # 실제반납날짜, 반납, 연체날짜 

        for ll in log_list:
            print(ll[0], end=" ")
            if ll[1]==1 :
                print("ISBN 등록")

            elif ll[1]==2 :
                print("입고")

            elif ll[1]==3 :
                for user in self.user_table:
                    if user.user_id == ll[2]:
                        user_data = user
                        break
                print("대출:",user_data.phone_number,user_data.name,"/",ll[3])

            elif ll[1]==4 :
                print("반납",end=" ")
                if ll[2]>0:
                    print(f"({ll[2]}일 연체)",end="")
                print()

            elif ll[1]==5 :
                print("삭제")
                    
        print("메인 프롬프트로 돌아갑니다.")
    
    # ========= 기타 Utility 함수 ========= #
    # 데이터 개수 검사
    def is_full(self) -> bool:
        if self.static_id > self.config["max_static_id"]:
            return True
        else:
            return False
    
    # 다음에 할당할 고유번호 반환
    def get_static_id(self) -> int:
        return self.static_id
    
    # 고유번호 증가
    def increase_static_id(self) -> bool:
        if self.is_full():
            return False
        self.static_id += 1
        return True
    
    # ========== 현재 날짜가 데이터 파일에 올바른지 검사 ========== #
    def check_today_by_data(self, today: MyDate) -> tuple[bool, str]:
        return True, ""

    # ========== 데이터 입력받는 함수 ========== #
    def input_isbn(self, input_message: str) -> str:
        isbn = input(input_message).strip()
        is_valid, error_message = self.check_isbn_validate(isbn)
        if is_valid:
            return isbn
        else:
            print(f"ERROR: {error_message}")
            return None

    def input_bookName(self, input_message: str) -> str:
        title = input(input_message)

        if not title:  # 입력값이 비어있는 경우
            print("ERROR: 책의 제목은 1글자 이상이어야 합니다.")
            return None
        
        title = title.strip()

        if not title:  # 공백을 제거한 후 비어있는 경우
            print("ERROR: 책의 제목은 공백일 수 없습니다.")
            return None
        
        is_valid, error_message = self.check_string_validate("제목", title)
        if is_valid:
            return title
        else:
            print(f"ERROR: {error_message}")
            return None

    def input_author(self, input_message: str) -> list: # AuthorRecord or name
        author = input(input_message)
        is_valid, error_message = self.check_author_validate(author)
        if not is_valid:
            print(f"ERROR: {error_message}")
            return None
        
        author_list = [a.strip() for a in author.split("&") if a.strip()]
        return_authors = []
            
        for author in author_list:
            if "#" in author:
                name, number = author.split("#")
                name = name.strip()
                number = int(number.strip())
            else:
                name = author.strip()
                number = None

            if not number:
                author_data = self.search_author_by_name(author)
                if len(author_data) == 0:
                    return_authors.append(author)
                    continue

                print(f"이미 등록되어 있는 저자가 {len(author_data)}명이 있습니다.")

                for author in author_data:
                    print(author)

                while True:
                    input_number = input("식별번호 또는 0 (새 동명이인) 입력: ").strip()
                    if not input_number.isdigit():
                        if (len(author_data) == 1 and input_number == ""):
                            print(f"{author_data[0]}로 선택하였습니다.")
                            return_authors.append(author_data[0])
                            break
                        else:
                            print("잘못된 입력입니다. 다시 입력해주세요.")
                            continue
                    
                    if input_number == "0":
                        print("새 동명이인으로 선택하였습니다.")
                        return_authors.append(name)
                        break
                    else:
                        found = False
                        for author in author_data:
                            if author.author_id == int(input_number):
                                print(f"{author}로 선택하였습니다.")
                                return_authors.append(author)
                                found = True
                                break
                        if not found:
                            print("잘못된 입력입니다. 다시 입력해주세요.")
                            continue
            else:
                author_data = self.search_author_by_id(number)
                return_authors.append(author_data)
        return return_authors

    def input_publisher(self, input_message: str) -> str:
        publisher = input(input_message)

        if not publisher:  # 입력값이 비어있는 경우
            print("ERROR: 책의 출판사는 1글자 이상이어야 합니다.")
            return None
        
        publisher = publisher.strip()  # 앞뒤 공백 제거
        
        if not publisher:  # 공백을 제거한 후 비어있는 경우
            print("ERROR: 책의 출판사는 공백일 수 없습니다.")
            return None
        
        is_valid, error_message = self.check_string_validate("출판사", publisher)
        if is_valid:
            return publisher
        else:
            print(f"ERROR: {error_message}")
            return None

    def input_year(self, input_message: str) -> str:
        year = input(input_message).strip()
        is_valid, error_message = self.check_year_validate(year)
        if is_valid:
            return year
        else:
            print(f"ERROR: {error_message}")
            return None

    def input_book_id(self, input_message: str, flag: int) -> int: # flag == 0 -> 중복되면 False, flag == 1 -> 중복되어도 True
        book_id = input(input_message)
        
        if book_id.strip() == self.config["cancel"]:
            return self.config["cancel"]
    
        if not book_id:  # 입력값이 비어있는 경우
            print("ERROR: 책의 고유번호는 1글자 이상이어야 합니다.")
            return None
        
        book_id = book_id.strip()  # 앞뒤 공백 제거
    
        if not book_id:  # 공백을 제거한 후 비어있는 경우
            print("ERROR: 책의 고유번호는 공백일 수 없습니다.")
            return None

        is_valid, error_message = self.check_book_id_validate(book_id, flag)
        if is_valid:
            return int(book_id)
        else:
            print(f"ERROR: {error_message}")
            return None

    def input_response(self, input_message: str) -> bool:
        response = input(input_message) #.strip()
        if response == 'Y':
            return True
        return False
    
    def input_borrower_name(self) -> str:
        borrower_name = input("대출자 이름을 입력해주세요: ")

        if not borrower_name:  # 입력값이 비어있는 경우
            print("ERROR: 책의 대출자 이름은 1글자 이상이어야 합니다.")
            return None
        
        borrower_name = borrower_name.strip()  # 앞뒤 공백 제거
        
        if not borrower_name:  # 공백을 제거한 후 비어있는 경우
            print("ERROR: 책의 대출자 이름은 공백일 수 없습니다.")
            return None
        
        is_valid, error_message = self.check_string_validate("대출자 이름", borrower_name)
        if is_valid:
            return borrower_name
        else:
            print(f"ERROR: {error_message}")
            return None

    def input_phone_number(self) -> str:
        phone_number = input("대출자 전화번호를 입력해주세요: ").strip()
        is_valid, error_message = self.check_phone_number_validate(phone_number)
        if is_valid:
            return phone_number
        else:
            print(f"ERROR: {error_message}")
            return None

    def input_setting_option(self) -> str:
        setting_option = input().strip()
        if setting_option == self.config["cancel"]:
            return self.config["cancel"]

        if setting_option not in ["1"]:
            print("원하는 설정에 해당하는 번호(숫자)만 입력해주세요.")
            return None
            
        return setting_option


    def input_return_period(self, input_message: str) -> int:
        return_period = input(input_message).strip()
        if return_period == self.config["cancel"]:
            return self.config["cancel"]
        if not return_period.isdigit() or int(return_period) < 0:
            print("0 이상의 올바른 정수를 입력해주세요.")
            return None
        return int(return_period)



""" ========== main prompt ========== """
def main_prompt(bookData: DataManager) -> None:
    slc = 0
    
    main_prompt_text = """1. 추가
2. 삭제
3. 수정
4. 검색
5. 대출
6. 반납
7. 설정
8. 연혁(로그) 조회
9. 종료\n"""
    
    while slc != 9:
        print(main_prompt_text + "-"*20 + "\nLibsystem_Main > ", end="")
        
        try:
            slc = int(input())
            assert 0 < slc < 10, "원하는 동작에 해당하는 번호(숫자)만 입력해주세요."
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
            bookData.add_book()
            
        if slc == 2:
            bookData.delete_book()
            
        if slc == 3:
            bookData.update_book()
        
        if slc == 4:
            bookData.search_book()
            
        if slc == 5:
            bookData.borrow_book()
            
        if slc == 6:
            bookData.return_book()
    
        # 설정
        if slc == 7:
            bookData.system_setting()
            
        # 연혁(로그) 조회
        if slc == 8:
            bookData.history()
    

    print("프로그램을 종료합니다.")


""" ========== 현재 날짜 입력 ========== """
def input_date(bookData: DataManager):
    pattern = r'^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$'
    
    while True:
        date_str = input("현재 날짜를 YYYY-MM-DD 형식으로 입력해주세요: ")
    
        # 문법 검사
        if not re.match(pattern, date_str):
            print("잘못된 형식입니다. 아래 형식을 참고하여 다시 입력해주세요.\n[네 자리 숫자][-][두 자리 숫자][-][두 자리 숫자]", end="\n\n")
            continue
            
        try:
            year, month, day = map(int, date_str.split("-"))
        except:
            print("잘못된 형식입니다. 아래 형식을 참고하여 다시 입력해주세요.\n[네 자리 숫자][-][두 자리 숫자][-][두 자리 숫자]", end="\n\n")
            continue
            
        # 날짜 유효성 검사
        if not MyDate.validate_day(year, month, day):
            print("올바르지 않은 날짜입니다. 다시 입력해주세요.", end="\n\n")
            continue
        
        # 연도가 1583보다 작은지 검사
        if year < 1583:
            print("연도는 1583년 부터 가능합니다.", end="\n\n")
            continue
            
        today = MyDate(year, month, day)    
        
        # 데이터 무결성 검사
        is_validate, message = bookData.check_today_by_data(today)
        
        if is_validate:
            return today
        else:
            print(message, end="\n\n")


""" ========== Windows 기준 사용자의 Home 경로 가져오는 함수 ========== """
def get_user_home_path() -> str:
    home_path = os.path.expanduser("~")
    return home_path


""" ========== main ========== """
if __name__ == "__main__":
    # try:
    #     dir_path = get_user_home_path()
        
    #     if dir_path is None or len(dir_path) == 0:
    #         raise ValueError 
        
    # except Exception as e:
    #     # print(e)
    #     # print("[DEBUG] HOME 경로를 찾을 수 없어 현재 경로로 지정")
    #     dir_path = "./"
    
    # 임시로 이 레포지토리의 경로로 설정
    dir_path = "./"
    
    # print("[DEBUG] HOME 경로:", dir_path)
    # bookData = BookData(file_path=opj(dir_path, "Libsystem_data.txt"))
    bookData = DataManager(file_path=dir_path)
    
    # config 불러오기
    config = bookData.load_configuration()
    
    # 데이터 파일 읽기
    bookData.read_data_files()
    
    # 현재 날짜 입력
    today = input_date(bookData)
    bookData.set_today(today)

    # 디버깅용 함수 주석 처리
    print(DataManager.get_header())
    print(bookData.print_book(1, include_borrow=True))
    
    main_prompt(bookData=bookData)
