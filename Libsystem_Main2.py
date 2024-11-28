import os
# import datetime
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
    def __init__(self, book_id: int, user_id: int, borrow_date: MyDate, return_date: MyDate, actual_return_date: MyDate=None, deleted: bool=False):
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
        self.today = None
        self.config = dict()
        self.static_id = -1
    
    # 오늘 날짜 설정
    def set_today(self, today: MyDate):
        self.today = today
        
    # 데이터 파일 읽기
    def read_data_files(self, sep: str="/", verbose=True):
        
        if verbose: print("="*10, "Start Reading Data Files", "="*10)
        
        # 1. Book Data
        with open(opj(self.file_path, "data", "Libsystem_Data_Book.txt"), "r") as f:
            lines = f.readlines()
            
            self.static_id = int(lines[0])
            
            for line in lines[1:]:
                book_id, isbn, register_date, deleted, delete_date = line.strip().split(sep)
                self.book_table.append(BookRecord(int(book_id), int(isbn), MyDate.from_str(register_date), MyDate.from_str(delete_date), bool(int(deleted))))
          
        if verbose:      
            print(f"{len(self.book_table)} Book Data Loaded")
            print(f"max_book_id: {self.static_id}")
                
        # 2. ISBN Data
        with open(opj(self.file_path, "data", "Libsystem_Data_Isbn.txt"), "r") as f:
            for line in f:
                isbn, title, publisher_id, published_year, isbn_register_date = line.strip().split(sep)
                self.isbn_table.append(ISBNRecord(int(isbn), title, int(publisher_id), int(published_year), MyDate.from_str(isbn_register_date)))
                
        if verbose: print(f"{len(self.isbn_table)} ISBN Data Loaded")
                
        # 3. Author Data
        with open(opj(self.file_path, "data", "Libsystem_Data_Author.txt"), "r") as f:
            for line in f:
                author_id, name, deleted = line.strip().split(sep)
                self.author_table.append(AuthorRecord(int(author_id), name, bool(int(deleted))))
                
        if verbose: print(f"{len(self.author_table)} Author Data Loaded")
                
        # 4. ISBN - Author Data
        with open(opj(self.file_path, "data", "Libsystem_Data_IsbnAuthor.txt"), "r") as f:
            for line in f:
                isbn, author_id = line.strip().split(sep)
                self.isbn_author_table.append(IsbnAuthorRecord(int(isbn), int(author_id)))
                
        if verbose: print(f"{len(self.isbn_author_table)} ISBN - Author Data Loaded")
                
        # 5. Book Edit Log Data
        with open(opj(self.file_path, "data", "Libsystem_Data_BookEditLog.txt"), "r") as f:
            for line in f:
                log_id, isbn, edit_date = line.strip().split(sep)
                self.book_edit_log_table.append(BookEditLogRecord(int(log_id), int(isbn), MyDate.from_str(edit_date)))
                
        if verbose: print(f"{len(self.book_edit_log_table)} Book Edit Log Data Loaded")
                
        # 6. Borrow Data
        with open(opj(self.file_path, "data", "Libsystem_Data_Borrow.txt"), "r") as f:
            for line in f:
                book_id, user_id, borrow_date, return_date, actual_return_date, deleted = line.strip().split(sep)
                self.borrow_table.append(BorrowRecord(int(book_id), int(user_id), MyDate.from_str(borrow_date), MyDate.from_str(return_date), MyDate.from_str(actual_return_date), bool(int(deleted))))
                
        if verbose: print(f"{len(self.borrow_table)} Borrow Data Loaded")            
    
        # 7. User Data
        with open(opj(self.file_path, "data", "Libsystem_Data_User.txt"), "r") as f:
            for line in f:
                user_id, phone_number, name, deleted = line.strip().split(sep)
                self.user_table.append(UserRecord(int(user_id), phone_number, name, bool(int(deleted))))
        
        if verbose: print(f"{len(self.user_table)} User Data Loaded")
        
        # 8. Publisher Data
        with open(opj(self.file_path, "data", "Libsystem_Data_Publisher.txt"), "r") as f:
            for line in f:
                publisher_id, name, deleted = line.strip().split(sep)
                self.publisher_table.append(PublisherRecord(int(publisher_id), name, bool(int((deleted)))))
                
        if verbose: 
            print(f"{len(self.publisher_table)} Publisher Data Loaded")
            print("="*10, "End Reading Data Files", "="*10)
        
    
    # ========== 데이터 파일 저장 (임시) ========== #
    def write_data_files(self):
        # 1. Book Data
        with open(opj(self.file_path, "data", "Libsystem_Data_Book.txt"), "w") as f:
            for book in self.book_table:
                f.write(f"{book.book_id}/{book.isbn}/{str(book.register_date)}/{int(book.deleted)}/{str(book.delete_date)}\n")
                
        # 2. ISBN Data
        with open(opj(self.file_path, "data", "Libsystem_Data_Isbn.txt"), "w") as f:
            for isbn in self.isbn_table:
                f.write(f"{isbn.isbn}/{isbn.title}/{isbn.publisher_id}/{isbn.published_year}/{str(isbn.isbn_register_date)}\n")
                
        # 3. Author Data
        with open(opj(self.file_path, "data", "Libsystem_Data_Author.txt"), "w") as f:
            for author in self.author_table:
                f.write(f"{author.author_id}/{author.name}/{int(author.deleted)}\n")
                
        # 4. ISBN - Author Data
        with open(opj(self.file_path, "data", "Libsystem_Data_IsbnAuthor.txt"), "w") as f:
            for isbn_author in self.isbn_author_table:
                f.write(f"{isbn_author.isbn}/{isbn_author.author_id}\n")
                
        # 5. Book Edit Log Data
        with open(opj(self.file_path, "data", "Libsystem_Data_BookEditLog.txt"), "w") as f:
            for log in self.book_edit_log_table:
                f.write(f"{log.log_id}/{log.isbn}/{str(log.edit_date)}\n")
                
        # 6. Borrow Data
        with open(opj(self.file_path, "data", "Libsystem_Data_Borrow.txt"), "w") as f:
            for borrow in self.borrow_table:
                f.write(f"{borrow.book_id}/{borrow.user_id}/{str(borrow.borrow_date)}/{str(borrow.return_date)}/{str(borrow.actual_return_date)}/{int(borrow.deleted)}\n")
                
        # 7. User Data
        with open(opj(self.file_path, "data", "Libsystem_Data_User.txt"), "w") as f:
            for user in self.user_table:
                f.write(f"{user.user_id}/{user.phone_number}/{user.name}/{int(user.deleted)}\n")
                
        # 8. Publisher Data
        with open(opj(self.file_path, "data", "Libsystem_Data_Publisher.txt"), "w") as f:
            for publisher in self.publisher_table:
                f.write(f"{publisher.publisher_id}/{publisher.name}/{int(publisher.deleted)}\n")
    
    # ========== 데이터 파일 메모리 -> 파일 동기화 (fetch) ========== #
    def fetch_data_file(self):
        pass
    
    # ========== 데이터 파일 무결성 검사 ========== #
    def check_data_files(self):
        pass
    
    # =========== 책 레코드를 문자열로 반환 ========== #
    def print_book(self, book_id: int, include_borrow: bool=False):        
        # find book
        book_data = None
        for book in self.book_table:
            if book.book_id == book_id:
                book_data = book
                break
        
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
                
        return_str = f"{book_data.book_id}/"
        return_str += str(isbn_data.isbn).zfill(2) + "/"
        return_str += f"{isbn_data.title}/"
        return_str += f"{" & ".join(list(map(lambda x:f"{x.name} #{x.author_id}", author_data)))}/"
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

    # =========== 설정 불러오기 ========== #
    def load_configuration(self) -> dict:
        config_dict = dict()
        
        try:
            with open(opj(self.file_path, "Libsystem_Config.json"), "r") as f:
                config = json.load(f)
                
            for c in config['configuration']:
                if c['value_type'] == 'int':
                    config_dict[c['constant_name']] = int(c['value'])
                else:
                    config_dict[c['constant_name']] = c['value']
                    
            self.config = config_dict
        
        except Exception as e:
            print("설정 파일을 찾을 수 없습니다.")
            
            new_config_dict = {
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
                    }
                ]
            }
            
            # config 파일 저장
            with open(opj(dir_path, "Libsystem_Config.json"), "w") as f:
                json.dump(new_config_dict, f, indent=4)
            
            config_dict = {
                "borrow_date": 7
            }
            
            self.config = config_dict

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
        if book_id_int < 0 or book_id_int > self.MAX_STATIC_ID:
            return False, "고유번호는 0에서 99 사이여야 합니다."
        
        if flag == 0 and self.search_id(book_id_int):
            return False, "중복된 고유번호가 존재합니다."
        
        if flag == 1 and self.search_id(book_id_int) is None:
            return False, "해당 고유번호를 가진 책이 존재하지 않습니다."
        
        return True, ""

    def check_string_validate(self, field_name, value):
        if value == self.config["cancel"]:
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
        if year == self.config["cancel"]:
            return True, ""
        # 1. 입력값이 숫자인지 확인
        if not year.isdigit():
            return False, "책의 출판년도는 오로지 숫자로만 구성되어야 합니다."
    
        # 2. 출판년도는 4자리 숫자여야 함을 확인
        if len(year) != 4:
            return False, "책의 출판년도는 4자리 양의 정수여야 합니다."
        
        year_int = int(year)
        current_year = today.year  # 현재 연도를 확인하는 변수

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
            
            # 연도가 1583 이상 9999 이하인지 확인
            if not (1583 <= year <= 9999):
                return False, "날짜는 1583년부터 9999년 사이여야 합니다."
            
            if not MyDate.validate_day(year, month, day):
                raise ValueError
            
            return True, ""
        
        except:
            return False, "날짜 형식이 올바르지 않습니다. (예: YYYY-MM-DD)"

    def check_isbn_validate(self, isbn):
        if isbn == self.config["cancel"]:
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

    def check_record_validate(self, book: BookRecord) -> tuple[bool, str]:
        # ISBN, 책 제목, 저자, 출판사, 출판년도, 등록 날짜 유효성 검사
        is_valid, error_message = self.check_isbn_validate(str(book.isbn))
        if not is_valid:
            return False, f"ISBN 에러: {error_message}"
        
        is_valid, error_message = self.check_string_validate("제목", book.title)
        if not is_valid:
            return False, f"제목 에러: {error_message}"
        
        is_valid, error_message = self.check_string_validate("저자", book.author)
        if not is_valid:
            return False, f"저자 에러: {error_message}"
        
        is_valid, error_message = self.check_string_validate("출판사", book.publisher)
        if not is_valid:
            return False, f"출판사 에러: {error_message}"
        
        is_valid, error_message = self.check_year_validate(str(book.published_year))
        if not is_valid:
            return False, f"출판년도 에러: {error_message}"
        
        is_valid, error_message = self.check_date_validate(str(book.register_date))
        if not is_valid:
            return False, f"등록 날짜 에러: {error_message}"

         # 대출 중인 경우 대출자 이름, 대출자 전화번호, 대출 날짜, 반납 예정일에 대한 추가 유효성 검사
        if book.is_borrowing:

            is_valid, error_message = self.check_string_validate("대출자", book.borrower_name)
            if not is_valid:
                return False, f"대출자 에러: {error_message}"
        
            is_valid, error_message = self.check_phone_number_validate(book.borrower_phone_number)
            if not is_valid:
                return False, f"전화번호 에러: {error_message}"
        
            is_valid, error_message = self.check_date_validate(str(book.borrow_date))
            if not is_valid:
                return False, f"대출 날짜 에러: {error_message}"
        
            is_valid, error_message = self.check_date_validate(str(book.return_date))
            if not is_valid:
                return False, f"반납 예정일 에러: {error_message}"
        else:
            # 대출자 정보가 없는 경우 대출 관련 필드가 비어있는지 확인
            if book.borrower_name or book.borrower_phone_number or book.borrow_date or book.return_date:
                return False, "대출 중이 아닌 도서에 대출 정보가 있습니다."

        return True, ""

    def check_overdue_delete(self, book_id):
        for book in self.book_data:
            if book.book_id == book_id and book.return_date:
                return True
        return False

    # ========== 1. 추가 ========== #
    def add_book(self):
        pass
    
    # ========== 2. 삭제 ========== #
    def delete_book(self):
        pass
    
    # ========== 3. 수정 ========== #
    def update_book(self):
        pass
    
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
        pass
    
    # ========== 6. 반납 ========== #
    def return_book(self):
        pass
    
    # ========== 7. 설정 ========== #
    def setting(self):
        pass
    
    # ========== 8. 연혁(로그) 조회 ========== #
    def history(self):
        pass
    
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

    def input_author(self, input_message: str) -> str:
        author = input(input_message)
    
        if not author:  # 입력값이 비어있는 경우
            print("ERROR: 책의 저자는 1글자 이상이어야 합니다.")
            return None
        
        author = author.strip()  # 앞뒤 공백 제거
        
        if not author:  # 공백을 제거한 후 비어있는 경우
            print("ERROR: 책의 저자는 공백일 수 없습니다.")
            return None
        
        is_valid, error_message = self.check_string_validate("저자", author)
        if is_valid:
            return author
        else:
            print(f"ERROR: {error_message}")
            return None

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
        
        if book_id.strip() == CANCEL:
            return CANCEL
    
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
            assert 0 < slc < 9, "원하는 동작에 해당하는 번호(숫자)만 입력해주세요."
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
            bookData.setting()
            
        # 연혁(로그) 조회
        if slc == 8:
            bookData.history()
    
        if slc == 9:
            bookData.return_book()

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
        
        # 연도가 1513보다 작은지 검사
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
