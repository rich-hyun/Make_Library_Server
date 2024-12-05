import os
from datetime import datetime
import re
import json
import shutil

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
        return f"{self.year}-{str(self.month).zfill(2)}-{str(self.day).zfill(2)}"

    @classmethod
    def from_str(self, text: str) -> object:
        try:
            year, month, day = map(int, text.split("-"))
            
            assert 1582 < year, "년도는 1582보다 큰 정수여야 합니다."
            assert 1 <= month <= 12, "월은 1과 12사이의 정수여야 합니다."
            assert self.validate_day(year, month, day), "년도와 월에 대해 일이 올바른 범위를 벗어났습니다."
            
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
        
    def __str__(self):
        return f"{self.book_id}/{str(self.isbn).zfill(2)}/{self.register_date}/{self.deleted}/{'' if self.delete_date is None else self.delete_date}"

# ISBN
class ISBNRecord(object):
    def __init__(self, isbn: int, title: str, publisher_id: int, published_year: int, isbn_register_date: MyDate):
        self.isbn = isbn
        self.title = title
        self.publisher_id = publisher_id
        self.published_year = published_year
        self.isbn_register_date = isbn_register_date
        
    def __str__(self):
        return f"{str(self.isbn).zfill(2)}/{self.title}/{self.publisher_id}/{self.published_year}/{self.isbn_register_date}"
        
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
        
    def __str__(self):
        return f"{str(self.isbn).zfill(2)}/{self.author_id}"
        
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
        
    def __str__(self):
        return f"{self.borrow_id}/{self.book_id}/{self.user_id}/{self.borrow_date}/{self.return_date}/{'' if self.actual_return_date is None else self.actual_return_date}/{self.deleted}"

# User
class UserRecord(object):
    def __init__(self, user_id: int, phone_number: str, name: str, deleted: bool=False):
        self.user_id = user_id
        self.phone_number = phone_number
        self.name = name
        self.deleted = deleted
        
    def __str__(self):
        return f"{self.user_id}/{self.phone_number}/{self.name}/{self.deleted}"
        
# Publisher
class PublisherRecord(object):
    def __init__(self, publisher_id: int, name: str, deleted: bool=False):
        self.publisher_id = publisher_id
        self.name = name
        self.deleted = deleted
        
    def __str__(self):
        return f"{self.publisher_id}/{self.name}/{self.deleted}"
    
# Overdue Penalty
class OverduePenaltyRecord(object):
    def __init__(self, penalty_id: int, user_id: int, penalty_start_date: MyDate, penalty_end_date: MyDate):
        self.penalty_id = penalty_id
        self.user_id = user_id
        self.penalty_start_date = penalty_start_date
        self.penalty_end_date = penalty_end_date
        
    def __str__(self):
        return f"{self.penalty_id}/{self.user_id}/{self.penalty_start_date}/{self.penalty_end_date}"
        
class LogRecord(object):
    def __init__(self, log_id: int, isbn: int, book_id: int, borrow_id: int, log_date: MyDate, log_type: str):
        self.log_id: int = log_id
        self.isbn: int = isbn
        self.book_id: int = book_id
        self.borrow_id: int = borrow_id
        self.log_date: MyDate = log_date
        self.log_type: str = log_type
        
    def __str__(self):
        return f"{self.log_id}/{str(self.isbn).zfill(2)}/{self.book_id}/{self.borrow_id}/{self.log_date}/{self.log_type}"

