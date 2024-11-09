import os
import datetime
import re

""" GLOBAL CONSTANTS """
CANCEL = "X"
BORROW_DATE = 7

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


class BookRecord(object):
    def __init__(self, book_id: int, 
                 isbn: int, title: str, 
                 author: str, publisher: str, 
                 published_year: int, register_date: MyDate,
                 borrower_name: str=None, 
                 borrower_phone_number: str=None,
                 borrow_date: MyDate=None,
                 return_date: MyDate=None):
        
        self.book_id = book_id
        self.isbn = isbn
        self.title = title
        self.author = author
        self.publisher = publisher
        self.published_year = published_year
        self.register_date = register_date
        self.borrower_name = borrower_name
        self.borrower_phone_number = borrower_phone_number
        self.borrow_date = borrow_date
        self.return_date = return_date
        
        self.is_borrowing: bool = borrower_name is not None
        
    def __str__(self) -> str:
        isbn_str = str(self.isbn).zfill(2)
        return f"{self.book_id} / {isbn_str} / {self.title} \
/ {self.author} / {self.publisher} \
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
        isbn_str = str(self.isbn).zfill(2)
        
        return f"{self.book_id} / {isbn_str} \
/ {self.title} / {self.author} \
/ {self.publisher} / {self.published_year} \
/ {str(self.register_date)}" \
+ (f" / {self.borrower_phone_number} {self.borrower_name} \
/ {str(self.borrow_date)} ~ {str(self.return_date)}" if self.is_borrowing and contain_borrow else "") \
+ (" *" if self.return_date < today else "")

    def to_record_str(self) -> str:
        isbn_str = str(self.isbn).zfill(2)
        return f"{self.book_id}/{isbn_str}\
/{self.title}/{self.author}\
/{self.publisher}/{self.published_year}\
/{str(self.register_date)}" \
+ (f"/{self.borrower_name}/{self.borrower_phone_number}\
/{str(self.borrow_date)}/{str(self.return_date)}" if self.is_borrowing else "////") 

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
    def __init__(self, file_path):
        self.file_path = file_path
        self.today: MyDate = None
        # 파일 읽어서 book_data 리스트 생성 (임시)
        self.book_data = []
        # 파일 읽어서 가장 큰 ID 저장
        self.static_id = 0
        
        # constant
        self.MAX_STATIC_ID = 99

    def set_today(self, today: MyDate):
        self.today = today

    # 파일 읽기
    def read_data_file(self):
        """
        데이터 파일 읽음
        """
        
        # 1. 경로에 데이터 파일 존재 여부 확인        
        if not os.path.isfile(self.file_path):
            # 1-1 파일이 존재하지 않는 경우 빈 파일 생성
            with open(self.file_path, "wb") as f:
                f.write(b"0\r\n")
            
            # 1-2. 최대 고유번호 0 설정
            self.book_data = []
            self.static_id = 0
            
            # print("1. 파일이 존재하지 않아 생성")
            
            # 1-3. 종료
            return
        
        # 2. 파일이 비어있는지 검사
        if os.stat(self.file_path).st_size == 0:
            # 2-1. 빈 파일 생성
            with open(self.file_path, "wb") as f:
                f.write(b"0\r\n")
                
            # 1-2. 최대 고유번호 0 설정
            self.book_data = []
            self.static_id = 0
            
            # print("2. 파일이 비어있어 생성")
            
            # 2-3. 종료
            return
        
        # 3. CRLF인지 확인
        with open(self.file_path, "rb") as f:
            content = f.read()
            
            crlf_flag = False
            
            if b"\r\n" in content:
                # print("CRLF")
                crlf_flag = True
            else:
                # print("NO CRLF")
                pass
        
        if not crlf_flag:
            # 3-1. 빈 파일 생성
            with open(self.file_path, "wb") as f:
                f.write(b"0\r\n")
                
            # 3-2. 최대 고유번호 0 설정
            self.book_data = []
            self.static_id = 0
            
            # print("3. 파일이 CRLF가 아니므로 삭제 후 생성")
            
            # 3-3. 종료
            return
        
        # 4. 무결성 검사 실행
        checked = self.check_data_file()
        
        # 4-1. 무결성 확인되면 계속 진행
        if checked:
            pass
        
        # 4-2. 무결성 깨지면 기존 파일을 삭제
        else:
            # 4-2. 기존 파일 삭제
            os.remove(self.file_path)

            # 추후 백업 기능
            # 새로운 파일 이름 생성
            # current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            # new_file_name = f"{self.file_path[:-4]}_{current_time}.txt"
            
            # 파일명 변경
            # os.rename(self.file_path, new_file_name)
            
            # 4-3. 새 파일 생성, 0 기입
            with open(self.file_path, "wb") as f:
                f.write(b"0\r\n")
            
            self.book_data = []
            self.static_id = 0
            
            # print("4. 무결성이 깨져서 기존 파일 삭제")
            
            return   
        
        # print("5. 무결성 검사 완료, 파일 읽기 시작")
        
        # 파일 읽기 시작 (무결성 검증 이후)
        book_records = []
        
        with open(self.file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            
            # 4. static id 읽어서 저장
            self.static_id = int(lines[0].strip())
            
            # 5. 
            for line in lines[1:]:
                data = line.strip().split("/")
                
                book_id = int(data[0])
                isbn = int(data[1])
                title = data[2]
                author = data[3]
                publisher = data[4]
                published_year = int(data[5])
                register_date = MyDate.from_str(data[6])
                
                borrower_name = data[7] if len(data[7]) > 0 else None
                borrower_phone_number = data[8] if len(data[7]) > 0 else None
                borrow_date = MyDate.from_str(data[9]) if len(data[7]) > 0 else None
                return_date = MyDate.from_str(data[10]) if len(data[7]) > 0 else None
                
                book_record = BookRecord(
                    book_id, isbn, title, author, publisher, published_year,
                    register_date, borrower_name, borrower_phone_number,
                    borrow_date, return_date
                )
                
                book_records.append(book_record)
                
            self.book_data = book_records
    
    # 파일에 기반한 현재 날짜 검사
    def check_today_by_data(self, today: MyDate) -> tuple[bool, str]:
        for record in self.book_data:
            # 1. 등록일과 비교
            if record.register_date > today:
                return (False, "가장 최근에 저장된 책의 등록날짜 또는 대출날짜보다 과거의 날짜입니다.")
                
            # 2. 출판년도는 현재 날짜보다 미래일 수 없음 (무결성검사에서 검사해서 여기서 오류나면 안됨)
            if record.published_year > today.year:
                print("여기서 오류가 난다는 것은 출판년도보다 등록일이 과거라는 의미임")
                return (False, "critical error is occured")
            
            # 3. 대출 날짜와 비교
            if record.borrow_date is not None and record.borrow_date > today:
                return (False, "가장 최근에 저장된 책의 등록날짜 또는 대출날짜보다 과거의 날짜입니다.")
        
        return (True, None)
    
    # 파일 무결성 검사
    def check_data_file(self, verbose=False):
        """
        파일 무결성 검사
        """
        
        with open(self.file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            
        # 1. 첫 줄 검사 (파일이 비어있지 않으므로 첫 줄은 반드시 존재)
        first_line = lines[0].strip()
        
        try:
            # 정수 변환 가능한지
            static_id = int(first_line)
            
            # 범위 검사
            assert 0 <= static_id <= self.MAX_STATIC_ID
            
        except ValueError:
            # 정수 변환 불가
            if verbose: print("1 첫 줄 정수 변환 불가")
            return False
        except AssertionError:
            # 범위 벗어남
            if verbose: print("1 첫 줄 범위 벗어남")
            return False
        
        # 2 구분자가 10개인지 검사
        sep_list = list(map(lambda x : x.split("/"), lines[1:]))
        if not all(len(rec) == 11 for rec in sep_list): 
            if verbose: print("2 구분자가 10개가 아님")
            return False
        
        # 3, 4 모든 레코드의 앞 7개 항목 비어있지 않는지 모두 가지는지 검사
        if not all(all(len(item.strip()) > 0 for item in rec[:7]) for rec in sep_list):
            if verbose: print("3, 4. 모든 레코드의 앞 7개 항목 중 빈 값 존재")
            return False
        
        # 7. 고유번호 검사
        first_elements = [rec[0] for rec in sep_list]
        
        # 모두 정수인지 검사
        if not all(x.isdigit() for x in first_elements):
            if verbose: print("7 고유번호가 정수가 아님")
            return False
        
        # 모두 정수로 변환 가능
        first_elements = list(map(int, first_elements))
        
        # 범위 검사
        if not all(0 <= x <= static_id for x in first_elements):
            if verbose: print("7 고유번호 범위 벗어남")
            return False
        
        # 8. 고유번호 중복 검사
        if len(first_elements) > len(set(first_elements)):
            if verbose: print("8 고유번호 중복")
            return False
        
        # 9. ISBN 검사
        second_elements = [rec[1] for rec in sep_list]
        
        # 길이 2이며, 정수로 변환 가능
        if not all(len(x) == 2 and x.isdigit() for x in second_elements):
            if verbose: print("9 ISBN 길이")
            return False
        
        # 10. 3-5번째 제목, 저자, 출판사 (빈 문자열은 아님)
        for rec in sep_list:
            if any(map(lambda x: "/" in x or "\\" in x, rec[2:5])) or any(map(lambda x: x.strip() == "X", rec[2:5])):
                if verbose: print("3 ~ 5 잘못된 문자열")
                return False
            
        # 11. 출판년도
        sixth_elements = [rec[5] for rec in sep_list]
        
        if not all(len(x) == 4 and x.isdigit() for x in sixth_elements):
            if verbose: print("11 잘못된 출판년도")
            return False
        
        sixth_elements = list(map(int, sixth_elements))
        if not all(1583 <= x <= 9999 for x in sixth_elements):
            if verbose: print("11 년도 범위 잘못됨")
            return False
        
        # 12. 등록 날짜 검사
        for rec in sep_list:
            if MyDate.from_str(rec[6]) is None:
                if verbose: print("12 등록 날짜 잘못됨")
                return False
            
        # 13. 대출 데이터 검사
        for rec in sep_list:
            # 4개 값이 모두 빈 값이거나, 4개 값이 모두 빈 값이 아니어야 함
            if not (all(len(rec[i].strip()) == 0 for i in range(7, 11)) or all(len(rec[i].strip()) > 0 for i in range(7, 11))):
                if verbose: print("13 대출 데이터 모두 빈 값이거나, 모두 값이 있지 않음")
                return False
           
        for rec in sep_list:
            # 대출 데이터가 없다면 패스 
            if len(rec[7]) > 0:
                # 14. 대출자 이름 (전화번호도 함께 검사)
                if any(map(lambda x: "/" in x or "\\" in x, rec[7:9])) or any(map(lambda x: x.strip() == "X", rec[7:9])):
                    if verbose: print("14 대출자 이름, 전화번호 잘못됨")
                    return False
                
                # 15 전화번호
                phone_number_pattern = re.compile(r'^010-\d{4}-\d{4}$')
                if not phone_number_pattern.match(rec[8]):
                    if verbose: print("15 전화번호 잘못됨")
                    return False
                
                # 16, 17 대출날짜, 반납예정날짜 검사
                borrow_date = MyDate.from_str(rec[9])
                return_date = MyDate.from_str(rec[10])
                reg_date = MyDate.from_str(rec[6])
                
                if borrow_date is None or return_date is None:
                    if verbose: print("16, 17 대출 반납 날짜 잘못됨")
                    return False
                
                # 17. 반납 예정일은 7일 후여야 함
                if borrow_date + BORROW_DATE != return_date:
                    if verbose: print("반납 예정일이 7일 후가 아님")
                    return False
            
                # 18. 등록 날짜와 대출 날짜 비교
                if reg_date > borrow_date:
                    if verbose: print("18 등록 날짜가 대출 날짜보다 미래임")
                    return False
            
            # 20. 등록 날짜와 출판 년도 검사
            reg_year = MyDate.from_str(rec[6]).year
            pub_year = int(rec[5])
            
            if reg_year < pub_year:
                return False
            
        # 24. ISBN이 같은데 다른 데이터 검사
        for i in range(len(sep_list)):
            book_isbn = int(sep_list[i][1])
            
            for j in range(i + 1, len(sep_list)):
                if (book_isbn == int(sep_list[j][1])):
                    # ISBN이 같으면 제목(2) 저자(3) 출판사(4) 출판년도(5)가 같아야 함
                    for k in range(2, 6):
                        if sep_list[i][k].strip() != sep_list[j][k].strip():
                            if verbose: print(f"24 ISBN 같은데 데이터 다름 {i} and {j} - {k}")
                            return False
        
        return True
    
    # 데이터 무결성 검사
    def check_data_integrity(self) -> tuple[bool, str]:
        # 데이터 무결성 검사를 수행하고 결과를 반환
        for book in self.book_data:
            is_valid, message = self.check_record_validate(book)
            if not is_valid:
                return (False, f"도서 '{book.title}'의 무결성 오류: {message}")
        return (True, None)

    ## 인자 얻는 함수
    def get_data(self):
        return self.book_data

    def get_static_id(self):
        return self.static_id
    
    ## Full 상태 체크
    def isFull(self) -> bool:
        if self.static_id > self.MAX_STATIC_ID:
            return True
        else:
            return False
        
    ## Search
    def search_isbn(self, isbn: int) -> list:
        matching_books = [book for book in self.book_data if book.isbn == isbn]
        return matching_books
    
    def search_id(self, book_id):
        if book_id == CANCEL:
            return None
        if isinstance(book_id, str):
            if book_id.isdigit():
                book_id = int(book_id)
            else:
                return None
        matching_book = next((book for book in self.book_data if book.book_id == book_id), None)
        return matching_book

    ## id 증가 함수
    def increase_static_id(self) -> bool:
        if self.isFull():
            return False
        else:
            self.static_id += 1
            return True

    # 메인에서 실행 될 함수들
    # 1. 추가
    # 2. 삭제
    # 3. 수정
    # 4. 검색
    # 5. 대출
    # 6. 반납
    # 7. 종료

    """ 1. 추가 """
    def add_book(self) -> bool:
        if bookData.isFull():
            print("더 이상 추가할 수 없습니다.")
            return False
        
        isbn = self.input_isbn("추가할 책의 ISBN을 입력하세요: ")
        if not isbn:
            return False

        if isbn == CANCEL:
            print("추가를 중단하며 메인 프롬프트로 돌아갑니다.")
            return False

        isbn = int(isbn)
        
        book_info = []
        books = bookData.search_isbn(isbn)
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

                if info == CANCEL:
                    print("추가를 중단하며 메인 프롬프트로 돌아갑니다.")
                    return False
                    
                book_info.append(info)
        else:
            print(f"ISBN이 {isbn}인 책이 이미 {len(books)}권이 있습니다.")
            book_info = str(books[0]).split(" / ")
            book_info = book_info[2:6]

        print(BookRecord.get_header())
        print()
        if books:
            for book in books:
                print(book.to_str(today=self.today, contain_borrow=True))
            print()
            print("여기에")
            print()

        book_record = BookRecord(
            bookData.get_static_id(), isbn, book_info[0], book_info[1], book_info[2], int(book_info[3]), today
        )

        print(book_record)
        print()
        if self.input_response("해당 책을 추가하시겠습니까?(Y/N): "):
            bookData.insert_record(book_record)
            self.save_data_to_file()
            return True
        else:
            print("추가를 중단하며 메인 프롬프트로 돌아갑니다.")
            return False
        
    # 데이터 삽입 인터페이스
    def insert_record(self, BookRecord):
        self.book_data.append(BookRecord)
        self.increase_static_id()
        print("성공적으로 책을 추가하였습니다.")

    """ 2. 삭제 """
    def delete_book(self):
        del_book_id = self.input_book_id("삭제할 책의 고유번호를 입력해주세요: ", 1)

        if (del_book_id==None):
            return False
        
        if del_book_id == CANCEL:
            print("삭제를 중단하며 메인 프롬프트로 돌아갑니다.")
            return False

        del_book_id = int(del_book_id)

        if self.check_overdue_delete(del_book_id):
            print("ERROR: 해당 책은 대출중이므로 삭제할 수 없습니다.")
            return False
        else:
            print("책이 특정되었습니다.")
            del_book_data = self.search_id(del_book_id)
            print(BookRecord.get_header(contain_borrow_info=False))
            print()
            print(del_book_data.to_str(self.today, contain_borrow=False))
            print()

            if self.confirm_delete(del_book_data):
                self.save_data_to_file()
                return True
            else:
                return False
            
    def confirm_delete(self, del_book_data):
        if self.input_response("삭제하면 되돌릴 수 없습니다. 정말로 삭제하시겠습니까?(Y/N): "):
            self.book_data.remove(del_book_data)
            print("삭제가 완료되었습니다. 메인프롬프트로 돌아갑니다.")
            return True
        else:
            print("삭제를 취소하였습니다. 메인프롬프트로 돌아갑니다.")
            return False

    """ 3. 수정 (업데이트) """
    def update_book(self) -> bool:
        try:
            isbn = self.input_isbn("수정할 책의 ISBN을 입력해주세요: ")
            if not isbn:
                return False  # 입력 실패 시 반환

            if isbn == CANCEL:
                print("수정을 중단하며 메인 프롬프트로 돌아갑니다.")
                return False

            isbn = int(isbn)

            # 책 존재 여부 확인
            books = self.search_isbn(isbn)

            if not books:
                print("ERROR: 해당 ISBN을 가진 책이 존재하지 않습니다.")
                return False
            else:
                print(f"ISBN이 {isbn}인 책 데이터가 {len(books)}권 있습니다.")
                print()

            # 기존 책 정보 출력
            print(BookRecord.get_header(contain_borrow_info=False))
            print()
            for book in books:
                print(book.to_str(today=self.today, contain_borrow=False))

            # 새로운 정보 입력
            new_title = self.input_bookName("책의 수정될 제목을 입력해주세요: ")
            if not new_title:
                return False

            if new_title == CANCEL:
                print("수정을 중단하며 메인 프롬프트로 돌아갑니다.")
                return False

            new_author = self.input_author("책의 수정될 저자를 입력해주세요: ")
            if not new_author:
                return False

            if new_author == CANCEL:
                print("수정을 중단하며 메인 프롬프트로 돌아갑니다.")
                return False

            new_publisher = self.input_publisher("책의 수정될 출판사를 입력해주세요: ")
            if not new_publisher:
                return False

            if new_publisher == CANCEL:
                print("수정을 중단하며 메인 프롬프트로 돌아갑니다.")
                return False
                
            new_year = self.input_year("책의 수정될 출판년도를 입력해주세요: ")
            if not new_year:
                return False

            if new_year == CANCEL:
                print("수정을 중단하며 메인 프롬프트로 돌아갑니다.")
                return False

            new_year = int(new_year)

            # 수정 여부 확인
            if not self.input_response("수정한 데이터는 복구할 수 없습니다. 정말로 수정하시겠습니까?(Y/N): "):
                print("수정을 취소하였습니다. 메인 프롬프트로 돌아갑니다.")
                return False

            # 수정 반영
            for book in books:
                book.title = new_title
                book.author = new_author
                book.publisher = new_publisher
                book.published_year = new_year

            print("수정이 완료되었습니다.")
            self.save_data_to_file()
            return True

        except Exception as e:
            print(f"ERROR: 예상하지 못한 오류가 발생했습니다. {str(e)}")
            return False
    
    """ 4. 검색 """
    def search_book(self):
        if not self.book_data:
            print("등록된 책이 존재하지 않습니다.")
            return False

        search_book = input("검색할 책의 제목 또는 저자를 입력하세요: ").strip()

        if search_book == CANCEL:
            print("검색을 중단하며 메인 프롬프트로 돌아갑니다.")
            return False
        
        if len(search_book) == 0:
            bookData.print_book_debug()
            return True

        is_valid, error_message = self.check_string_validate("제목 또는 저자", search_book)
        if not is_valid:
            print(f"ERROR: {error_message}")
            return False
        
        bookData.search_content_book(search_book)

    def search_content_book(self, search_book):
        search_results = [
            book for book in self.book_data 
            if search_book in book.title or search_book in book.author
        ]

        if not search_results:
            
            if self.input_response("해당 책이 존재하지 않습니다. 다시 검색하시겠습니까?(Y/N): "):
                self.search_book()
            else:
                print("검색을 중단하며 메인 프롬프트로 돌아갑니다.")
                return False
        

        print(BookRecord.get_header())
        print()
        for book in search_results:
            print(book.to_str(today=self.today, contain_borrow=True))
        print()
        return True

    """ 5. 책 대출 """
    def borrow_book(self):

        name = self.input_borrower_name()
        if not name:
            return False

        if name == CANCEL:
            print("대출이 취소되었습니다. 메인 프롬프트로 돌아갑니다.")
            return False
        
        phone = self.input_phone_number()
        if not phone:
            return False

        if phone == CANCEL:
            print("대출이 취소되었습니다. 메인 프롬프트로 돌아갑니다.")
            return False
        
        overdue_books = self.check_overdue_books(name, phone)
        if overdue_books:
            print("연체중인 책을 보유하고 있어 대출이 불가능합니다.")
            print("아래 목록은 대출자가 현재 연체중인 책입니다.")
            print(BookRecord.get_header(contain_borrow_info=True))
            print()
            for book in overdue_books:
                print(book.to_str(self.today, contain_borrow=True))
            return False

        borrowed_count = self.count_borrowed_books(name, phone)
        max_limit = 3
        if borrowed_count >= max_limit:
            print(f"대출 중인 책이 {borrowed_count}권 있으며 더 이상 대출이 불가능합니다.")
            print(BookRecord.get_header(contain_borrow_info=True))
            print()
            for book in self.book_data:
                if book.borrower_name == name and book.borrower_phone_number == phone:
                    print(book.to_str(self.today, contain_borrow=True))
            return False 
        else:
            print(f"대출중인 책이 {borrowed_count}권 있으며, {max_limit - borrowed_count}권 대출이 가능합니다.")

        book_id = self.input_book_id("대출할 책의 고유번호를 입력해주세요: ", 1)
        
        if (book_id==None):
            return False
        
        if book_id == CANCEL:
            print("대출이 취소되었습니다. 메인 프롬프트로 돌아갑니다.")
            return False

        book_id = int(book_id)

        book = self.search_id(book_id)
        print("책이 특정되었습니다.")
        print(BookRecord.get_header(contain_borrow_info=False))
        print()
        print(book.to_str(self.today, contain_borrow=False)) 
        
        if book.borrower_name:
            print("이미 다른 사용자에 의해 대출 중이므로 대출이 불가능합니다.")
            return False

        if self.input_response("위 책을 대출할까요? (Y/N): "):
            borrow_date = self.today
            due_date = self.today + BORROW_DATE
            book.is_borrowing = True
            book.borrower_name = name
            book.borrower_phone_number = phone
            book.borrow_date = borrow_date
            book.return_date = due_date
            print(f"대출이 완료되었습니다. 반납 예정일은 {due_date} 입니다.")
            self.save_data_to_file()
            return True
        else:
            print("대출이 취소되었습니다. 메인 프롬프트로 돌아갑니다.")
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
    
    """ 6. 책 반납 """
    def return_book(self) -> bool:
        try:
            rtn_book_id = self.input_book_id("반납할 책의 고유번호를 입력해주세요: ", 1)

            if (rtn_book_id==None):
                return False  # 입력 실패 시 반환

            if rtn_book_id == CANCEL:
                print("반납을 취소했습니다. 메인 프롬프트로 돌아갑니다.")
                return False

            rtn_book_id = int(rtn_book_id)
            
            # 고유번호에 해당하는 책 존재 여부 확인
            book_to_return = self.search_id(rtn_book_id)

            if not book_to_return:
                print()
                return False

            # 대출 여부 확인
            if not book_to_return.is_borrowing:
                print("ERROR: 현재 대출 중인 책이 아닙니다.")
                return False

            # 책 정보 및 대출자 정보 출력
            print(f"{book_to_return.book_id} / {book_to_return.isbn} / {book_to_return.title} / {book_to_return.author} / {book_to_return.publisher} / {book_to_return.published_year} / {book_to_return.register_date}")
            print(f"대출자: {book_to_return.borrower_name} {book_to_return.borrower_phone_number} / 대출일: {book_to_return.borrow_date}")

            # 반납 여부 확인
            if not self.input_response("위 책을 반납할까요? (Y/N): "):
                print("반납을 취소했습니다. 메인 프롬프트로 돌아갑니다.")
                return False

            # 반납 처리
            book_to_return.is_borrowing = False
            book_to_return.borrower_name = None
            book_to_return.borrower_phone_number = None
            book_to_return.borrow_date = None
            book_to_return.return_date = None

            print("반납이 완료되었습니다.")
            self.save_data_to_file()  # 데이터 파일에 변경사항 저장
            return True

        except Exception as e:
            print(f"ERROR: 예상하지 못한 오류가 발생했습니다. {str(e)}")
            return False

    """ 검사 함수 """
    def check_book_id_validate(self, book_id, flag): # flag == 0 -> 있으면 False 없으면 True, flag == 1 -> 없으면 False 있으면 True
        if book_id == CANCEL:
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
        if value == CANCEL:
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
        if year == CANCEL:
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
        if isbn == CANCEL:
            return True, ""
        # ISBN이 공백인지 확인
        if not isbn.strip():  # 공백을 제거한 후 빈 문자열인지 확인
            return False, "책의 ISBN은 공백일 수 없습니다."
        # ISBN이 두 자리 숫자(00~99)로 구성되어 있는지 확인
        if len(isbn) != 2 or not isbn.isdigit():
            return False, "ISBN은 두 자리 숫자여야 합니다."
        return True, ""

    def check_phone_number_validate(self, phone_number):
        if phone_number == CANCEL:
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

    def save_data_to_file(self) -> None:
        """파일에 현재 book_data 리스트를 저장합니다."""
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                # 첫 줄에 static_id 저장
                f.write(f"{self.static_id}\n")

                # 각 BookRecord 객체를 파일에 저장
                for book in self.book_data:
                    f.write(f"{book.book_id}/{book.isbn}/{book.title}/{book.author}/{book.publisher}/"
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
        print()
        for book in self.book_data:
            print(book.to_str(today=self.today, contain_borrow=True))
        print("="*30)

    """ input 함수 """
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


""" main prompt """
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

    print("프로그램을 종료합니다.")


""" 현재 날짜 입력 """
def input_date(bookData: BookData):
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


""" main """
if __name__ == "__main__":
    bookData = BookData(file_path="./Libsystem_data.txt")
    
    # 데이터 파일 읽기
    bookData.read_data_file()
    
    # 현재 날짜 입력
    today = input_date(bookData)
    bookData.set_today(today)

    # 디버깅용 함수 주석 처리
    # bookData.print_book_debug()
    
    main_prompt(bookData=bookData)
