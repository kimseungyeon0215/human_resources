
from database import engine
from models import Base
import models 

print("🔄 데이터베이스 초기화를 시작합니다...")

try:
    # 기존 테이블 강제 삭제
    Base.metadata.drop_all(bind=engine)
    print("✅ 기존 테이블 삭제 완료!")

    # 새 테이블 생성 (password 컬럼 포함됨)
    Base.metadata.create_all(bind=engine)
    print("✅ 새 테이블 생성 완료!")
    
    print("🎉 DB 초기화 성공! 이제 서버를 켜고 유저를 다시 등록하세요.")

except Exception as e:
    print(f"❌ 에러 발생: {e}")