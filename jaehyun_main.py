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

    def to_record_str(self) -> str:
        return f"{self.book_id}/{self.isbn}\
/{self.title}/{self.writer}\
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
        
        # 1. 경로에 데이터 파일 존재 여부 확인        
        if not os.path.isfile(self.file_path):
            # 1-1 파일이 존재하지 않는 경우 빈 파일 생성
            with open(self.file_path, "w", encoding="utf-8") as f:
                # 1-2. 파일에 0 기입,
                f.write("0")
            
            # 1-2. 최대 고유번호 0 설정
            self.book_data = []
            self.static_id = 0
            
            print("1. 파일이 존재하지 않아 생성")
            
            # 1-3. 종료
            return
        
        # 2. 파일이 비어있는지 검사
        if os.stat(self.file_path).st_size == 0:
            # 2-1. 빈 파일 생성
            with open(self.file_path, "w", encoding="utf-8") as f:
                # 2-2 파일에 0 기입,
                f.write("0")
                
            # 1-2. 최대 고유번호 0 설정
            self.book_data = []
            self.static_id = 0
            
            print("2. 파일이 비어있어 생성")
            
            # 2-3. 종료
            return
        
        # 3. 무결성 검사 실행
        checked = self.check_data_file()
        
        # 3-1. 무결성 확인되면 계속 진행
        if checked:
            pass
        
        # 3-2. 무결성 깨지면 기존 파일을 삭제
        else:
            # 3-2. 기존 파일 삭제
            os.remove(self.file_path)

            # 추후 백업 기능
            # 새로운 파일 이름 생성
            # current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            # new_file_name = f"{self.file_path[:-4]}_{current_time}.txt"
            
            # 파일명 변경
            # os.rename(self.file_path, new_file_name)
            
            # 3-3. 새 파일 생성, 0 기입
            with open(self.file_path, "w", encoding="utf-8") as f:
                f.write("0")
            
            self.book_data = []
            self.static_id = 0
            
            print("3. 무결성이 깨져서 기존 파일 삭제")
            
            return   
        
        print("4. 무결성 검사 완료, 파일 읽기 시작")
        
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
            print("1 첫 줄 정수 변환 불가")
            return False
        except AssertionError:
            # 범위 벗어남
            print("1 첫 줄 범위 벗어남")
            return False
        
        # 2 구분자가 10개인지 검사
        sep_list = list(map(lambda x : x.split("/"), lines[1:]))
        if not all(len(rec) == 11 for rec in sep_list): 
            print("2 구분자가 10개가 아님")
            return False
        
        # 3, 4 모든 레코드의 앞 7개 항목 비어있지 않는지 모두 가지는지 검사
        if not all(all(len(item.strip()) > 0 for item in rec[:7]) for rec in sep_list):
            print("3, 4. 모든 레코드의 앞 7개 항목 중 빈 값 존재")
            return False
        
        # 7. 고유번호 검사
        first_elements = [rec[0] for rec in sep_list]
        
        # 모두 정수인지 검사
        if not all(x.isdigit() for x in first_elements):
            print("7 고유번호가 정수가 아님")
            return False
        
        # 모두 정수로 변환 가능
        first_elements = list(map(int, first_elements))
        
        # 범위 검사
        if not all(0 <= x <= static_id for x in first_elements):
            print("7 고유번호 범위 벗어남")
            return False
        
        # 8. 고유번호 중복 검사
        if len(first_elements) > len(set(first_elements)):
            print("8 고유번호 중복")
            return False
        
        # 9. ISBN 검사
        second_elements = [rec[1] for rec in sep_list]
        
        # 길이 2이며, 정수로 변환 가능
        if not all(len(x) == 2 and x.isdigit() for x in second_elements):
            print("9 ISBN 길이")
            return False
        
        # 10. 3-5번째 제목, 저자, 출판사 (빈 문자열은 아님)
        for rec in sep_list:
            if any(map(lambda x: "/" in x or "\\" in x, rec[2:5])) or any(map(lambda x: x.strip() == "X", rec[2:5])):
                print("3 ~ 5 잘못된 문자열")
                return False
            
        # 11. 출판년도
        sixth_elements = [rec[5] for rec in sep_list]
        
        if not all(len(x) == 4 and x.isdigit() for x in sixth_elements):
            print("11 잘못된 출판년도")
            return False
        
        sixth_elements = list(map(int, sixth_elements))
        if not all(1583 <= x <= self.today.year for x in sixth_elements):
            print("11 년도 범위 잘못됨")
            return False
        
        # 12. 등록 날짜 검사
        for rec in sep_list:
            if MyDate.from_str(rec[6]) is None:
                print("12 등록 날짜 잘못됨")
                return False
            
        # 13. 대출 데이터 검사
        for rec in sep_list:
            # 4개 값이 모두 빈 값이거나, 4개 값이 모두 빈 값이 아니어야 함
            if not (all(len(rec[i].strip()) == 0 for i in range(7, 11)) or all(len(rec[i].strip()) > 0 for i in range(7, 11))):
                print("13 대출 데이터 모두 빈 값이거나, 모두 값이 있지 않음")
                return False
           
        for rec in sep_list:
            # 대출 데이터가 없다면 패스 
            if len(rec[7]) > 0:
                # 14. 대출자 이름 (전화번호도 함께 검사)
                if any(map(lambda x: "/" in x or "\\" in x, rec[7:9])) or any(map(lambda x: x.strip() == "X", rec[7:9])):
                    print("14 대출자 이름, 전화번호 잘못됨")
                    return False
                
                # 15 전화번호
                phone_number_pattern = re.compile(r'^010-\d{4}-\d{4}$')
                if not phone_number_pattern.match(rec[8]):
                    print("15 전화번호 잘못됨")
                    return False
                
                # 16, 17 대출날짜, 반납예정날짜 검사
                borrow_date = MyDate.from_str(rec[9])
                return_date = MyDate.from_str(rec[10])
                reg_date = MyDate.from_str(rec[6])
                
                if borrow_date is None or return_date is None:
                    print("16, 17 대출 반납 날짜 잘못됨")
                    return False
                
                # 17. 반납 예정일은 7일 후여야 함
                if borrow_date + 7 != return_date:
                    print("반납 예정일이 7일 후가 아님")
                    return False
            
                # 18. 등록 날짜와 대출 날짜 비교
                if reg_date > borrow_date:
                    print("18 등록 날짜가 대출 날짜보다 미래임")
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
                            print(f"24 ISBN 같은데 데이터 다름 {i} and {j} - {k}")
                            return False
        
        return True

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

    def update_book(self):
        print("수정할 책의 ISBN을 입력해주세요: ", end="")
        try:
            # ISBN 입력 확인
            isbn = self.input_isbn()
            if not isbn:
                print("ISBN 입력에 실패하였습니다.")
                return False  # ISBN 입력 실패 시 반환

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
            print("\n수정할 책이 확인되었습니다.")
            print(book_to_update.to_str(today=self.today))

            # 새로운 정보 입력
            new_title = self.input_bookName()
            if new_title is None:
                print("제목 입력에 실패하였습니다.")
                return False

            new_author = self.input_author()
            if new_author is None:
                print("저자 입력에 실패하였습니다.")
                return False

            new_publisher = self.input_publisher()
            if new_publisher is None:
                print("출판사 입력에 실패하였습니다.")
                return False

            new_year = self.input_year()
            if new_year is None:
                print("출판년도 입력에 실패하였습니다.")
                return False

            # 수정 여부 확인
            print("\n수정한 데이터는 복구할 수 없습니다. 정말로 수정하시겠습니까? (Y/N): ", end="")
            confirm = input().strip()
            if confirm != "Y":
                print("수정을 취소하였습니다. 메인 프롬프트로 돌아갑니다.")
                return False

            # 수정 반영
            book_to_update.title = new_title
            book_to_update.writer = new_author
            book_to_update.publisher = new_publisher
            book_to_update.published_year = new_year

            print("수정이 완료되었습니다.")
            self.save_data_to_file()  # 변경된 데이터를 파일에 저장
            return True

        except Exception as e:
            print(f"ERROR: 예상하지 못한 오류가 발생했습니다. {str(e)}")
            return False


    def delete_book(self):
        print("삭제할", end=" ")
        del_book_id = self.input_book_id()

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
        if input_response("삭제하면 되돌릴 수 없습니다. 정말로 삭제하시겠습니까?(Y/N): "):
            self.book_data.remove(del_book_data)
            print("삭제가 완료되었습니다. 메인프롬프트로 돌아갑니다.")
            return True
        else:
            print("삭제를 취소하였습니다. 메인프롬프트로 돌아갑니다.")
            return False
    
    # 책 대출
    def borrow_book(self):

        name = self.input_borrower_name()
        
        phone = self.input_phone_number()

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

        print("대출할", end=" ")
        book_id = self.input_book_id()
        
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

        if input_response("위 책을 대출할까요? (Y/N): "):
            borrow_date = self.today
            due_date = self.today+7
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
    
    # 책 반납
    def return_book(self) -> tuple[bool, str]:
        return (True, None)

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
        return True, ""
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

    # 데이터 저장
    def save_data_to_file(self) -> tuple[bool, str]:
        """
        데이터를 파일에 쓰기
        """
        try:
            file_text = f"{self.static_id}\n"
            file_text += "\n".join(list(map(lambda x : x.to_record_str(), self.book_data)))
        except:
            return (False, "데이터 파일 변환 과정에서 오류 발생")
        
        try:        
            with open(self.file_path + "_temp", "w", encoding="utf-8") as f:
                f.write(file_text)
        except:
            return (False, "데이터 파일 저장 과정에서 오류 발생")
        
        return (True, "파일 저장 성공")
    
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
            bookData.delete_book()
            
        if slc == 3:
            bookData.update_book()
        
        if slc == 4:
            pass
            
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
