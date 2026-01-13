from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime, timedelta
import calendar
import logging
from pydantic import BaseModel

# --- 파일 임포트 (프로젝트 구조에 맞게 확인) ---
import database
import models
import schemas
from routers import leaves, auth
from database import get_db

# --- 설정 ---
logging.basicConfig(level=logging.INFO)

# DB 테이블 자동 생성
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

# ==========================================
# CORS 설정
# ==========================================
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 라우터 등록 ---
app.include_router(leaves.router, prefix="/api/leaves", tags=["leaves"])
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])


# ==========================================
#  데이터 스키마 (Pydantic Models)
# ==========================================

class AttendanceRequest(BaseModel):
    employee_id: str
    location: Optional[str] = "-"

class WeeklyStatus(BaseModel):
    date: str
    workTime: str
    overtime: str
    totalTime: str

class Application(BaseModel):
    type: str
    startDate: str
    endDate: str
    duration: str
    requestDate: str
    status: str

class ApplicationRequest(BaseModel):
    employee_id: str
    application_type: str
    start_date: str
    end_date: str
    reason: str

class ApplicationStatusUpdate(BaseModel):
    status: str

class MonthlyStats(BaseModel):
    total: int
    normal: int
    unprocessed: int
    actual: int

class MonthlyRecord(BaseModel):
    date: str
    dayOfWeek: str
    clockInTime: str
    clockInLocation: str
    clockOutTime: str
    clockOutLocation: str
    totalWorkTime: str
    status: str

class MonthlyResponse(BaseModel):
    userName: str
    stats: MonthlyStats
    records: List[MonthlyRecord]

class DashboardSummary(BaseModel):
    myRequestCount: int      
    workTimeSummary: str     
    leaveBalance: float      
    outingCount: int         


# ==========================================
#  API 구현
# ==========================================

# 1. 출근
@app.post("/api/attendance/clock-in")
def clock_in(request: AttendanceRequest, db: Session = Depends(get_db)):
    today = datetime.now().date()
    existing = db.query(models.Attendance).filter(
        models.Attendance.employee_id == request.employee_id, 
        models.Attendance.attendance_date == today
    ).first()
    
    if existing: 
        raise HTTPException(status_code=400, detail="이미 오늘 출근 처리가 완료되었습니다.")
    
    new_attendance = models.Attendance(
        attendance_id=f"ATT-{int(datetime.now().timestamp())}", 
        employee_id=request.employee_id, 
        attendance_date=today, 
        attendance_in_time=datetime.now().time(), 
        attendance_method="PC", 
        attendance_in_location=request.location
    )
    db.add(new_attendance)
    db.commit()
    return {"message": "출근 처리되었습니다."}

# 2. 퇴근
@app.put("/api/attendance/clock-out")
def clock_out(request: AttendanceRequest, db: Session = Depends(get_db)):
    today = datetime.now().date()
    record = db.query(models.Attendance).filter(
        models.Attendance.employee_id == request.employee_id, 
        models.Attendance.attendance_date == today
    ).first()
    
    if record:
        record.attendance_out_time = datetime.now().time()
        record.attendance_out_location = request.location
        db.commit()
        return {"message": "퇴근 처리되었습니다."}
    raise HTTPException(status_code=404, detail="출근 기록이 없습니다.")

