from sqlalchemy import Column, String, Integer, Date, Time, DateTime, Text, TIMESTAMP, Float
from database import Base

# 1. 사원 정보 테이블
class Employee(Base):
    __tablename__ = 'employees'

    # 사원 ID (Primary Key)
    employee_id = Column(String(50), primary_key=True)
    
    # 사원 이름
    name = Column(String(100), nullable=False)
    
    # [핵심] 로그인 에러 해결을 위한 비밀번호 컬럼 (필수!)
    password = Column(String(255), nullable=False)

    # 마이페이지 및 상세 정보
    department = Column(String(50), nullable=True)   # 부서
    position = Column(String(50), nullable=True)     # 직급
    email = Column(String(100), nullable=True)       # 이메일
    phone_number = Column(String(50), nullable=True) # 전화번호
    hire_date = Column(Date, nullable=True)          # 입사일
    status = Column(String(20), default="재직")      # 재직 상태
    
    # 연차 개수 (반차 계산을 위해 소수점 허용)
    total_leave_days = Column(Float, default=15.0)


# 2. 출퇴근 기록 테이블
class Attendance(Base):
    __tablename__ = 'attendance'

    # 출퇴근 기록 ID
    attendance_id = Column(String(50), primary_key=True)
    
    # 사원 ID
    employee_id = Column(String(50))
    
    # 날짜
    attendance_date = Column(Date)
    
    # 시간
    attendance_in_time = Column(Time, nullable=True)
    attendance_out_time = Column(Time, nullable=True)
    
    # 장소
    attendance_in_location = Column(String(100), nullable=True)
    attendance_out_location = Column(String(100), nullable=True)
    
    # 방식
    attendance_method = Column(String(50), nullable=True)


# 3. 신청서 테이블 (휴가/외출 등)
class ApplicationModel(Base):
    __tablename__ = 'applications'

    # 신청서 ID
    application_id = Column(String(50), primary_key=True)
    
    # 사원 ID
    employee_id = Column(String(50))
    
    # 신청 유형
    application_type = Column(String(50), nullable=False)
    
    # 기간
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    
    # 사유
    reason = Column(Text, nullable=True)
    
    # 상태 (대기/승인/반려)
    status = Column(String(50), default="대기")
    
    # 작성 시간
    created_at = Column(TIMESTAMP)