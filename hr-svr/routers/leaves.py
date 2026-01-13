from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

# [수정] 상대 경로(..) 제거 -> 루트 경로에서 바로 import
import schemas
import database
import models

# [수정] 같은 폴더에 있어도 명확하게 패키지 경로로 import
from routers.auth import get_current_user

router = APIRouter()

@router.get("/my-status", response_model=schemas.LeaveStatusResponse)
def get_my_leave_status(
    db: Session = Depends(database.get_db),
    current_user: models.Employee = Depends(get_current_user)
):
    # 1. 로그인한 사원(current_user)의 '승인'된 신청 내역만 가져오기
    applications = db.query(models.ApplicationModel).filter(
        models.ApplicationModel.employee_id == current_user.employee_id,
        models.ApplicationModel.status == "승인"
    ).all()

    # 2. 휴가 사용량 계산하기
    used_annual = 0.0  # 연차 (반차 포함)
    used_sick = 0.0    # 병가
    used_event = 0.0   # 경조사
    used_public = 0.0  # 공가

    for app in applications:
        # 날짜 차이 구하기 (종료일 - 시작일 + 1)
        duration = (app.end_date - app.start_date).days + 1
        if duration < 1: duration = 1.0

        if app.application_type == "연차":
            used_annual += float(duration)
        elif app.application_type in ["오전 반차", "오후 반차"]:
            used_annual += 0.5  # 반차는 0.5일
        elif app.application_type == "병가":
            used_sick += float(duration)
        elif app.application_type == "경조사 휴가":
            used_event += float(duration)
        # 공가 등 다른 타입이 있다면 여기에 추가

    # 3. 사원의 총 연차 일수 가져오기 (DB에 없으면 기본 15일)
    total_annual = float(current_user.total_leave_days) if current_user.total_leave_days else 15.0

    # 4. 프론트엔드로 보낼 데이터 만들기
    leave_list = [
        {
            "id": 1,
            "name": "연차휴가",
            "total_days": total_annual,
            "used_days": used_annual,
            "remaining_days": total_annual - used_annual
        },
        {
            "id": 2,
            "name": "경조사휴가",
            "total_days": 0.0,
            "used_days": used_event,
            "remaining_days": 0.0
        },
        {
            "id": 3,
            "name": "병가휴가",
            "total_days": 0.0,
            "used_days": used_sick,
            "remaining_days": 0.0
        },
        {
            "id": 4,
            "name": "공가 휴가",
            "total_days": 0.0,
            "used_days": used_public,
            "remaining_days": 0.0
        }
    ]

    # 최종 응답
    return {
        "total_used_all": used_annual,
        "leaves": leave_list
    }