# 3. 주간 현황 조회
@app.get("/api/attendance/weekly/{employee_id}", response_model=List[WeeklyStatus])
def get_weekly_status(employee_id: str, db: Session = Depends(get_db)):
    today = datetime.now().date()
    start_date = today - timedelta(days=today.weekday())
    end_date = start_date + timedelta(days=6)
    
    db_records = db.query(models.Attendance).filter(
        models.Attendance.employee_id == employee_id, 
        models.Attendance.attendance_date.between(start_date, end_date)
    ).all()
    
    records_map = {r.attendance_date: r for r in db_records}
    result = []
    day_map = {0: "월", 1: "화", 2: "수", 3: "목", 4: "금", 5: "토", 6: "일"}
    
    def fmt_time(hours): return f"{int(hours):02d}:{int((hours * 60) % 60):02d}"
    
    for i in range(7):
        target_date = start_date + timedelta(days=i)
        record = records_map.get(target_date)
        formatted_date = f'{target_date.strftime("%m/%d")}({day_map[i]})'
        item = {"date": formatted_date, "workTime": "-", "overtime": "-", "totalTime": "-"}
        
        if record and record.attendance_in_time and record.attendance_out_time:
            t_in = datetime.combine(target_date, record.attendance_in_time)
            t_out = datetime.combine(target_date, record.attendance_out_time)
            duration_sec = (t_out - t_in).total_seconds()
            work_hours = duration_sec / 3600
            overtime_hours = 0
            std_close = t_in.replace(hour=18, minute=0, second=0)
            if t_out > std_close: 
                overtime_hours = (t_out - max(t_in, std_close)).total_seconds() / 3600
            
            item["workTime"] = fmt_time(work_hours)
            item["overtime"] = fmt_time(overtime_hours)
            item["totalTime"] = fmt_time(work_hours + overtime_hours)
        result.append(item)
    return result

# --- [신청서 관련 API] ---

# 4. 신청서 작성
@app.post("/api/applications")
def create_application(req: ApplicationRequest, db: Session = Depends(get_db)):
    try:
        def parse_dt(d_str):
            for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d", "%Y-%m-%d %H:%M:%S"):
                try:
                    return datetime.strptime(d_str, fmt)
                except ValueError:
                    continue
            return datetime.strptime(d_str, "%Y-%m-%d")

        new_app = models.ApplicationModel(
            application_id=f"APP-{int(datetime.now().timestamp())}",
            employee_id=req.employee_id,
            application_type=req.application_type,
            start_date=parse_dt(req.start_date),
            end_date=parse_dt(req.end_date),
            reason=req.reason,
            status="대기",
            created_at=datetime.now()
        )
        db.add(new_app)
        db.commit()
        return {"message": "신청이 완료되었습니다."}
    except Exception as e:
        print(f"Error occurred: {e}")
        raise HTTPException(status_code=500, detail="신청 중 오류가 발생했습니다.")

# 5. [관리자용] 모든 신청 내역 조회 (결재 대기 위젯용)
@app.get("/api/applications")
def get_all_applications(db: Session = Depends(get_db)):
    apps = db.query(models.ApplicationModel).order_by(models.ApplicationModel.created_at.desc()).all()
    return apps