""" ========== 도서 관리 클래스 구현 ========== """
class DataManager(object):
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.book_table: list[BookRecord] = []
        self.isbn_table: list[ISBNRecord] = []
        self.author_table: list[AuthorRecord] = []
        self.isbn_author_table: list[IsbnAuthorRecord] = []
        self.borrow_table: list[BorrowRecord] = []
        self.user_table: list[UserRecord] = []
        self.publisher_table: list[PublisherRecord] = []
        self.overdue_penalty_table: list[OverduePenaltyRecord] = []
        self.log_table: list[LogRecord] = []
        self.today = None
        self.config = dict()
        self.static_id = 0  # default is 0

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
    def read_data_files(self, sep: str="/", verbose=True) -> tuple[bool, str]:

        if verbose: print("="*10, "Start Reading Data Files", "="*10)
        
        # 경로에 "data" 폴더가 없으면 생성
        data_folder_path = opj(self.file_path, "data")
        if not os.path.exists(data_folder_path):
            os.makedirs(data_folder_path)
        
        # ---------- 1. Publisher Data ----------
         # 파일이 존재하지 않으면 생성
        if not os.path.exists(opj(self.file_path, "data", "Libsystem_Data_Publisher.txt")):
            with open(opj(self.file_path, "data", "Libsystem_Data_Publisher.txt"), "w", encoding='utf-8') as f:
                pass
        
        # 무결성 검사(데이터가 올바르지 않을경우 파일명 변경(Libsystem_Data_{테이블명}-yyyyMMdd_hhmmss.bak) 후 새 Libsystem_Data_Publisher.txt 파일 생성)
        # yyyyMMdd-hhmmss는 컴퓨터 운영체제 시스템 시간을 기준으로 함
        passed, message = self.check_data_publisher_files(self.file_path)
        
        if not passed:
            # now = datetime.now().strftime("%Y%m%d_%H%M%S")
            # shutil.copy(opj(self.file_path, "data", "Libsystem_Data_Publisher.txt"), opj(self.file_path, "data", f"Libsystem_Data_Publisher-{now}.bak"))
            return (False, message)

        with open(opj(self.file_path, "data", "Libsystem_Data_Publisher.txt"), "r",encoding='utf-8') as f:
            for line in f:
                publisher_id, name, deleted = line.strip().split(sep)
                self.publisher_table.append(PublisherRecord(int(publisher_id), name, bool(int((deleted)))))

        if verbose: print(f"{len(self.publisher_table)} Publisher Data Loaded")
        
        # ---------- 2. ISBN Data ----------
        # 파일이 존재하지 않으면 생성(아무 데이터 없음)
        if not os.path.exists(opj(self.file_path, "data", "Libsystem_Data_Isbn.txt")):
            with open(opj(self.file_path, "data", "Libsystem_Data_Isbn.txt"), "w", encoding='utf-8') as f:
                pass
        
        # 무결성 검사(데이터가 올바르지 않을경우 파일명 변경(Libsystem_Data_{테이블명}-yyyyMMdd_hhmmss.bak) 후 새 Libsystem_Data_Isbn.txt 파일 생성)
        # yyyyMMdd-hhmmss는 컴퓨터 운영체제 시스템 시간을 기준으로 함
        passed, message = self.check_data_isbn_files(self.file_path)
        
        if not passed:
            # now = datetime.now().strftime("%Y%m%d_%H%M%S")
            # shutil.copy(opj(self.file_path, "data", "Libsystem_Data_Isbn.txt"), opj(self.file_path, "data", f"Libsystem_Data_Isbn-{now}.bak"))
            return (False, message)

        with open(opj(self.file_path, "data", "Libsystem_Data_Isbn.txt"), "r",encoding='utf-8') as f:
            for line in f:
                isbn, title, publisher_id, published_year, isbn_register_date = line.strip().split(sep)
                self.isbn_table.append(ISBNRecord(int(isbn), title, int(publisher_id), int(published_year), MyDate.from_str(isbn_register_date)))
                
        if verbose: print(f"{len(self.isbn_table)} ISBN Data Loaded")
        
        # ---------- 3. Book Data ----------
         # 파일이 존재하지 않으면 생성
        if not os.path.exists(opj(self.file_path, "data", "Libsystem_Data_Book.txt")):
            with open(opj(self.file_path, "data", "Libsystem_Data_Book.txt"), "w", encoding='utf-8') as f:
                f.write("0\n")

        # 파일이 비어있으면 생성
        file_path = opj(self.file_path, "data", "Libsystem_Data_Book.txt")
        with open(file_path, "r", encoding='utf-8') as rf:
            lines = rf.readlines()  # 파일의 모든 줄을 리스트로 읽어옵니다.
            if len(lines) == 0:
                # 파일이 비어있으면 기본 데이터를 작성
                with open(file_path, "w", encoding='utf-8') as wf:
                    wf.write("0\n")

        
        # 무결성 검사(데이터가 올바르지 않을경우 파일명 변경(Libsystem_Data_{테이블명}-yyyyMMdd_hhmmss.bak) 후 새 Libsystem_Data_Book.txt 파일 생성)
        # yyyyMMdd-hhmmss는 컴퓨터 운영체제 시스템 시간을 기준으로 함
        passed, message = self.check_data_book_files(self.file_path)
        
        if not passed:
            # now = datetime.now().strftime("%Y%m%d_%H%M%S")
            # shutil.copy(opj(self.file_path, "data", "Libsystem_Data_Book.txt"), opj(self.file_path, "data", f"Libsystem_Data_Book-{now}.bak"))
            return (False, message)

        with open(opj(self.file_path, "data", "Libsystem_Data_Book.txt"), "r",encoding='utf-8') as f:
            lines = f.readlines()
            
            self.static_id = int(lines[0])
            
            for line in lines[1:]:
                book_id, isbn, register_date, deleted, delete_date = line.strip().split(sep)
                self.book_table.append(BookRecord(int(book_id), int(isbn), MyDate.from_str(register_date), MyDate.from_str(delete_date), bool(int(deleted))))
          
        if verbose:      
            print(f"{len(self.book_table)} Book Data Loaded")
            print(f"max_book_id: {self.static_id}")
        
        # ---------- 5. Author Data ----------

        # 파일이 존재하지 않으면 생성(아무 데이터 없음)
        if not os.path.exists(opj(self.file_path, "data", "Libsystem_Data_Author.txt")):
            with open(opj(self.file_path, "data", "Libsystem_Data_Author.txt"), "w", encoding='utf-8') as f:
                 pass
            
        
         # 무결성 검사(데이터가 올바르지 않을경우 파일명 변경(Libsystem_Data_{테이블명}-yyyyMMdd_hhmmss.bak) 후 새 Libsystem_Data_Author.txt 파일 생성)
        # yyyyMMdd-hhmmss는 컴퓨터 운영체제 시스템 시간을 기준으로 함
        passed, message = self.check_data_author_files(self.file_path)
        
        if not passed:
            # now = datetime.now().strftime("%Y%m%d_%H%M%S")
            # shutil.copy(opj(self.file_path, "data", "Libsystem_Data_Author.txt"), opj(self.file_path, "data", f"Libsystem_Data_Author-{now}.bak"))
            return (False, message)
            
        with open(opj(self.file_path, "data", "Libsystem_Data_Author.txt"), "r",encoding='utf-8') as f:
            for line in f:
                author_id, name, deleted = line.strip().split(sep)
                self.author_table.append(AuthorRecord(int(author_id), name, bool(int(deleted))))
                
        if verbose: print(f"{len(self.author_table)} Author Data Loaded")
        
        # ---------- 6. ISBN - Author Data ----------
        # 파일이 존재하지 않으면 생성
        if not os.path.exists(opj(self.file_path, "data", "Libsystem_Data_IsbnAuthor.txt")):
            with open(opj(self.file_path, "data", "Libsystem_Data_IsbnAuthor.txt"), "w", encoding='utf-8') as f:
                 pass
            
        
        # 무결성 검사(데이터가 올바르지 않을경우 파일명 변경(Libsystem_Data_{테이블명}-yyyyMMdd_hhmmss.bak) 후 새 Libsystem_Data_IsbnAuthor.txt 파일 생성)
        # yyyyMMdd-hhmmss는 컴퓨터 운영체제 시스템 시간을 기준으로 함
        passed, message = self.check_data_isbn_author_files(self.file_path)
        
        if not passed:
            # now = datetime.now().strftime("%Y%m%d_%H%M%S")
            # shutil.copy(opj(self.file_path, "data", "Libsystem_Data_IsbnAuthor.txt"), opj(self.file_path, "data", f"Libsystem_Data_IsbnAuthor-{now}.bak"))
            return (False, message)

        with open(opj(self.file_path, "data", "Libsystem_Data_IsbnAuthor.txt"), "r",encoding='utf-8') as f:
            for line in f:
                isbn, author_id = line.strip().split(sep)
                self.isbn_author_table.append(IsbnAuthorRecord(int(isbn), int(author_id)))
                
        if verbose: print(f"{len(self.isbn_author_table)} ISBN - Author Data Loaded")

        # ---------- 7. User Data ----------
        # 파일이 존재하지 않으면 생성
        if not os.path.exists(opj(self.file_path, "data", "Libsystem_Data_User.txt")):
            with open(opj(self.file_path, "data", "Libsystem_Data_User.txt"), "w", encoding='utf-8') as f:
                pass
            
        
        # 무결성 검사(데이터가 올바르지 않을경우 파일명 변경(Libsystem_Data_{테이블명}-yyyyMMdd_hhmmss.bak) 후 새 Libsystem_Data_User.txt 파일 생성)
        # yyyyMMdd-hhmmss는 컴퓨터 운영체제 시스템 시간을 기준으로 함
        passed, message = self.check_data_user_files(self.file_path)
        
        if not passed:
            # now = datetime.now().strftime("%Y%m%d_%H%M%S")
            # shutil.copy(opj(self.file_path, "data", "Libsystem_Data_User.txt"), opj(self.file_path, "data", f"Libsystem_Data_User-{now}.bak"))
            return (False, message)

        with open(opj(self.file_path, "data", "Libsystem_Data_User.txt"), "r",encoding='utf-8') as f:
            for line in f:
                user_id, phone_number, name, deleted = line.strip().split(sep)
                self.user_table.append(UserRecord(int(user_id), phone_number, name, bool(int(deleted))))
        
        if verbose: print(f"{len(self.user_table)} User Data Loaded")
        
        # ---------- 8. Borrow Data ----------
        # 파일이 존재하지 않으면 생성
        if not os.path.exists(opj(self.file_path, "data", "Libsystem_Data_Borrow.txt")):
            with open(opj(self.file_path, "data", "Libsystem_Data_Borrow.txt"), "w", encoding='utf-8') as f:
                pass
            
        
        # 무결성 검사(데이터가 올바르지 않을경우 파일명 변경(Libsystem_Data_{테이블명}-yyyyMMdd_hhmmss.bak) 후 새 Libsystem_Data_Borrow.txt 파일 생성)
        # yyyyMMdd-hhmmss는 컴퓨터 운영체제 시스템 시간을 기준으로 함
        passed, message = self.check_data_borrow_files(self.file_path)
        
        if not passed:
            # now = datetime.now().strftime("%Y%m%d_%H%M%S")
            # shutil.copy(opj(self.file_path, "data", "Libsystem_Data_Borrow.txt"), opj(self.file_path, "data", f"Libsystem_Data_Borrow-{now}.bak"))
            return (False, message)

        with open(opj(self.file_path, "data", "Libsystem_Data_Borrow.txt"), "r",encoding='utf-8') as f:
            for line in f:
                borrow_id, book_id, user_id, borrow_date, return_date, actual_return_date, deleted = line.strip().split(sep)
                self.borrow_table.append(BorrowRecord(int(borrow_id), int(book_id), int(user_id), MyDate.from_str(borrow_date), MyDate.from_str(return_date), MyDate.from_str(actual_return_date), bool(int(deleted))))
                
        if verbose: print(f"{len(self.borrow_table)} Borrow Data Loaded") 
        
        # ---------- 9. Overdue Penalty Data ----------
        # 파일이 존재하지 않으면 생성
        if not os.path.exists(opj(self.file_path, "data", "Libsystem_Data_OverduePenalty.txt")):
            with open(opj(self.file_path, "data", "Libsystem_Data_OverduePenalty.txt"), "w", encoding='utf-8') as f:
                pass
            
        
        # 무결성 검사(데이터가 올바르지 않을경우 파일명 변경(Libsystem_Data_{테이블명}-yyyyMMdd_hhmmss.bak) 후 새 Libsystem_Data_OverduePenalty.txt 파일 생성)
        # yyyyMMdd-hhmmss는 컴퓨터 운영체제 시스템 시간을 기준으로 함
        passed, message = self.check_data_overdue_penalty_files(self.file_path)
        
        if not passed:
            # now = datetime.now().strftime("%Y%m%d_%H%M%S")
            # shutil.copy(opj(self.file_path, "data", "Libsystem_Data_OverduePenalty.txt"), opj(self.file_path, "data", f"Libsystem_Data_OverduePenalty-{now}.bak"))
            return (False, message)

        with open(opj(self.file_path, "data", "Libsystem_Data_OverduePenalty.txt"), "r",encoding='utf-8') as f:
            for line in f:
                penalty_id, user_id, penalty_start_date, penalty_end_date = line.strip().split(sep)
                self.overdue_penalty_table.append(OverduePenaltyRecord(int(penalty_id), int(user_id), MyDate.from_str(penalty_start_date), MyDate.from_str(penalty_end_date)))

        if verbose: print(f"{len(self.overdue_penalty_table)} Overdue Penalty Data Loaded")
        
        # ---------- 10. Log Data ----------
        # 파일이 존재하지 않으면 생성
        if not os.path.exists(opj(self.file_path, "data", "Libsystem_Data_Log.txt")):
            with open(opj(self.file_path, "data", "Libsystem_Data_Log.txt"), "w", encoding='utf-8') as f:
                pass
            
        # 무결성 검사(데이터가 올바르지 않을경우 파일명 변경(Libsystem_Data_{테이블명}-yyyyMMdd_hhmmss.bak) 후 새 Libsystem_Data_Log.txt 파일 생성)
        # yyyyMMdd-hhmmss는 컴퓨터 운영체제 시스템 시간을 기준으로 함
        passed, message = self.check_data_log_files(self.file_path)
        
        if not passed:
            # now = datetime.now().strftime("%Y%m%d_%H%M%S")
            # shutil.copy(opj(self.file_path, "data", "Libsystem_Data_Log.txt"), opj(self.file_path, "data", f"Libsystem_Data_Log-{now}.bak"))
            return (False, message)
        
        with open(opj(self.file_path, "data", "Libsystem_Data_Log.txt"), "r",encoding='utf-8') as f:
            for line in f:
                log_id, isbn, book_id, borrow_id, log_date, log_type = line.strip().split(sep)
                self.log_table.append(LogRecord(int(log_id), int(isbn), None if book_id == "" else int(book_id), None if borrow_id == "" else int(borrow_id), MyDate.from_str(log_date), log_type))
                
        if verbose: print(f"{len(self.log_table)} Log Data Loaded")
        if verbose: print("="*10, "End Reading Data Files", "="*10)
            
        return (True, "")

    # ========== 데이터 파일 메모리 -> 파일 동기화 (fetch) ========== #
    def fetch_data_file(self) -> bool:
        try:
            # 1. Book Data
            with open(opj(self.file_path, "data", "Libsystem_Data_Book.txt"), "w", encoding='utf-8') as f:
                f.write(f"{len(self.book_table)}\n")
                for book in self.book_table:
                    f.write(f"{book.book_id}/{str(book.isbn).zfill(2)}/{book.register_date}/{int(book.deleted)}/{'' if book.delete_date is None else book.delete_date}\n")

            # 2. ISBN Data
            with open(opj(self.file_path, "data", "Libsystem_Data_Isbn.txt"), "w", encoding='utf-8') as f:
                for isbn in self.isbn_table:
                    f.write(f"{str(isbn.isbn).zfill(2)}/{isbn.title}/{isbn.publisher_id}/{isbn.published_year}/{str(isbn.isbn_register_date)}\n")
                    
            # 3. Author Data
            with open(opj(self.file_path, "data", "Libsystem_Data_Author.txt"), "w", encoding='utf-8') as f:
                for author in self.author_table:
                    f.write(f"{author.author_id}/{author.name}/{int(author.deleted)}\n")
                    
            # 4. ISBN - Author Data
            with open(opj(self.file_path, "data", "Libsystem_Data_IsbnAuthor.txt"), "w", encoding='utf-8') as f:
                for isbn_author in self.isbn_author_table:
                    f.write(f"{str(isbn_author.isbn).zfill(2)}/{isbn_author.author_id}\n")
                    
            # 5. Book Edit Log Data
            # with open(opj(self.file_path, "data", "Libsystem_Data_BookEditLog.txt"), "w", encoding='utf-8') as f:
            #     for log in self.book_edit_log_table:
            #         f.write(f"{log.log_id}/{str(log.isbn).zfill(2)}/{str(log.edit_date)}\n")
            
            # 5. Log Data
            # with open(opj(self.file_path, "data", "Libsystem_Data_Log.txt"), "w", encoding='utf-8') as f:
            #     for log in self.log_table:
            #         f.write(f"{log.log_id}/{str(log.isbn).zfill(2)}/{"" if log.book_id is None else log.book_id}/{"" if log.borrow_id is None else log.borrow_id}/{str(log.log_date)}/{log.log_type}\n")
                    
            # 6. Borrow Data
            with open(opj(self.file_path, "data", "Libsystem_Data_Borrow.txt"), "w", encoding='utf-8') as f:
                for borrow in self.borrow_table:
                    f.write(f"{borrow.borrow_id}/{borrow.book_id}/{borrow.user_id}/{borrow.borrow_date}/{borrow.return_date}/{'' if borrow.actual_return_date is None else borrow.actual_return_date}/{int(borrow.deleted)}\n")

                    
            # 7. User Data
            with open(opj(self.file_path, "data", "Libsystem_Data_User.txt"), "w", encoding='utf-8') as f:
                for user in self.user_table:
                    f.write(f"{user.user_id}/{user.phone_number}/{user.name}/{int(user.deleted)}\n")
                    
            # 8. Publisher Data
            with open(opj(self.file_path, "data", "Libsystem_Data_Publisher.txt"), "w", encoding='utf-8') as f:
                for publisher in self.publisher_table:
                    f.write(f"{publisher.publisher_id}/{publisher.name}/{int(publisher.deleted)}\n")
                    
            # 9. Overdue Penalty Data
            with open(opj(self.file_path, "data", "Libsystem_Data_OverduePenalty.txt"), "w", encoding='utf-8') as f:
                for penalty in self.overdue_penalty_table:
                    f.write(f"{penalty.penalty_id}/{penalty.user_id}/{str(penalty.penalty_start_date)}/{str(penalty.penalty_end_date)}\n")
                    
            return True
        
        except Exception as e:
            print("ERROR: 데이터 파일 저장에 실패했습니다.")
            return False
    
    # ========== 데이터 파일 무결성 검사 ========== #
    # 오류 발생 시 오류 발생한 줄과 오류 메세지 출력
    def check_data_book_files(self,file_path: str) -> tuple[bool, str]:
        # 오류 발생한 줄과 오류 메세지 파일의 마지막 줄에 추가
        line_num = 1
        def add_error(line_num, error_message):
            now = datetime.now().strftime("%Y%m%d_%H%M%S")
            shutil.copy(opj(self.file_path, "data", "Libsystem_Data_Book.txt"), opj(self.file_path, "data", f"Libsystem_Data_Book-{now}.bak"))
            with open(opj(file_path, "data", f"Libsystem_Data_Book-{now}.bak"), "a", encoding='utf-8') as f:
                f.write(f"데이터 파일 무결성 검사에 실패했습니다. 오류 발생 위치 : {line_num}번째 줄 - {error_message}\n")

        with open(opj(file_path, "data", "Libsystem_Data_Book.txt"), "r", encoding='utf-8') as f:
            lines = f.readlines()
        first_line = lines[0].strip()
        
        # 첫 줄이 숫자인지 확인
        if not first_line.isdigit() or int(first_line) > 99:
            add_error(line_num, "첫 줄이 0에서 99 사이의 정수가 아닙니다.")
            return (False, f"데이터 파일 무결성 검사에 실패했습니다. 오류 발생 위치 : {line_num}번째 줄 - 첫 줄이 0에서 99 사이의 정수가 아닙니다.")
        

        first_line = int(first_line)
        
        # 구분자가 4개인지 확인
        for line in lines[1:]:
            line_num += 1
            line = line.strip()
            if line_num == 2 and line == "":
                return (True, "")
            if len(line.strip().split("/")) != 5:
                add_error(line_num, "구분자가 4개가 아닙니다")
                return (False, f"데이터 파일 무결성 검사에 실패했습니다. 오류 발생 위치 : {line_num}번째 줄 - 구분자가 4개가 아닙니다")
            
        line_num = 1
            
        # 모든 레코드의 앞 4개 항목 비어있지 않는 지 확인
        for line in lines[1:]:
            line_num += 1
            book_id, isbn, register_date, deleted, delete_date = line.strip().split("/")
            if book_id == "" or isbn == "" or register_date == "" or deleted == "":
                add_error(line_num, "모든 레코드의 앞 4개 항목이 비어있습니다.")
                return (False, f"데이터 파일 무결성 검사에 실패했습니다. 오류 발생 위치 : {line_num}번째 줄 - 모든 레코드의 앞 4개 항목이 비어있습니다.")
        
        line_num = 1
            
        # 고유번호 검사
        for line in lines[1:]:
            line_num += 1
            book_id, isbn, register_date, deleted, delete_date = line.strip().split("/")
            # 고유번호가 숫자인지 확인
            if not book_id.isdigit() or int(book_id) >= first_line:
                add_error(line_num, "고유번호가 0에서 첫 줄의 값 사이의 정수가 아닙니다.")
                return (False, f"데이터 파일 무결성 검사에 실패했습니다. 오류 발생 위치 : {line_num}번째 줄 - 고유번호가 0에서 첫 줄의 값 사이의 정수가 아닙니다.")
            
            # 고유번호 중복 검사
            book_ids = [line.strip().split("/")[0] for line in lines]
            if book_ids.count(book_id) > 1:
                add_error(line_num, "고유번호가 중복됩니다.")
                return (False, f"데이터 파일 무결성 검사에 실패했습니다. 오류 발생 위치 : {line_num}번째 줄 - 고유번호가 중복됩니다.")
            
            # 고유번호는 0부터 1씩 증가해야 함
            if int(book_id) != line_num - 2:
                add_error(line_num, "책 고유번호는 0부터 1씩 증가해야 합니다.")
                return (False, f"데이터 파일 무결성 검사에 실패했습니다. 오류 발생 위치 : {line_num}번째 줄 - 책 고유번호는 0부터 1씩 증가해야 합니다.")
            
            # ISBN 검사(길이가 2이며, 정수로 변환 가능한지)
            if len(isbn) != 2 or not isbn.isdigit():
                add_error(line_num, "ISBN이 2자리 숫자가 아닙니다.")
                return (False, f"데이터 파일 무결성 검사에 실패했습니다. 오류 발생 위치 : {line_num}번째 줄 - ISBN이 2자리 숫자가 아닙니다.")
            
            # 등록 날짜 검사
            if not MyDate.from_str(register_date):
                add_error(line_num, "등록 날짜가 날짜 형식이 아닙니다.")
                return (False, f"데이터 파일 무결성 검사에 실패했습니다. 오류 발생 위치 : {line_num}번째 줄 - 등록 날짜가 날짜 형식이 아닙니다.")
            
            # 삭제 여부 검사
            if deleted not in ["0", "1"]:
                add_error(line_num, "삭제 여부가 0 또는 1이 아닙니다.")
                return (False, f"데이터 파일 무결성 검사에 실패했습니다. 오류 발생 위치 : {line_num}번째 줄 - 삭제 여부가 0 또는 1이 아닙니다.")
            
            # 삭제 날짜 검사(날짜 검사 및 삭제 여부가 1일 때만 검사)
            if deleted == "1" and not MyDate.from_str(delete_date):
                add_error(line_num, "삭제 날짜가 날짜 형식이 아닙니다.")
                return (False, f"데이터 파일 무결성 검사에 실패했습니다. 오류 발생 위치 : {line_num}번째 줄 - 삭제 날짜가 날짜 형식이 아닙니다.")
            
            if deleted == "1" and MyDate.from_str(delete_date) < MyDate.from_str(register_date):
                add_error(line_num, "삭제 날짜가 등록 날짜보다 이전입니다.")
                return (False, f"데이터 파일 무결성 검사에 실패했습니다. 오류 발생 위치 : {line_num}번째 줄 - 삭제 날짜가 등록 날짜보다 이전입니다.")
            
            # ISBN 참조 무결성 검사
            isbn_found = False
            for isbn_record in self.isbn_table:
                if isbn_record.isbn == int(isbn):
                    isbn_found = True
                    break
                
            if not isbn_found:
                add_error(line_num, "참조하는 ISBN이 ISBN 데이터에 없습니다.")
                return (False, f"데이터 파일 무결성 검사에 실패했습니다. 오류 발생 위치 : {line_num}번째 줄 - 참조하는 ISBN이 ISBN 데이터에 없습니다.")
            
        return (True, "")
    
    def check_data_isbn_files(self,file_path: str) -> tuple[bool, str]:
        # 오류 발생한 줄과 오류 메세지 파일의 마지막 줄에 추가
        def add_error(line_num, error_message):
            now = datetime.now().strftime("%Y%m%d_%H%M%S")
            shutil.copy(opj(self.file_path, "data", "Libsystem_Data_Isbn.txt"), opj(self.file_path, "data", f"Libsystem_Data_Isbn-{now}.bak"))
            with open(opj(file_path, "data", f"Libsystem_Data_Isbn-{now}.bak"), "a", encoding='utf-8') as f:
                f.write(f"데이터 파일 무결성 검사에 실패했습니다. 오류 발생 위치 : {line_num}번째 줄 - {error_message}\n")

        with open(opj(file_path, "data", "Libsystem_Data_Isbn.txt"), "r", encoding='utf-8') as f:
            lines = f.readlines()
            
        line_num = 0
        
        # 구분자가 4개인지 확인
        for line in lines:
            line_num += 1
            line = line.strip()
            if line_num ==1 and line == "":
                return (True, "")
            
            if len(line.strip().split("/")) != 5:
                add_error(line_num, "구분자가 4개가 아닙니다")
                return (False, f"데이터 파일 무결성 검사에 실패했습니다. 오류 발생 위치 : {line_num}번째 줄 - 구분자가 4개가 아닙니다")
            
        line_num = 0
            
        # 모든 레코드의 앞 5개 항목 비어있지 않는 지 확인
        for line in lines:
            line_num += 1
            isbn, title, publisher_id, published_year, isbn_register_date = line.strip().split("/")
            if isbn == "" or title == "" or publisher_id == "" or published_year == "" or isbn_register_date == "":
                add_error(line_num, "모든 레코드의 앞 5개 항목이 비어있습니다.")
                return (False, f"데이터 파일 무결성 검사에 실패했습니다. 오류 발생 위치 : {line_num}번째 줄 - 모든 레코드의 앞 5개 항목이 비어있습니다.")
        
        line_num = 0
            
        # ISBN 검사
        for line in lines:
            line_num += 1
            isbn, title, publisher_id, published_year, isbn_register_date = line.strip().split("/")
            # ISBN이 숫자인지 확인
            if not isbn.isdigit() or int(isbn) > 99:
                add_error(line_num, "ISBN이 0에서 99 사이의 정수가 아닙니다.")
                return (False, f"데이터 파일 무결성 검사에 실패했습니다. 오류 발생 위치 : {line_num}번째 줄 - ISBN이 0에서 99 사이의 정수가 아닙니다.")
            
            # ISBN 중복 검사
            isbns = [line.strip().split("/")[0] for line in lines]
            if isbns.count(isbn) > 1:
                add_error(line_num, "ISBN이 중복됩니다.")
                return (False, f"데이터 파일 무결성 검사에 실패했습니다. 오류 발생 위치 : {line_num}번째 줄 - ISBN이 중복됩니다.")
            
            # 출판사 ID 검사
            if not publisher_id.isdigit():
                add_error(line_num, "출판사 ID가 0 이상의 숫자가 아닙니다.")
                return (False, f"데이터 파일 무결성 검사에 실패했습니다. 오류 발생 위치 : {line_num}번째 줄 - 출판사 ID가 0 이상의 숫자가 아닙니다.")
            
            # 책 제목에 '/'나 '\'가 포함되어 있는지 확인
            if "/" in title or "\\" in title:
                add_error(line_num, "책 제목에 '/'나 '\\'가 포함되어 있습니다.")
                return (False, f"데이터 파일 무결성 검사에 실패했습니다. 오류 발생 위치 : {line_num}번째 줄 - 책 제목에 '/'나 '\\'가 포함되어 있습니다.")
            
            # 출판년도 검사
            if not published_year.isdigit():
                add_error(line_num, "출판년도가 숫자가 아닙니다.")
                return (False, f"데이터 파일 무결성 검사에 실패했습니다. 오류 발생 위치 : {line_num}번째 줄 - 출판년도가 숫자가 아닙니다.")
            
            # 출판년도가 1583에서 9999 사이의 정수인지 확인
            if int(published_year) < 1583 or int(published_year) > 9999:
                add_error(line_num, "출판년도가 1583에서 9999 사이의 정수가 아닙니다.")
                return (False, f"데이터 파일 무결성 검사에 실패했습니다. 오류 발생 위치 : {line_num}번째 줄 - 출판년도가 1583에서 9999 사이의 정수가 아닙니다.")
            
            # ISBN 등록 날짜 검사
            if not MyDate.from_str(isbn_register_date):
                add_error(line_num, "ISBN 등록 날짜가 날짜 형식이 아닙니다.")
                return (False, f"데이터 파일 무결성 검사에 실패했습니다. 오류 발생 위치 : {line_num}번째 줄 - ISBN 등록 날짜가 날짜 형식이 아닙니다.")
            
            # 등록날짜의 년도가 출판년도보다 크거나 같아야 함
            if MyDate.from_str(isbn_register_date).year < int(published_year):
                add_error(line_num, "ISBN 등록 날짜의 년도가 출판년도보다 작습니다.")
                return (False, f"데이터 파일 무결성 검사에 실패했습니다. 오류 발생 위치 : {line_num}번째 줄 - ISBN 등록 날짜의 년도가 출판년도보다 작습니다.")
            
            # 참조 검사: Publisher ID가 출판사 테이블에 있는지 확인
            publisher_found = False
            for publisher in self.publisher_table:
                if publisher.publisher_id == int(publisher_id):
                    publisher_found = True
                    break
                
            if not publisher_found:
                add_error(line_num, "참조하는 출판사 고유번호가 출판사 데이터에 없습니다.")
                return (False, f"데이터 파일 무결성 검사에 실패했습니다. 오류 발생 위치 : {line_num}번째 줄 - 참조하는 출판사 고유번호가 출판사 데이터에 없습니다.")
            
        return (True, "")

    def check_data_author_files(self,file_path: str) -> tuple[bool, str]:
        # 오류 발생한 줄과 오류 메세지 파일의 마지막 줄에 추가
        def add_error(line_num, error_message):
            now = datetime.now().strftime("%Y%m%d_%H%M%S")
            shutil.copy(opj(self.file_path, "data", "Libsystem_Data_Author.txt"), opj(self.file_path, "data", f"Libsystem_Data_Author-{now}.bak"))
            with open(opj(file_path, "data", f"Libsystem_Data_Author-{now}.bak"), "a",encoding='utf-8') as f:
                f.write(f"데이터 파일 무결성 검사에 실패했습니다. 오류 발생 위치 : {line_num}번째 줄 - {error_message}\n")

        with open(opj(file_path, "data", "Libsystem_Data_Author.txt"), "r", encoding='utf-8') as f:
            lines = f.readlines()
            
        line_num = 0
        
        # 구분자가 2개인지 확인
        for line in lines:
            line_num += 1
            line = line.strip()
            if line_num ==1 and line == "":
                return (True, "")
            if len(line.strip().split("/")) != 3:
                add_error(line_num, "구분자가 2개가 아닙니다.")
                return (False, f"데이터 파일 무결성 검사에 실패했습니다. 오류 발생 위치 : {line_num}번째 줄 - 구분자가 2개가 아닙니다.")
            
        line_num = 0

        # 모든 레코드의 앞 3개 항목 비어있지 않는 지 확인
        for line in lines:
            line_num += 1
            author_id, name, deleted = line.strip().split("/")
            if author_id == "" or name == "" or deleted == "":
                add_error(line_num, "필수항목 중 비어있는 항목이 있습니다.")
                return (False, f"데이터 파일 무결성 검사에 실패했습니다. 오류 발생 위치 : {line_num}번째 줄 - 필수항목 중 비어있는 항목이 있습니다.")
            
        line_num = 0

        # 저자 ID 검사
        for line in lines:
            line_num += 1
            author_id, name, deleted = line.strip().split("/")
            # 저자 ID가 숫자인지 확인
            if not author_id.isdigit() or author_id == "0":
                add_error(line_num, "저자 ID가 1 이상의 숫자가 아닙니다.")
                return (False, f"데이터 파일 무결성 검사에 실패했습니다. 오류 발생 위치 : {line_num}번째 줄 - 저자 ID가 1 이상의 숫자가 아닙니다.")
            
            # 저자 ID 중복 검사
            author_ids = [line.strip().split("/")[0] for line in lines]
            if author_ids.count(author_id) > 1:
                add_error(line_num, "저자 ID가 중복됩니다.")
                return (False, f"데이터 파일 무결성 검사에 실패했습니다. 오류 발생 위치 : {line_num}번째 줄 - 저자 ID가 중복됩니다.")
            
            # 저자 식별번호는 1부터 1씩 증가해야 함
            if int(author_id) != line_num:
                add_error(line_num, "저자 식별번호는 1부터 1씩 증가해야 합니다.")
                return (False, f"데이터 파일 무결성 검사에 실패했습니다. 오류 발생 위치 : {line_num}번째 줄 - 저자 식별번호는 1부터 1씩 증가해야 합니다.")
            
            # 저자 이름에 '/'나 '\'가 포함되어 있는지 확인
            if "/" in name or "\\" in name:
                add_error(line_num, "저자 이름에 '/'나 '\\'가 포함되어 있습니다.")
                return (False, f"데이터 파일 무결성 검사에 실패했습니다. 오류 발생 위치 : {line_num}번째 줄 - 저자 이름에 '/'나 '\\'가 포함되어 있습니다.")
            
            # 삭제 여부 검사
            if deleted not in ["0", "1"]:
                add_error(line_num, "삭제 여부가 0 또는 1이 아닙니다.")
                return (False, f"데이터 파일 무결성 검사에 실패했습니다. 오류 발생 위치 : {line_num}번째 줄 - 삭제 여부가 0 또는 1이 아닙니다.")
            
        return (True, "")


    def check_data_isbn_author_files(self,file_path: str) -> tuple[bool, str]:
        # 오류 발생한 줄과 오류 메세지 파일의 마지막 줄에 추가
        def add_error(line_num, error_message):
            now = datetime.now().strftime("%Y%m%d_%H%M%S")
            shutil.copy(opj(self.file_path, "data", "Libsystem_Data_IsbnAuthor.txt"), opj(self.file_path, "data", f"Libsystem_Data_IsbnAuthor-{now}.bak"))
            with open(opj(file_path, "data", f"Libsystem_Data_IsbnAuthor-{now}.bak"), "a", encoding='utf-8') as f:
                f.write(f"데이터 파일 무결성 검사에 실패했습니다. 오류 발생 위치 : {line_num}번째 줄 - {error_message}\n")

        with open(opj(file_path, "data", "Libsystem_Data_IsbnAuthor.txt"), "r", encoding='utf-8') as f:
            lines = f.readlines()
            
        line_num = 0
        
        # 구분자가 1개인지 확인
        for line in lines:
            line_num += 1
            line = line.strip()
            if line_num ==1 and line == "":
                return (True, "")
            
            if len(line.strip().split("/")) != 2:
                add_error(line_num, "구분자가 1개가 아닙니다")
                return (False, f"데이터 파일 무결성 검사에 실패했습니다. 오류 발생 위치 : {line_num}번째 줄 - 구분자가 1개가 아닙니다")
            
        line_num = 0

        # 모든 레코드의 앞 2개 항목 비어있지 않는 지 확인
        for line in lines:
            line_num += 1
            isbn, author_id = line.strip().split("/")
            if isbn == "" or author_id == "":
                add_error(line_num, "필수항목 중 비어있는 항목이 있습니다.")
                return (False, f"데이터 파일 무결성 검사에 실패했습니다. 오류 발생 위치 : {line_num}번째 줄 - 필수항목 중 비어있는 항목이 있습니다.")
            
        line_num = 0

        # ISBN 검사
        for line in lines:
            line_num += 1
            isbn, author_id = line.strip().split("/")
            # ISBN이 숫자인지 확인
            if not isbn.isdigit() or int(isbn) > 99:
                add_error(line_num, "ISBN이 0에서 99 사이의 숫자가 아닙니다.")
                return (False, f"데이터 파일 무결성 검사에 실패했습니다. 오류 발생 위치 : {line_num}번째 줄 - ISBN이 0에서 99 사이의 숫자가 아닙니다.")
            
            # 저자 ID 검사
            if not author_id.isdigit() or int(author_id) < 1:
                add_error(line_num, "저자 ID가 1 이상의 숫자가 아닙니다.")
                return (False, f"데이터 파일 무결성 검사에 실패했습니다. 오류 발생 위치 : {line_num}번째 줄 - 저자 ID가 1 이상의 숫자가 아닙니다.")
            
            # ISBN-저자 ID 중복 검사
            isbn_author_ids = [line.strip().split("/") for line in lines]
            if isbn_author_ids.count([isbn, author_id]) > 1:
                add_error(line_num, "중복된 ISBN-저자 관계가 발견되었습니다.")
                return (False, f"데이터 파일 무결성 검사에 실패했습니다. 오류 발생 위치 : {line_num}번째 줄 - 중복된 ISBN-저자 관계가 발견되었습니다.")
            
            
            # ISBN 참조 무결성 검사
            isbn_found = False
            for isbn_record in self.isbn_table:
                if isbn_record.isbn == int(line.strip().split("/")[0]):
                    isbn_found = True
                    break
                
            if not isbn_found:
                add_error(line_num, "참조하는 ISBN이 ISBN 데이터에 없습니다.")
                return (False, f"데이터 파일 무결성 검사에 실패했습니다. 오류 발생 위치 : {line_num}번째 줄 - 참조하는 ISBN이 ISBN 데이터에 없습니다.")
            
            # 저자 ID 참조 무결성 검사
            author_id_found = False
            for author_record in self.author_table:
                if author_record.author_id == int(line.strip().split("/")[1]):
                    author_id_found = True
                    break
            
            if not author_id_found:
                add_error(line_num, "참조하는 저자 식별번호가 저자 데이터에 없습니다.")
                return (False, f"데이터 파일 무결성 검사에 실패했습니다. 오류 발생 위치 : {line_num}번째 줄 - 참조하는 저자 식별번호가 저자 데이터에 없습니다.")
        
        
        return (True, "")

    def check_data_borrow_files(self,file_path: str) -> tuple[bool, str]:
        # 오류 발생한 줄과 오류 메세지 파일의 마지막 줄에 추가
        def add_error(line_num, error_message):
            now = datetime.now().strftime("%Y%m%d_%H%M%S")
            shutil.copy(opj(self.file_path, "data", "Libsystem_Data_Borrow.txt"), opj(self.file_path, "data", f"Libsystem_Data_Borrow-{now}.bak"))
            with open(opj(file_path, "data", f"Libsystem_Data_Borrow-{now}.bak"), "a", encoding='utf-8') as f:
                f.write(f"데이터 파일 무결성 검사에 실패했습니다. 오류 발생 위치 : {line_num}번째 줄 - {error_message}\n")

        with open(opj(file_path, "data", "Libsystem_Data_Borrow.txt"), "r", encoding='utf-8') as f:
            lines = f.readlines()
            
        line_num = 0
        
        # 구분자가 6개인지 확인
        for line in lines:
            line_num += 1
            line = line.strip()
            if line_num ==1 and line == "":
                return (True, "")
            if len(line.strip().split("/")) != 7:
                add_error(line_num, "구분자가 6개가 아닙니다")
                return (False, f"데이터 파일 무결성 검사에 실패했습니다. 오류 발생 위치 : {line_num}번째 줄 - 구분자가 6개가 아닙니다")
            
            # book_id 참조 무결성 검사
            book_id_found = False
            for book_record in self.book_table:
                if book_record.book_id == int(line.strip().split("/")[1]):
                    book_id_found = True
                    break
                
            if not book_id_found:
                add_error(line_num, "참조하는 책 고유번호가 책 데이터에 없습니다.")
                return (False, f"데이터 파일 무결성 검사에 실패했습니다. 오류 발생 위치 : {line_num}번째 줄 - 참조하는 책 고유번호가 책 데이터에 없습니다.")
            
            # user_id 참조 무결성 검사
            user_id_found = False
            for user_record in self.user_table:
                if user_record.user_id == int(line.strip().split("/")[2]):
                    user_id_found = True
                    break
                
            if not user_id_found:
                add_error(line_num, "참조하는 사용자 고유번호가 사용자 데이터에 없습니다.")
                return (False, f"데이터 파일 무결성 검사에 실패했습니다. 오류 발생 위치 : {line_num}번째 줄 - 참조하는 사용자 고유번호가 사용자 데이터에 없습니다.")
            
        line_num = 0

        # 모든 레코드의 앞 6개 항목 비어있지 않는 지 확인
        for line in lines:
            line_num += 1
            borrow_id,book_id, user_id, borrow_date, return_date, actual_return_date, deleted = line.strip().split("/")
            if borrow_id=="" or book_id == "" or user_id == "" or borrow_date == "" or return_date == "" or deleted == "":
                add_error(line_num, "필수항목 중 비어있는 항목이 있습니다.")
                return (False, f"데이터 파일 무결성 검사에 실패했습니다. 오류 발생 위치 : {line_num}번째 줄 - 필수항목 중 비어있는 항목이 있습니다.")
            
        line_num = 0

        for line in lines:
            line_num += 1
            borrow_id,book_id, user_id, borrow_date, return_date, actual_return_date, deleted = line.strip().split("/")
            # 대출 ID가 숫자인지 확인
            if not borrow_id.isdigit():
                add_error(line_num, "대출 ID가 0 이상의 숫자가 아닙니다.")
                return (False, f"데이터 파일 무결성 검사에 실패했습니다. 오류 발생 위치 : {line_num}번째 줄 - 대출 ID가 0 이상의 숫자가 아닙니다.")
            
            # 대출 ID 중복 검사
            borrow_ids = [line.strip().split("/")[0] for line in lines]
            if borrow_ids.count(borrow_id) > 1:
                add_error(line_num, "대출 ID가 중복됩니다.")
                return (False, f"데이터 파일 무결성 검사에 실패했습니다. 오류 발생 위치 : {line_num}번째 줄 - 대출 ID가 중복됩니다.")
             
            # 고유번호는 0부터 1씩 증가해야 함
            if int(borrow_id) != line_num - 1:
                add_error(line_num, "대출 고유번호는 0부터 1씩 증가해야 합니다.")
                return (False, f"데이터 파일 무결성 검사에 실패했습니다. 오류 발생 위치 : {line_num}번째 줄 - 대출 고유번호는 0부터 1씩 증가해야 합니다.")
             
            # 책 ID가 숫자인지 확인
            if not book_id.isdigit():
                add_error(line_num, "책 ID가 0 이상의 숫자가 아닙니다.")
                return (False, f"데이터 파일 무결성 검사에 실패했습니다. 오류 발생 위치 : {line_num}번째 줄 - 책 ID가 0 이상의 숫자가 아닙니다.")
            
            # 책 ID 중복 검사
            book_ids = [line.strip().split("/")[1] for line in lines]
            if book_ids.count(book_id) > 1:
                add_error(line_num, "책 ID가 중복됩니다.")
                return (False, f"데이터 파일 무결성 검사에 실패했습니다. 오류 발생 위치 : {line_num}번째 줄 - 책 ID가 중복됩니다.")
            
            # 사용자 ID 검사
            if not user_id.isdigit():
                add_error(line_num, "사용자 ID가 0 이상의 숫자가 아닙니다.")
                return (False, f"데이터 파일 무결성 검사에 실패했습니다. 오류 발생 위치 : {line_num}번째 줄 - 사용자 ID가 0 이상의 숫자가 아닙니다.")
            
            # 대출 날짜 검사
            if not MyDate.from_str(borrow_date):
                add_error(line_num, "대출 날짜가 날짜 형식이 아닙니다.")
                return (False, f"데이터 파일 무결성 검사에 실패했습니다. 오류 발생 위치 : {line_num}번째 줄 - 대출 날짜가 날짜 형식이 아닙니다.")
            
            # 반납 날짜 검사
            if not MyDate.from_str(return_date):
                add_error(line_num, "반납 날짜가 날짜 형식이 아닙니다.")
                return (False, f"데이터 파일 무결성 검사에 실패했습니다. 오류 발생 위치 : {line_num}번째 줄 - 반납 날짜가 날짜 형식이 아닙니다.")
            
            # 실제 반납 날짜 검사(실제 반납 존재 시)
            if actual_return_date != "" and not MyDate.from_str(actual_return_date):
                add_error(line_num, "실제 반납 날짜가 날짜 형식이 아닙니다.")
                return (False, f"데이터 파일 무결성 검사에 실패했습니다. 오류 발생 위치 : {line_num}번째 줄 - 실제 반납 날짜가 날짜 형식이 아닙니다.")
            
            # 실제 반납 날짜가 대출 날짜 이후인지 확인(실제 반납 존재 시)
            if actual_return_date != "" and MyDate.from_str(actual_return_date) < MyDate.from_str(borrow_date):
                add_error(line_num, "실제 반납 날짜가 대출 날짜 이전입니다.")
                return (False, f"데이터 파일 무결성 검사에 실패했습니다. 오류 발생 위치 : {line_num}번째 줄 - 실제 반납 날짜가 대출 날짜 이전입니다.")
            
            # 반납 날짜가 대출 날짜 이후인지 확인
            if MyDate.from_str(return_date) < MyDate.from_str(borrow_date):
                add_error(line_num, "반납 날짜가 대출 날짜 이전입니다.")
                return (False, f"데이터 파일 무결성 검사에 실패했습니다. 오류 발생 위치 : {line_num}번째 줄 - 반납 날짜가 대출 날짜 이전입니다.")
            
            # 삭제 여부 검사
            if deleted not in ["0", "1"]:
                add_error(line_num, "삭제 여부가 0 또는 1이 아닙니다.")
                return (False, f"데이터 파일 무결성 검사에 실패했습니다. 오류 발생 위치 : {line_num}번째 줄 - 삭제 여부가 0 또는 1이 아닙니다.")
            
        return (True, "")

    def check_data_user_files(self,file_path: str) -> tuple[bool, str]:
        # 오류 발생한 줄과 오류 메세지 파일의 마지막 줄에 추가
        def add_error(line_num, error_message):
            now = datetime.now().strftime("%Y%m%d_%H%M%S")
            shutil.copy(opj(self.file_path, "data", "Libsystem_Data_User.txt"), opj(self.file_path, "data", f"Libsystem_Data_User-{now}.bak"))
            with open(opj(file_path, "data", f"Libsystem_Data_User-{now}.bak"), "a", encoding='utf-8') as f:
                f.write(f"데이터 파일 무결성 검사에 실패했습니다. 오류 발생 위치 : {line_num}번째 줄 - {error_message}\n")

        with open(opj(file_path, "data", "Libsystem_Data_User.txt"), "r", encoding='utf-8') as f:
            lines = f.readlines()
            
        line_num = 0
        
        # 구분자가 3개인지 확인
        for line in lines:
            line_num += 1
            line = line.strip()
            if line_num ==1 and line == "":
                return (True, "")
            if len(line.strip().split("/")) != 4:
                add_error(line_num, "구분자가 3개가 아닙니다")
                return (False, f"데이터 파일 무결성 검사에 실패했습니다. 오류 발생 위치 : {line_num}번째 줄 - 구분자가 3개가 아닙니다")
            
        line_num = 0

        # 모든 레코드의 앞 4개 항목 비어있지 않는 지 확인
        for line in lines:
            line_num += 1
            user_id, phone_number, name, deleted = line.strip().split("/")
            if user_id == "" or phone_number == "" or name == "" or deleted == "":
                add_error(line_num, "필수항목 중 비어있는 항목이 있습니다.")
                return (False, f"데이터 파일 무결성 검사에 실패했습니다. 오류 발생 위치 : {line_num}번째 줄 - 필수항목 중 비어있는 항목이 있습니다.")
            
        line_num = 0

        # 사용자 ID 검사
        for line in lines:
            line_num += 1
            user_id, phone_number, name, deleted = line.strip().split("/")
            # 사용자 ID가 숫자인지 확인
            if not user_id.isdigit():
                add_error(line_num, "사용자 ID가 0 이상의 숫자가 아닙니다.")
                return (False, f"데이터 파일 무결성 검사에 실패했습니다. 오류 발생 위치 : {line_num}번째 줄 - 사용자 ID가 0 이상의 숫자가 아닙니다.")
            
            # 사용자 ID 중복 검사
            user_ids = [line.strip().split("/")[0] for line in lines]
            if user_ids.count(user_id) > 1:
                add_error(line_num, "사용자 ID가 중복됩니다.")
                return (False, f"데이터 파일 무결성 검사에 실패했습니다. 오류 발생 위치 : {line_num}번째 줄 - 사용자 ID가 중복됩니다.")
            
            # 고유번호는 0부터 1씩 증가해야 함
            if int(user_id) != line_num - 1:
                add_error(line_num, "사용자 고유번호는 0부터 1씩 증가해야 합니다.")
                return (False, f"데이터 파일 무결성 검사에 실패했습니다. 오류 발생 위치 : {line_num}번째 줄 - 사용자 고유번호는 0부터 1씩 증가해야 합니다.")
            
            # 전화번호 검사(010-1234-5678 형식)
            if not re.match(r"01[0-9]-[0-9]{4}-[0-9]{4}", phone_number):
                add_error(line_num, "전화번호 형식이 잘못되었습니다.")
                return (False, f"데이터 파일 무결성 검사에 실패했습니다. 오류 발생 위치 : {line_num}번째 줄 - 전화번호 형식이 잘못되었습니다.")
            
            
            # 이름에 '/'나 '\'가 포함되어 있는지 확인
            if "/" in name or "\\" in name:
                add_error(line_num, "이름에 '/'나 '\\'가 포함되어 있습니다.")
                return (False, f"데이터 파일 무결성 검사에 실패했습니다. 오류 발생 위치 : {line_num}번째 줄 - 이름에 '/'나 '\\'가 포함되어 있습니다.")
            
            # 삭제 여부 검사
            if deleted not in ["0", "1"]:
                add_error(line_num, "삭제 여부가 0 또는 1이 아닙니다.")
                return (False, f"데이터 파일 무결성 검사에 실패했습니다. 오류 발생 위치 : {line_num}번째 줄 - 삭제 여부가 0 또는 1이 아닙니다.")
            
        return (True, "")

    def check_data_publisher_files(self,file_path: str) -> tuple[bool, str]:
        # 오류 발생한 줄과 오류 메세지 파일의 마지막 줄에 추가
        def add_error(line_num, error_message):
            now = datetime.now().strftime("%Y%m%d_%H%M%S")
            shutil.copy(opj(self.file_path, "data", "Libsystem_Data_Publisher.txt"), opj(self.file_path, "data", f"Libsystem_Data_Publisher-{now}.bak"))
            with open(opj(file_path, "data", f"Libsystem_Data_Publisher-{now}.bak"), "a", encoding='utf-8') as f:
                f.write(f"데이터 파일 무결성 검사에 실패했습니다. 오류 발생 위치 : {line_num}번째 줄 - {error_message}\n")

        with open(opj(file_path, "data", "Libsystem_Data_Publisher.txt"), "r", encoding='utf-8') as f:
            lines = f.readlines()
            
        line_num = 0

        # 구분자가 2개인지 확인
        for line in lines:
            line_num += 1
            line = line.strip()
            if line_num ==1 and line == "":
                return (True, "")
            if len(line.strip().split("/")) != 3:
                add_error(line_num, "구분자가 2개가 아닙니다")
                return (False, f"데이터 파일 무결성 검사에 실패했습니다. 오류 발생 위치 : {line_num}번째 줄 - 구분자가 2개가 아닙니다")
            
        line_num = 0

        # 모든 레코드의 앞 3개 항목 비어있지 않는 지 확인
        for line in lines:
            line_num += 1
            publisher_id, name, deleted = line.strip().split("/")
            if publisher_id == "" or name == "" or deleted == "":
                add_error(line_num, "필수항목 중 비어있는 항목이 있습니다.")
                return (False, f"데이터 파일 무결성 검사에 실패했습니다. 오류 발생 위치 : {line_num}번째 줄 - 필수항목 중 비어있는 항목이 있습니다.")
            
        line_num = 0

        # 출판사 ID 검사
        for line in lines:
            line_num += 1
            publisher_id, name, deleted = line.strip().split("/")
            # 출판사 ID가 숫자인지 확인
              # 출판사 ID 검사
            if not publisher_id.isdigit():
                add_error(line_num, "출판사 ID가 0 이상의 숫자가 아닙니다.")
                return (False, f"데이터 파일 무결성 검사에 실패했습니다. 오류 발생 위치 : {line_num}번째 줄 - 출판사 ID가 0 이상의 숫자가 아닙니다.")
            
            # 출판사 ID 중복 검사
            publisher_ids = [line.strip().split("/")[0] for line in lines]
            if publisher_ids.count(publisher_id) > 1:
                add_error(line_num, "출판사 ID가 중복됩니다.")
                return (False, f"데이터 파일 무결성 검사에 실패했습니다. 오류 발생 위치 : {line_num}번째 줄 - 출판사 ID가 중복됩니다.")
            
            # 고유번호는 0부터 1씩 증가해야 함
            if int(publisher_id) != line_num - 1:
                add_error(line_num, "출판사 고유번호는 0부터 1씩 증가해야 합니다.")
                return (False, f"데이터 파일 무결성 검사에 실패했습니다. 오류 발생 위치 : {line_num}번째 줄 - 출판사 고유번호는 0부터 1씩 증가해야 합니다.")
            
            # 이름에 '/'나 '\'가 포함되어 있는지 확인
            if "/" in name or "\\" in name:
                add_error(line_num, "출판사 이름에 '/'나 '\\'가 포함되어 있습니다.")
                return (False, f"데이터 파일 무결성 검사에 실패했습니다. 오류 발생 위치 : {line_num}번째 줄 - 출판사 이름에 '/'나 '\\'가 포함되어 있습니다.")
            
            # 삭제 여부 검사
            if deleted not in ["0", "1"]:
                add_error(line_num, "삭제 여부가 0 또는 1이 아닙니다.")
                return (False, f"데이터 파일 무결성 검사에 실패했습니다. 오류 발생 위치 : {line_num}번째 줄 - 삭제 여부가 0 또는 1이 아닙니다.")
            
        return (True, "")
    
    def check_data_overdue_penalty_files(self,file_path: str) -> tuple[bool, str]:
        # 오류 발생한 줄과 오류 메세지 파일의 마지막 줄에 추가
        def add_error(line_num, error_message):
            now = datetime.now().strftime("%Y%m%d_%H%M%S")
            shutil.copy(opj(self.file_path, "data", "Libsystem_Data_OverduePenalty.txt"), opj(self.file_path, "data", f"Libsystem_Data_OverduePenalty-{now}.bak"))
            with open(opj(file_path, "data", f"Libsystem_Data_OverduePenalty-{now}.bak"), "a", encoding='utf-8') as f:
                f.write(f"데이터 파일 무결성 검사에 실패했습니다. 오류 발생 위치 : {line_num}번째 줄 - {error_message}\n")

        with open(opj(file_path, "data", "Libsystem_Data_OverduePenalty.txt"), "r", encoding='utf-8') as f:
            lines = f.readlines()

        line_num = 0

        # 모든 레코드의 앞 4개 항목 비어있지 않는 지 확인
        for line in lines:
            line_num += 1
            line = line.strip()
            if line_num ==1 and line == "":
                return (True, "")
            # 구분자가 3개인지 확인
            if len(line.strip().split("/")) != 4:
                add_error(line_num, "구분자가 3개가 아닙니다")
                return (False, f"데이터 파일 무결성 검사에 실패했습니다. 오류 발생 위치 : {line_num}번째 줄 - 구분자가 3개가 아닙니다")

            panalty_id, user_id, panalty_start_date, panalty_end_date = line.strip().split("/")
            if panalty_id == "" or user_id == "" or panalty_start_date == "" or panalty_end_date == "":
                add_error(line_num, "필수항목 중 비어있는 항목이 있습니다.")
                return (False, f"데이터 파일 무결성 검사에 실패했습니다. 오류 발생 위치 : {line_num}번째 줄 - 필수항목 중 비어있는 항목이 있습니다.")
            
            # 패널티 ID가 숫자인지 확인
            if not panalty_id.isdigit():
                add_error(line_num, "패널티 ID가 0 이상의 숫자가 아닙니다.")
                return (False, f"데이터 파일 무결성 검사에 실패했습니다. 오류 발생 위치 : {line_num}번째 줄 - 패널티 ID가 0 이상의 숫자가 아닙니다.")
            
            # 패널티 ID 중복 검사
            panalty_ids = [line.strip().split("/")[0] for line in lines]
            if panalty_ids.count(panalty_id) > 1:
                add_error(line_num, "패널티 ID가 중복됩니다.")
                return (False, f"데이터 파일 무결성 검사에 실패했습니다. 오류 발생 위치 : {line_num}번째 줄 - 패널티 ID가 중복됩니다.")
            
            # 고유번호는 0부터 1씩 증가해야 함
            if int(panalty_id) != line_num - 1:
                add_error(line_num, "연체 패널티 고유번호는 0부터 1씩 증가해야 합니다.")
                return (False, f"데이터 파일 무결성 검사에 실패했습니다. 오류 발생 위치 : {line_num}번째 줄 - 연체 패널티 고유번호는 0부터 1씩 증가해야 합니다.")
            
            # 사용자 ID가 숫자인지 확인
            if not user_id.isdigit():
                add_error(line_num, "사용자 ID가 0 이상의 숫자가 아닙니다.")
                return (False, f"데이터 파일 무결성 검사에 실패했습니다. 오류 발생 위치 : {line_num}번째 줄 - 사용자 ID가 0 이상의 숫자가 아닙니다.")
            
            # 패널티 시작 날짜 검사
            if not MyDate.from_str(panalty_start_date):
                add_error(line_num, "패널티 시작 날짜가 날짜 형식이 아닙니다.")
                return (False, f"데이터 파일 무결성 검사에 실패했습니다. 오류 발생 위치 : {line_num}번째 줄 - 패널티 시작 날짜가 날짜 형식이 아닙니다.")
            
            # 패널티 종료 날짜 검사
            if not MyDate.from_str(panalty_end_date):
                add_error(line_num, "패널티 종료 날짜가 날짜 형식이 아닙니다.")
                return (False, f"데이터 파일 무결성 검사에 실패했습니다. 오류 발생 위치 : {line_num}번째 줄 - 패널티 종료 날짜가 날짜 형식이 아닙니다.")
            
            # 패널티 종료 날짜가 패널티 시작 날짜 이후인지 확인
            if MyDate.from_str(panalty_end_date) < MyDate.from_str(panalty_start_date):
                add_error(line_num, "패널티 종료 날짜가 패널티 시작 날짜 이전입니다.")
                return (False, f"데이터 파일 무결성 검사에 실패했습니다. 오류 발생 위치 : {line_num}번째 줄 - 패널티 종료 날짜가 패널티 시작 날짜 이전입니다.")
            
            # 사용자 고유번호 참조 무결성 검사
            user_id_found = False
            for user_record in self.user_table:
                if user_record.user_id == int(user_id):
                    user_id_found = True
                    break
                
            if not user_id_found:
                add_error(line_num, "참조하는 사용자 고유번호가 사용자 데이터에 없습니다.")
                return (False, f"데이터 파일 무결성 검사에 실패했습니다. 오류 발생 위치 : {line_num}번째 줄 - 참조하는 사용자 고유번호가 사용자 데이터에 없습니다.")
            
        return (True, "")
    
    def check_data_log_files(self, file_path: str) -> tuple[bool, str]:
        # 오류 발생한 줄과 오류 메세지 파일의 마지막 줄에 추가
        def add_error(line_num, error_message):
            now = datetime.now().strftime("%Y%m%d_%H%M%S")
            shutil.copy(opj(self.file_path, "data", "Libsystem_Data_Log.txt"), opj(self.file_path, "data", f"Libsystem_Data_Log-{now}.bak"))
            with open(opj(file_path, "data", f"Libsystem_Data_Log-{now}.bak"), "a", encoding='utf-8') as f:
                f.write(f"데이터 파일 무결성 검사에 실패했습니다. 오류 발생 위치 : {line_num}번째 줄 - {error_message}\n")

        with open(opj(file_path, "data", "Libsystem_Data_Log.txt"), "r", encoding='utf-8') as f:
            lines = f.readlines()
            
        line_num = 0
        last_log_date = None
        
        # log_id / isbn / book_id / borrow_id / log_date / log_type
        for line in lines:
            line_num += 1
            line = line.strip()
            
            # 구분자가 5개인지 확인
            if len(line.split("/")) != 6:
                add_error(line_num, "구분자가 5개가 아닙니다")
                return (False, f"데이터 파일 무결성 검사에 실패했습니다. 오류 발생 위치 : {line_num}번째 줄 - 구분자가 5개가 아닙니다")
        
            # log_id, isbn, log_date, log_type은 빈 값일 수 없음
            log_id, isbn, book_id, borrow_id, log_date, log_type = line.split("/")
            if log_id == "" or isbn == "" or log_date == "" or log_type == "":
                add_error(line_num, "필수항목 중 비어있는 항목이 있습니다.")
                return (False, f"데이터 파일 무결성 검사에 실패했습니다. 오류 발생 위치 : {line_num}번째 줄 - 필수항목 중 비어있는 항목이 있습니다.")
            
            # 자료형 검사
            if not log_id.isdigit():
                add_error(line_num, "로그 고유번호가 0 이상의 숫자가 아닙니다.")
                return (False, f"데이터 파일 무결성 검사에 실패했습니다. 오류 발생 위치 : {line_num}번째 줄 - 로그 고유번호가 0 이상의 숫자가 아닙니다.")
            
            if not isbn.isdigit() or int(isbn) > 99 or len(isbn) != 2:
                add_error(line_num, "ISBN이 00 이상, 99 이하의 숫자가 아닙니다.")
                return (False, f"데이터 파일 무결성 검사에 실패했습니다. 오류 발생 위치 : {line_num}번째 줄 - ISBN이 00 이상, 99 이하의 숫자가 아닙니다")
            
            # book_id, borrow_id는 정수
            if book_id != "" and not book_id.isdigit():
                add_error(line_num, "책 고유번호가 0 이상의 숫자가 아닙니다.")
                return (False, f"데이터 파일 무결성 검사에 실패했습니다. 오류 발생 위치 : {line_num}번째 줄 - 책 고유번호가 0 이상의 숫자가 아닙니다.")
            
            if borrow_id != "" and not borrow_id.isdigit():
                add_error(line_num, "대출 고유번호가 0 이상의 숫자가 아닙니다.")
                return (False, f"데이터 파일 무결성 검사에 실패했습니다. 오류 발생 위치 : {line_num}번째 줄 - 대출 고유번호가 0 이상의 숫자가 아닙니다.")
            
            # 고유번호는 0부터 1씩 증가해야 함
            if int(log_id) != line_num - 1:
                add_error(line_num, "로그 고유번호는 0부터 1씩 증가해야 합니다.")
                return (False, f"데이터 파일 무결성 검사에 실패했습니다. 오류 발생 위치 : {line_num}번째 줄 - 로그 고유번호는 0부터 1씩 증가해야 합니다.")
            
            # 참조하는 ISBN, Book ID, Borrow ID가 존재하는지 확인
            isbn_found = False
            for isbn_record in self.isbn_table:
                if isbn_record.isbn == int(isbn):
                    isbn_found = True
                    break
                
            if not isbn_found:
                add_error(line_num, "참조하는 ISBN이 ISBN 데이터에 없습니다.")
                return (False, f"데이터 파일 무결성 검사에 실패했습니다. 오류 발생 위치 : {line_num}번째 줄 - 참조하는 ISBN이 ISBN 데이터에 없습니다.")
            
            if book_id != "":
                book_id_found = False
                for book_record in self.book_table:
                    if book_record.book_id == int(book_id):
                        book_id_found = True
                        break
                    
                if not book_id_found:
                    add_error(line_num, "참조하는 책 고유번호가 책 데이터에 없습니다.")
                    return (False, f"데이터 파일 무결성 검사에 실패했습니다. 오류 발생 위치 : {line_num}번째 줄 - 참조하는 책 고유번호가 책 데이터에 없습니다.")
                
            if borrow_id != "":
                borrow_id_found = False
                for borrow_record in self.borrow_table:
                    if borrow_record.borrow_id == int(borrow_id):
                        borrow_id_found = True
                        break
                    
                if not borrow_id_found:
                    add_error(line_num, "참조하는 대출 고유번호가 대출 데이터에 없습니다.")
                    return (False, f"데이터 파일 무결성 검사에 실패했습니다. 오류 발생 위치 : {line_num}번째 줄 - 참조하는 대출 고유번호가 대출 데이터에 없습니다.")
                
            # log type 검사
            if log_type not in ["BOOK_REGISTER", "ISBN_EDIT", "BOOK_BORROW", "BOOK_RETURN", "BOOK_DELETE"]:
                add_error(line_num, "로그 타입이 올바른 값이 아닙니다.")
                return (False, f"데이터 파일 무결성 검사에 실패했습니다. 오류 발생 위치 : {line_num}번째 줄 - 로그 타입이 올바른 값이 아닙니다.")
            
            # log date 검사
            if not MyDate.from_str(log_date):
                add_error(line_num, "로그 날짜가 날짜 형식이 아닙니다.")
                return (False, f"데이터 파일 무결성 검사에 실패했습니다. 오류 발생 위치 : {line_num}번째 줄 - 로그 날짜가 날짜 형식이 아닙니다.")
            
            # 고유번호는 날짜 오름차순으로 존재해야 함 (이전 날짜보다 크거나 같음)
            log_date = MyDate.from_str(log_date)
            if last_log_date is not None and log_date < last_log_date:
                add_error(line_num, "로그 날짜는 오름차순으로 정렬되어야 합니다.")
                return (False, f"데이터 파일 무결성 검사에 실패했습니다. 오류 발생 위치 : {line_num}번째 줄 - 로그 날짜는 오름차순으로 정렬되어야 합니다.")
            
            last_log_date = log_date
            
            # book id와 ISBN 관계 검사
            if book_id != "":
                book_record = None
                for book in self.book_table:
                    if book.book_id == int(book_id):
                        book_record = book
                        break
                
                if book_record is None or book_record.isbn != int(isbn):
                    add_error(line_num, "책 고유번호에 대한 ISBN이 올바르지 않습니다.")
                    return (False, f"데이터 파일 무결성 검사에 실패했습니다. 오류 발생 위치 : {line_num}번째 줄 - 책 고유번호에 대한 ISBN이 올바르지 않습니다.")
                
            # borrow id와 book id 관계 검사
            if borrow_id != "":
                borrow_record = None
                for borrow in self.borrow_table:
                    if borrow.borrow_id == int(borrow_id):
                        borrow_record = borrow
                        break
                
                if borrow_record is None or borrow_record.book_id != int(book_id):
                    add_error(line_num, "대출 고유번호에 대한 책 고유번호가 올바르지 않습니다.")
                    return (False, f"데이터 파일 무결성 검사에 실패했습니다. 오류 발생 위치 : {line_num}번째 줄 - 대출 고유번호에 대한 책 고유번호가 올바르지 않습니다.")
                
        return (True, "")
    
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
                if borrow.book_id == book_id and borrow.actual_return_date is None: # 반납이 완료된 대출 정보는 제외:
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
        
        # 저자 없는 경우 
        if len(author_data) == 0:
            return_str += "-"
        else:
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
        for book in self.book_table: # 삭제가 안되었거나 삭제되었지만 삭제 날짜가 오늘 이후인 경우 출력
            if not book.deleted or (book.deleted and book.delete_date > self.today):
                print(self.print_book(book.book_id, include_borrow=True))

    def load_configuration(self) -> None:
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
    def check_book_id_validate(self, book_id, flag, include_deleted=False): # flag == 0 -> 있으면 False 없으면 True, flag == 1 -> 없으면 False 있으면 True
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
            return False, f"고유번호는 0에서 {self.config['max_static_id']} 사이여야 합니다."
        
        if flag == 0 and self.search_book_by_id(book_id_int, include_deleted=include_deleted):
            return False, "중복된 고유번호가 존재합니다."
        
        if flag == 1 and self.search_book_by_id(book_id_int, include_deleted=include_deleted) is None:
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

    def check_phone_number_validate(self, phone_number):
        if phone_number == self.config["cancel"]:
            return True, ""
        # 정규표현식으로 010-XXXX-XXXX 형식 확인
        pattern = r'^010-\d{4}-\d{4}$'
        if re.fullmatch(pattern, phone_number):
            return True, ""
        return False, "전화번호는 010-XXXX-XXXX 형식이어야 합니다."
    
    def check_author_id_validate(self, author_id): 
        if author_id == self.config["cancel"]:
            return True, ""
        
        # 1. 입력값이 공백으로만 구성되지 않았는지 확인
        if author_id.strip() == "":
            return False, "저자의 식별번호는 공백일 수 없습니다."
        
        # 2. 저자의 식별번호가 숫자로만 구성되어 있는지 확인
        if not author_id.isdigit():
            return False, "저자의 식별번호는 숫자여야 합니다."
        
        # 3. 저자의 식별번호가 0으로 시작하는 지 확인
        if author_id.startswith("0"):
            return False, "저자의 식별번호는 0으로 시작할 수 없습니다."
        
        # 4. 저자의 식별번호가 1 이상인지 확인
        if int(author_id) < 1:
            return False, "저자의 식별번호는 1 이상이어야 합니다."
        
        return True, ""

    def check_overdue_delete(self, book_id):
        for book in self.book_table:
            for borrow in self.borrow_table:
                if borrow.book_id == book_id and borrow.actual_return_date is None:
                    return True
        return False

    def check_borrow_delete(self, book_id):
        for borrow in self.borrow_table:
            if borrow.book_id == book_id and borrow.return_date is not None:
                return True
        return False        
    
    # 저자 식별번호로 이름 #식별번호 형태로 반환
    def convert_author_ids_to_name_id(self, author_ids: list[int]) -> str:
        names = []
        
        # 저자 없는 경우 "-" 반환
        if len(author_ids) == 0:
            return "-"
        
        for author_id in author_ids:
            author = self.search_author_by_id(author_id)
            if author:
                # 동명 이인 있는 경우 식별번호를 붙여줌
                if len(self.search_author_by_name(author.name)) > 1:
                    names.append(f"{author.name} #{author.author_id}")
                else:
                    names.append(author.name)
                
        return " & ".join(names)

    # ========== 검색 함수 ========== #
    # 고유번호로 검색
    def search_book_by_id(self, book_id, include_deleted: bool=False) -> BookRecord:
        """_summary_ 
        책 고유번호로 책 인스턴스 반환
        """
        if include_deleted:
            for book in self.book_table:
                if book.book_id == book_id:
                    return book
                
        else:
            for book in self.book_table:
                if book.book_id == book_id and (not book.deleted or (book.deleted and book.delete_date > self.today)):
                    return book

        return None
    
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
    
    def search_borrow_by_id(self, borrow_id) -> BorrowRecord:
        """_summary_
        대출 ID로 대출 인스턴스 반환
        """
        for borrow in self.borrow_table:
            if borrow.borrow_id == borrow_id:
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
                    if isinstance(author, AuthorRecord):
                        author_name = author.name
                    else:
                        author_name = author

                    if i == len(book_info[1]) - 1:
                        author_string += author_name
                    else:
                        author_string += f"{author_name} & "
            
            print(self.get_header())
            print()

            print(f"{book_id}/{new_isbn.isbn}/{new_isbn.title}/{author_string}/{publisher.name}/{new_isbn.published_year}/{new_isbn.isbn_register_date}")
            print()
            
            if self.input_response("해당 책을 추가하시겠습니까?(Y/N): "):
                if not publisher_flag:
                    self.publisher_table.append(publisher)
                
                for author in book_info[1]:
                    if not isinstance(author, AuthorRecord):
                        self.author_table.append(AuthorRecord(len(self.author_table) + 1, author, False))
                        self.isbn_author_table.append(IsbnAuthorRecord(isbn, self.author_table[-1].author_id))
                    else:
                        self.isbn_author_table.append(IsbnAuthorRecord(isbn, author.author_id))

                self.isbn_table.append(new_isbn)
                self.book_table.append(new_book)    
                
                # 책 등록 로그 추가
                self.add_to_log(log_type="BOOK_REGISTER", isbn=new_isbn.isbn, book_id=new_book.book_id, borrow_id=None, log_date=self.today)
                
                self.fetch_data_file()
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
                
                # 책 등록 로그 추가
                self.add_to_log(log_type="BOOK_REGISTER", isbn=isbn, book_id=new_book.book_id, borrow_id=None, log_date=self.today)
                
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

        book_to_delete = self.search_book_by_id(del_book_id)
        if book_to_delete.deleted:
            print("ERROR: 이미 삭제된 책이므로 삭제할 수 없습니다.")
            return False

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
            for i in range(len(self.book_table)):
                if self.book_table[i].book_id == del_book_id:
                    self.book_table[i].deleted = True
                    self.book_table[i].delete_date = self.today
                    
                    # 책 삭제 로그 추가
                    self.add_to_log(log_type="BOOK_DELETE", isbn=self.book_table[i].isbn, book_id=self.book_table[i].book_id, borrow_id=None, log_date=self.today)
                    
                    break
            
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
        total_error_message = ""
        is_total_valid = True

        if not input_author_list:
            return True, None
        
        if len(input_author_list) > 5:
            return False, "ERROR: 책의 저자는 최대 5명입니다."
        
        for author in input_author_list:
            if author.count("#") > 1:
                is_total_valid = False
                total_error_message += f"[{author}] ERROR: 저자의 형식은 '이름' 또는 '이름 #식별번호' 둘 중 하나여야 합니다.\n"

        if not is_total_valid:
            return False, total_error_message
        
        for author in input_author_list:
            if "#" in author:
                name, number = author.split("#")
                name = name.strip()
                number = number.strip()
            else:
                name = author.strip()
                number = None

            is_valid, error_message = self.check_string_validate("저자의 이름", name)
            if not is_valid:
                is_total_valid = False
                total_error_message += f"[{author}] ERROR: {error_message}\n"

            if number is not None:
                is_valid, error_message = self.check_author_id_validate(number)
                if not is_valid:
                    is_total_valid = False
                    total_error_message += f"[{author}] ERROR: {error_message}\n"

        if not is_total_valid:
            return False, total_error_message
        
        for author in input_author_list:
            if "#" in author:
                _, number = author.split("#")
                number = number.strip()

                author_data = self.search_author_by_id(int(number))
                if not author_data:
                    is_total_valid = False
                    total_error_message += f"[{author}] ERROR: {int(number)}번 저자가 존재하지 않습니다.\n"
                elif author_data.name != name:
                    is_total_valid = False
                    total_error_message += f"[{author}] ERROR: {int(number)}번 저자의 이름은 '{name}'이 아닙니다.\n"
        if is_total_valid:
            return True, None
        else:
            return False, total_error_message

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

         # 2. 책 저자 입력 (add_book과 동일한 로직 호출)
        valid_authors = self.handle_author_input(cancel_value)
        if valid_authors is None:  # 입력 취소 시
            print("수정을 중단하며 메인 프롬프트로 돌아갑니다.")
            return False

        # 3. 출판사 입력
        while True:
            new_publisher = input("수정할 책의 출판사를 입력해주세요: ").strip()
            if not new_publisher or not self.check_string_validate("출판사", new_publisher):
                print("ERROR: 입력한 출판사가 유효하지 않습니다.")
            else:
                break
            
        # 출판사 수정
        new_publisher_id = None
        for publisher in self.publisher_table:
            if publisher.name == new_publisher:  # 입력된 출판사가 이미 존재하면
                new_publisher_id = publisher.publisher_id  # 해당 출판사의 ID 반영
                new_publisher_data = None
                break

        if new_publisher_id is None:  # 입력된 출판사가 존재하지 않으면
            new_publisher_id = len(self.publisher_table)
            new_publisher_data = PublisherRecord(new_publisher_id, new_publisher, False)  # 새 출판사 데이터 추가
        
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
                isbn_data.publisher_id = new_publisher_id
                break
            
        # 출판사가 새로 추가된 경우에 테이블에 추가
        if new_publisher_data is not None:
            self.publisher_table.append(new_publisher_data)
            
        # 책 수정 로그 추가
        self.add_to_log(log_type="ISBN_EDIT", isbn=isbn, book_id=None, borrow_id=None, log_date=self.today)

        # 저자 수정
        # 기존 저자-ISBN 관계 삭제
        self.isbn_author_table = [ia for ia in self.isbn_author_table if ia.isbn != isbn]
        # 새 저자-ISBN 관계 추가
        for name, number in valid_authors:
            self.isbn_author_table.append(IsbnAuthorRecord(isbn, number))

        print("수정이 완료되었습니다.")
        self.fetch_data_file()
        return True
    def handle_author_input(self, cancel_value):
        """저자 입력 처리 공통 메서드"""
        while True:
            authors_input = input("수정할 책의 저자를 입력해주세요: ").strip()
            if authors_input == cancel_value:
                return None  # 입력 취소 시 None 반환

            if not authors_input:
                confirm = input("저자가 없는 책으로 처리하시겠습니까? (Y/N): ").strip().lower()
                if confirm == 'y':
                    return []  # 빈 리스트 반환
                else:
                    continue  # 다시 입력 받기

            # 입력된 저자 이름 목록을 분리
            author_list = [author.strip() for author in authors_input.split("&") if author.strip()]
            if len(author_list) > 5:
                print("ERROR: 저자 입력이 5명을 초과합니다. 다시 입력해주세요.")
                continue

            valid_authors = set()  # 중복 제거를 위한 집합 사용
            errors = []

            for author_entry in author_list:
                if "#" in author_entry:  # #이 포함된 경우 처리
                    try:
                        name, author_id = author_entry.rsplit("#", 1)
                        name = name.strip()
                        author_id = int(author_id.strip())
                        valid_authors.add((name, author_id))  # 중복 자동 제거
                        continue  # 다음 저자로 넘어감
                    except ValueError:
                        print(f"ERROR: '{author_entry}'에서 식별번호 형식이 잘못되었습니다. 다시 입력해주세요.")
                        continue

                while True:  # 각 저자에 대해 반복적으로 질문
                    matching_authors = self.search_author_by_name(author_entry)
                    if not matching_authors:  # 동일 이름의 저자가 없으면 새로 추가
                        print(f"[{author_entry}] 해당 이름의 저자가 없습니다. 새로 추가합니다.")
                        new_author_id = len(self.author_table) + 1
                        self.author_table.append(AuthorRecord(new_author_id, author_entry, False))
                        valid_authors.add((author_entry, new_author_id))
                        break
                    else:
                        print(f"이미 등록되어 있는 저자가 {len(matching_authors)}명이 있습니다.")
                        for idx, match in enumerate(matching_authors):
                            if len(matching_authors) > 1:
                                print(f"{idx + 1}. {match.name} #{match.author_id}")
                            else:
                                print(f"{idx + 1}. {match.name}")  # 동명이인이 없으면 번호 출력하지 않음
                        print("0. (새 동명이인 추가)")

                        try:
                            choice = int(input("해당 저자의 번호를 입력해주세요: "))
                            if choice == 0:  # 새 동명이인 추가
                                new_author_id = len(self.author_table) + 1
                                self.author_table.append(AuthorRecord(new_author_id, author_entry, False))
                                valid_authors.add((author_entry, new_author_id))
                                break
                            elif 1 <= choice <= len(matching_authors):  # 선택된 저자를 추가
                                selected_author = matching_authors[choice - 1]
                                valid_authors.add((selected_author.name, selected_author.author_id))
                                break
                            else:
                                print("ERROR: 잘못된 선택입니다. 다시 입력해주세요.")
                        except ValueError:
                            print("ERROR: 입력값이 유효하지 않습니다. 다시 입력해주세요.")
                            continue

            if errors:
                print("\n".join(errors))
                print("모든 저자의 이름과 식별번호를 다시 입력해주세요.")
            else:
                return list(valid_authors)  # 집합을 리스트로 변환하여 반환


    
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
            self.print_book_all()
            return True
        
        is_valid, error_message = self.check_string_validate("제목 또는 저자", search_book)
        if not is_valid:
            print(f"ERROR: {error_message}")
            return False
        
        self.search_content_book(search_book)
    
    def search_content_book(self, search_book):
        search_results = []
        
        for book in self.book_table:
            # find isbn
            isbn_data = None
            for isbn in self.isbn_table:
                if isbn.isbn == book.isbn:
                    isbn_data = isbn
                    
                
            # find author isbn relationship
            author_isbn_data = None
            for isbn_author in self.isbn_author_table:
                if isbn_author.isbn == isbn_data.isbn:
                    author_isbn_data = isbn_author
                    
                
            author_data = None
            for author in self.author_table:
                if author.author_id == author_isbn_data.author_id:
                    author_data = author
                    

            # 만약 #로 search_book이 시작하면 해당 작가 식별 번호 가진 책 검색
            if search_book.startswith("#"):
                # 제목에 포함되는지 확인 (첫 글자 # 포함)
                if search_book in isbn_data.title and (not book.deleted or (book.deleted and book.delete_date > self.today)):
                    search_results.append(book)
                else:
                    # # 문자 제외한 나머지 부분을 저자 식별번호와 완전 일치 비교
                    author_id_str = search_book[1:].strip()
                    if author_id_str == str(author_data.author_id) and (not book.deleted or (book.deleted and book.delete_date > self.today)):
                        search_results.append(book)

            else:
                # 제목에 포함되는지 확인
                if search_book in isbn_data.title and (not book.deleted or (book.deleted and book.delete_date > self.today)):
                    search_results.append(book)
                # 저자 이름에 포함되는지 확인 (중간에 #이 있어도 이름으로 비교)
                elif search_book in author_data.name and (not book.deleted or (book.deleted and book.delete_date > self.today)):
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
            print(self.get_header(contain_borrow_info=True))
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
            
            # 책 대출 로그 추가
            self.add_to_log(log_type="BOOK_BORROW", isbn=book.isbn, book_id=book_id, borrow_id=borrow.borrow_id, log_date=self.today)
            
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
        
        # 고유번호에 해당하는 책 존재 여부 확인
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
        
        author_name = self.convert_author_ids_to_name_id(author_ids)
        
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
                
        # 책 반납 로그 추가
        self.add_to_log(log_type="BOOK_RETURN", isbn=rtn_isbn.isbn, book_id=borrow_info.book_id, borrow_id=borrow_info.borrow_id, log_date=self.today)
                
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
            print("-"*20)
            print("Libsystem >",end="")
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
    def add_to_log(self, log_type: str, isbn: int, book_id: int, borrow_id: int, log_date: MyDate) -> bool:
        assert log_type in ["BOOK_REGISTER", "ISBN_EDIT", "BOOK_BORROW", "BOOK_RETURN", "BOOK_DELETE"]
        assert isbn is not None, "ISBN은 None일 수 없습니다."
        assert log_date is not None, "로그 날짜는 None일 수 없습니다."

        new_log = LogRecord(len(self.log_table), isbn, book_id, borrow_id, log_date, log_type)
        self.log_table.append(new_log)
        self.fetch_data_file()
        
        return True
    
    def history(self):
        history_book_id = self.input_book_id("연혁(로그) 조회를 할 책의 고유번호를 입력해주세요: ", 1, include_deleted=True)

        if (history_book_id==None):
            return False  # 입력 실패 시 반환

        if history_book_id == self.config["cancel"]:
            print("연혁(로그) 조회를 취소했습니다. 메인 프롬프트로 돌아갑니다.")
            return False
        
        history_book_id = int(history_book_id)
        
        # 고유번호에 해당하는 책 존재 여부 확인
        book_history = self.search_book_by_id(history_book_id, include_deleted=True)
        
        if not book_history:
            print("ERROR: 해당 고유번호의 책이 존재하지 않습니다.")
            return False
        
        history_isbn = self.search_isbn_data(book_history.isbn)
        author_ids = self.search_author_ids_by_isbn(history_isbn.isbn)
        
        author_name = self.convert_author_ids_to_name_id(author_ids)
        
        history_publisher = self.search_publisher_by_id(history_isbn.publisher_id)
        print(f"{history_book_id} / {book_history.isbn} / {history_isbn.title} / {author_name} / {history_publisher.name} / {history_isbn.published_year} / {book_history.register_date}")

        # ISBN 등록 먼저 출력
        isbn_record = self.search_isbn_data(book_history.isbn)
        print(f"{isbn_record.isbn_register_date} ISBN 등록")

        for log in self.log_table:
            if history_isbn.isbn == log.isbn:
                # 1) ISBN_EDIT
                if log.log_type == "ISBN_EDIT":
                    print(f"{log.log_date} ISBN 수정")
                    continue
                
                # 2) BOOK_REGISTER
                if log.log_type == "BOOK_REGISTER" and log.book_id == history_book_id:
                    print(f"{log.log_date} 입고")
                    continue
                
                # 3) BOOK_BORROW
                if log.log_type == "BOOK_BORROW" and log.book_id == history_book_id:
                    # 대출 데이터 검색
                    borrow_data = self.search_borrow_by_id(log.borrow_id)
                    # 대출자 정보 검색
                    borrower_data = self.search_user_by_id(borrow_data.user_id)
                    
                    print(f"{log.log_date} 대출: {borrower_data.phone_number} {borrower_data.name} / {borrow_data.return_date}")
                    continue
                
                # 4) BOOK_RETURN
                if log.log_type == "BOOK_RETURN" and log.book_id == history_book_id:
                    # 대출 데이터 검색
                    borrow_data = self.search_borrow_by_id(log.borrow_id)
                    # 대출자 정보 검색
                    borrower_data = self.search_user_by_id(borrow_data.user_id)
                    
                    # 연체인 경우
                    assert borrow_data.actual_return_date is not None, "반납일이 None일 수 없습니다."
                    if borrow_data.actual_return_date > borrow_data.return_date:
                        print(f"{log.log_date} 반납 ({borrow_data.actual_return_date - borrow_data.return_date}일 연체)")
                    else:
                        print(f"{log.log_date} 반납")
                
                # 5) BOOK_DELETE
                if log.log_type == "BOOK_DELETE" and log.book_id == history_book_id:
                    assert log.log_date == book_history.delete_date, "삭제일과 로그 날짜가 일치하지 않습니다"
                    print(f"{log.log_date} 삭제")
                    continue
        
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
        for book in self.book_table:
            # 등록 날짜가 현재 날짜보다 미래인 경우
            if book.register_date > today:
                return False, f"가장 최근에 저장된 책의 등록날짜 또는 대출날짜보다 과거의 날짜입니다."
            
            
        for isbn_year in self.isbn_table:
            # 출판년도는 현재 날짜보다 미래일 수 없음 (무결성검사에서 검사해서 오류나면 안됨)
            if isbn_year.published_year > today.year:
                print("여기서 오류가 난다는 것은 출판년도보다 등록일이 과거라는 의미임")
                return False, f"critical error is occured"
            
        # 대출 날짜와 비교   
        for record in self.borrow_table:
            if record.borrow_date is not None and record.borrow_date > today:
                return False, f"가장 최근에 저장된 책의 등록날짜 또는 대출날짜보다 과거의 날짜입니다."
            
        return (True, None)

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
            print(f"{error_message}")
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
                            break
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

    def input_book_id(self, input_message: str, flag: int, include_deleted=False) -> int: # flag == 0 -> 중복되면 False, flag == 1 -> 중복되어도 True
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

        is_valid, error_message = self.check_book_id_validate(book_id, flag, include_deleted=include_deleted)
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
def main() -> None:
    try:
        dir_path = get_user_home_path()
        
        if dir_path is None or len(dir_path) == 0:
            raise ValueError 
        
    except Exception as e:
        # print(e)
        # print("[DEBUG] HOME 경로를 찾을 수 없어 현재 경로로 지정")
        dir_path = "./"
        
    print(dir_path)
    
    # print("[DEBUG] HOME 경로:", dir_path)
    bookData = DataManager(file_path=dir_path)
    
    # config 불러오기
    bookData.load_configuration()
    
    # 데이터 파일 읽기
    done, message = bookData.read_data_files(verbose=True)
    
    if not done:
        print("ERROR:", message)
        print("프로그램을 종료합니다.")
        return
    
    # 현재 날짜 입력
    today = input_date(bookData)
    bookData.set_today(today)
    
    main_prompt(bookData=bookData)
    
    # 파일 저장 후 종료
    bookData.fetch_data_file()


if __name__ == "__main__":
    main()
