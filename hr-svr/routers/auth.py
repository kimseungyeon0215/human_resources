from datetime import datetime, timedelta
from typing import Union
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import JWTError, jwt
from pydantic import BaseModel

import database
import models

# --- 설정 (보안상 실제 배포 시에는 환경변수로 숨겨야 합니다) ---
SECRET_KEY = "my_super_secret_key_change_this"  # 임의의 긴 문자열로 변경하세요
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 
# --- 보안 도구 설정 ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

router = APIRouter()

# --- 토큰 응답 스키마 ---
class Token(BaseModel):
    access_token: str
    token_type: str

# 테스트 회원가입용 데이터 스키마
class UserCreate(BaseModel):
    employee_id: str
    password: str
    name: str

# --- 1. 비밀번호 관련 함수들 ---

def verify_password(plain_password, hashed_password):
    """입력받은 비밀번호와 DB의 암호화된 비밀번호가 일치하는지 확인"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """비밀번호를 암호화해서 리턴 (회원가입/초기화 때 사용)"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    """JWT 토큰 생성"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# --- 2. 로그인 API (토큰 발급) ---

@router.post("/login", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    # 1. DB에서 사용자 찾기 (form_data.username에는 사번(ID)이 들어옵니다)
    user = db.query(models.Employee).filter(models.Employee.employee_id == form_data.username).first()
    
    # 2. 사용자가 없거나 비밀번호가 틀리면 에러
    if not user or not user.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="아이디 또는 비밀번호가 일치하지 않습니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 3. 비밀번호 검증 (입력받은 것 vs DB에 있는 것)
    if not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="아이디 또는 비밀번호가 일치하지 않습니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 4. 인증 성공 시 토큰 생성
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.employee_id}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

# --- 테스트용 회원가입 API ---
@router.post("/signup-test")
def create_test_user(user: UserCreate, db: Session = Depends(database.get_db)):
    # 1. 이미 존재하는 ID인지 확인
    existing_user = db.query(models.Employee).filter(models.Employee.employee_id == user.employee_id).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="이미 존재하는 사번입니다.")

    # 2. 비밀번호 암호화
    hashed_password = get_password_hash(user.password)
    
    # 3. 유저 생성 (연차는 기본 15일 부여)
    new_user = models.Employee(
        employee_id=user.employee_id,
        name=user.name,
        password=hashed_password, 
        total_leave_days=15.0
    )
    
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return {"message": f"테스트 유저 생성 완료! ID: {user.employee_id}, 이름: {user.name}"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"에러 발생: {str(e)}")

# 현재 로그인한 사용자 가져오기 (의존성 함수) 

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="자격 증명을 확인할 수 없습니다.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = db.query(models.Employee).filter(models.Employee.employee_id == user_id).first()
    if user is None:
        raise credentials_exception
        
    return user