# 6. [관리자용] 신청 내역 리스트 조회 (검색/필터 포함)
@app.get("/api/applications/list")
def get_application_list(
    start: Optional[str] = None, 
    end: Optional[str] = None, 
    query: Optional[str] = None, 
    db: Session = Depends(get_db)
):
    q = db.query(models.ApplicationModel, models.Employee).outerjoin(
        models.Employee, models.ApplicationModel.employee_id == models.Employee.employee_id
    )

    if start and end:
        s_date = datetime.strptime(start, "%Y-%m-%d")
        e_date = datetime.strptime(end, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
        q = q.filter(models.ApplicationModel.start_date.between(s_date, e_date))

    if query:
        q = q.filter(
            (models.Employee.name.like(f"%{query}%")) | 
            (models.Employee.department.like(f"%{query}%"))
        )

    records = q.order_by(models.ApplicationModel.created_at.desc()).all()

    result = []
    days_kr = ["월", "화", "수", "목", "금", "토", "일"]

    for app, emp in records:
        duration = "-"
        if app.start_date and app.end_date:
            diff = (app.end_date - app.start_date).total_seconds()
            h = int(diff // 3600)
            m = int((diff % 3600) // 60)
            duration = f"{h:02d}:{m:02d}"

        category = "기타"
        if "휴가" in app.application_type or "연차" in app.application_type: category = "휴가"
        elif "외근" in app.application_type: category = "외근"
        elif "출장" in app.application_type: category = "출장"
        elif "연장" in app.application_type or "근무" in app.application_type: category = "연장"
        elif "수정" in app.application_type or "정정" in app.application_type: category = "수정"

        status_text = app.status
        if app.status == "승인": status_text = "승인완료"

        result.append({
            "id": app.application_id,
            "date": f"{app.start_date.month}/{app.start_date.day}({days_kr[app.start_date.weekday()]})",
            "name": emp.name if emp else app.employee_id,
            "dept": emp.department if emp else "-",
            "rank": emp.position if emp else "-",
            "category": category,
            "type": app.application_type,
            "startTime": app.start_date.strftime("%H:%M"),
            "endTime": app.end_date.strftime("%H:%M"),
            "duration": duration,
            "status": status_text
        })
    
    return result

# 7. [관리자용] 신청 내역 상태 변경
@app.put("/api/applications/{app_id}/status")
def update_application_status(app_id: str, req: ApplicationStatusUpdate, db: Session = Depends(get_db)):
    app = db.query(models.ApplicationModel).filter(models.ApplicationModel.application_id == app_id).first()
    
    if not app and app_id.isdigit():
        app = db.query(models.ApplicationModel).filter(models.ApplicationModel.id == int(app_id)).first()
        
    if not app:
        raise HTTPException(status_code=404, detail="해당 신청 내역을 찾을 수 없습니다.")
    
    app.status = req.status
    db.commit()
    return {"message": f"상태가 '{req.status}'(으)로 변경되었습니다."}

# 8. [개인용] 최근 신청 내역 조회
@app.get("/api/applications/recent/{employee_id}", response_model=List[Application])
def get_recent_applications(employee_id: str, db: Session = Depends(get_db)):
    one_month_ago = datetime.now() - timedelta(days=30)
    
    records = db.query(models.ApplicationModel).filter(
        models.ApplicationModel.employee_id == employee_id,
        models.ApplicationModel.created_at >= one_month_ago
    ).order_by(models.ApplicationModel.created_at.desc()).all()
    
    result = []
    for r in records:
        result.append({
            "type": r.application_type,
            "startDate": r.start_date.strftime("%Y.%m.%d"),
            "endDate": r.end_date.strftime("%Y.%m.%d"),
            "duration": "-", 
            "requestDate": r.created_at.strftime("%Y.%m.%d"),
            "status": r.status
        })
    return result

# 9. 월별 근태 조회 (개인)
@app.get("/api/attendance/monthly/{employee_id}", response_model=MonthlyResponse)
def get_monthly_attendance(employee_id: str, year: int, month: int, db: Session = Depends(get_db)):
    emp = db.query(models.Employee).filter(models.Employee.employee_id == employee_id).first()
    user_name = emp.name if emp else "알 수 없음"
    
    _, last_day = calendar.monthrange(year, month)
    start_date = date(year, month, 1)
    end_date = date(year, month, last_day)
    
    records = db.query(models.Attendance).filter(
        models.Attendance.employee_id == employee_id,
        models.Attendance.attendance_date.between(start_date, end_date)
    ).order_by(models.Attendance.attendance_date.asc()).all()
    
    records_map = {r.attendance_date: r for r in records}
    
    processed = []
    stats = {"total": last_day, "normal": 0, "unprocessed": 0, "actual": len(records)}
    day_map = {0: "월", 1: "화", 2: "수", 3: "목", 4: "금", 5: "토", 6: "일"}

    def simple_loc(loc):
        if not loc or loc == '-': return '-'
        parts = loc.split()
        filtered = [p for p in parts if any(x in p for x in ['시', '구', '군', '동', '읍', '면'])]
        return " ".join(filtered[:2]) if filtered else loc

    for d in range(1, last_day + 1):
        curr = date(year, month, d)
        rec = records_map.get(curr)
        
        item = {
            "date": curr.strftime("%Y.%m.%d"),
            "dayOfWeek": day_map[curr.weekday()],
            "clockInTime": "-", "clockInLocation": "-",
            "clockOutTime": "-", "clockOutLocation": "-",
            "totalWorkTime": "-", "status": "미처리"
        }
        
        if rec:
            if rec.attendance_in_time:
                item["clockInTime"] = rec.attendance_in_time.strftime("%H:%M")
                item["clockInLocation"] = simple_loc(rec.attendance_in_location)
            if rec.attendance_out_time:
                item["clockOutTime"] = rec.attendance_out_time.strftime("%H:%M")
                item["clockOutLocation"] = simple_loc(rec.attendance_out_location)
            
            if rec.attendance_in_time and rec.attendance_out_time:
                t_in = datetime.combine(date.min, rec.attendance_in_time)
                t_out = datetime.combine(date.min, rec.attendance_out_time)
                dur = (t_out - t_in).total_seconds()
                h, m = int(dur // 3600), int((dur % 3600) // 60)
                item["totalWorkTime"] = f"{h:02d}:{m:02d}"
                item["status"] = "정상처리"
                stats["normal"] += 1
            elif rec.attendance_in_time:
                item["status"] = "퇴근미처리"
                stats["unprocessed"] += 1
        else:
            if curr.weekday() >= 5: item["status"] = "-"
            elif curr < date.today():
                item["status"] = "결근"
                stats["unprocessed"] += 1
            else: item["status"] = "-"

        processed.append(item)

    return {"userName": user_name, "stats": stats, "records": processed}

# 10. 대시보드 요약 (개인)
@app.get("/api/dashboard/summary/{employee_id}", response_model=DashboardSummary)
def get_dashboard_summary(employee_id: str, db: Session = Depends(get_db)):
    today = datetime.now()
    start_of_month = date(today.year, today.month, 1)
    
    request_count = db.query(models.ApplicationModel).filter(
        models.ApplicationModel.employee_id == employee_id, 
        models.ApplicationModel.created_at >= start_of_month
    ).count()
    
    monthly_records = db.query(models.Attendance).filter(
        models.Attendance.employee_id == employee_id, 
        models.Attendance.attendance_date >= start_of_month
    ).all()
    
    total_work = 0
    total_over = 0
    for r in monthly_records:
        if r.attendance_in_time and r.attendance_out_time:
            t_in = datetime.combine(r.attendance_date, r.attendance_in_time)
            t_out = datetime.combine(r.attendance_date, r.attendance_out_time)
            total_work += (t_out - t_in).total_seconds()
            std_close = t_in.replace(hour=18, minute=0, second=0)
            if t_out > std_close: 
                total_over += (t_out - max(t_in, std_close)).total_seconds()
            
    emp = db.query(models.Employee).filter(models.Employee.employee_id == employee_id).first()
    
    total_leave = float(emp.total_leave_days) if emp and emp.total_leave_days else 15.0
    
    approved_apps = db.query(models.ApplicationModel).filter(
        models.ApplicationModel.employee_id == employee_id,
        models.ApplicationModel.status == "승인"
    ).all()
    
    used_leave = 0.0
    for app in approved_apps:
        if app.application_type in ["연차", "병가", "경조사 휴가"]:
             if app.application_type == "연차":
                days = (app.end_date - app.start_date).days + 1
                used_leave += float(days)
        elif app.application_type in ["오전 반차", "오후 반차"]:
            used_leave += 0.5

    outing_count = db.query(models.ApplicationModel).filter(
        models.ApplicationModel.employee_id == employee_id, 
        models.ApplicationModel.application_type.in_(["이석", "외출", "출장"]), 
        models.ApplicationModel.created_at >= start_of_month
    ).count()
    
    return {
        "myRequestCount": request_count,
        "workTimeSummary": f"{int(total_work//3600)}h / {int(total_over//3600)}h", 
        "leaveBalance": total_leave - used_leave, 
        "outingCount": outing_count
    }

# ==========================================
# [관리자 대시보드용 API]
# ==========================================

# 11. [관리자용] 전체 직원 출퇴근 내역 조회
@app.get("/api/attendance/all")
def get_all_attendance(date: Optional[str] = None, db: Session = Depends(get_db)):
    target_date = datetime.strptime(date, "%Y-%m-%d").date() if date else datetime.now().date()
    
    records = db.query(models.Attendance, models.Employee).outerjoin(
        models.Employee, models.Attendance.employee_id == models.Employee.employee_id
    ).filter(
        models.Attendance.attendance_date == target_date
    ).all()
    
    result = []
    for att, emp in records:
        in_time = att.attendance_in_time.strftime("%H:%M") if att.attendance_in_time else "-"
        out_time = att.attendance_out_time.strftime("%H:%M") if att.attendance_out_time else "-"
        
        status = "-"
        if in_time != "-" and out_time != "-": status = "정상처리"
        elif in_time != "-": status = "퇴근미처리"
        
        result.append({
            "date": att.attendance_date.strftime("%m/%d"),
            "name": emp.name if emp else att.employee_id,
            "dept": emp.department if emp else "-",
            "rank": emp.position if emp else "-",
            "in": in_time,
            "inLoc": att.attendance_in_location or "-",
            "out": out_time,
            "outLoc": att.attendance_out_location or "-",
            "status": status
        })
    return result

# 12. (삭제됨) 출퇴근 수정 요청 API 제거 완료

# 13. [관리자용] 휴가 일정 조회
@app.get("/api/leaves/schedule")
def get_leave_schedule(
    year: Optional[int] = None, 
    month: Optional[int] = None, 
    start: Optional[str] = None, 
    end: Optional[str] = None, 
    db: Session = Depends(get_db)
):
    import calendar
    
    target_start = datetime.now()
    target_end = datetime.now()

    if start and end:
        target_start = datetime.strptime(start, "%Y-%m-%d")
        target_end = datetime.strptime(end, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
    elif year and month:
        _, last_day = calendar.monthrange(year, month)
        target_start = datetime(year, month, 1)
        target_end = datetime(year, month, last_day, 23, 59, 59)
    else:
        today = datetime.now()
        _, last_day = calendar.monthrange(today.year, today.month)
        target_start = datetime(today.year, today.month, 1)
        target_end = datetime(today.year, today.month, last_day, 23, 59, 59)

    apps = db.query(models.ApplicationModel, models.Employee).outerjoin(
        models.Employee, models.ApplicationModel.employee_id == models.Employee.employee_id
    ).filter(
        models.ApplicationModel.start_date <= target_end,
        models.ApplicationModel.end_date >= target_start,
        (models.ApplicationModel.application_type.like("%휴가%")) | 
        (models.ApplicationModel.application_type.like("%연차%")) | 
        (models.ApplicationModel.application_type.like("%반차%")) |
        (models.ApplicationModel.application_type.like("%병가%"))
    ).all()

    result = []
    days_kr = ["월", "화", "수", "목", "금", "토", "일"]

    for app, emp in apps:
        item_name = "휴가"
        if "취소" in app.application_type: item_name = "휴가취소"
        
        duration = ""
        if app.start_date and app.end_date:
            diff = (app.end_date - app.start_date).total_seconds()
            hours = diff / 3600
            if "반차" in app.application_type:
                duration = "04:00"
            elif hours >= 8:
                duration = "" 
            else:
                h = int(hours)
                m = int((diff % 3600) // 60)
                duration = f"{h:02d}:{m:02d}"

        display_status = app.status
        if app.status == "승인": display_status = "승인완료"

        result.append({
            "id": app.application_id,  # [수정] app.id -> app.application_id (오류 방지)
            "date": f"{app.start_date.month}/{app.start_date.day}({days_kr[app.start_date.weekday()]})",
            "name": emp.name if emp else app.employee_id,
            "dept": emp.department if emp else "-",
            "rank": emp.position if emp else "-",
            "item": item_name, 
            "type": app.application_type,
            "startTime": app.start_date.strftime("%H:%M"),
            "endTime": app.end_date.strftime("%H:%M"),
            "duration": duration,
            "status": display_status,
            "raw_date": app.start_date
        })
    
    result.sort(key=lambda x: x['raw_date'])
    return result

# 14. [추가] 직원 상세 정보 조회 (프론트엔드 에러 해결용)
@app.get("/api/employees/{employee_id}")
def get_employee_detail(employee_id: str, db: Session = Depends(get_db)):
    emp = db.query(models.Employee).filter(models.Employee.employee_id == employee_id).first()
    
    if not emp:
        # 직원이 없으면 에러 대신 기본 정보라도 리턴 (프론트엔드 멈춤 방지)
        return {
            "employee_id": employee_id,
            "name": "알 수 없음",
            "department": "-",
            "position": "-",
            "email": "-",
            "phone": "-",
            "join_date": str(date.today()),
            "total_leave_days": 15
        }
    
    return {
        "employee_id": emp.employee_id,
        "name": emp.name,
        "department": emp.department,
        "position": emp.position,
        "email": emp.email,
        "phone": emp.phone,
        "join_date": str(emp.join_date) if emp.join_date else "-",
        "total_leave_days": emp.total_leave_days
    }