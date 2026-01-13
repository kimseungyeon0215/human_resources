// src/lib/types.ts

// 주간 근무 데이터 타입
export type WeeklyWorkData = {
    day: string;
    work: number;
    color: string;
};

// 근무 요약 데이터 타입
export type WorkSummary = {
    totalString: string;
    workHours: number;
    overtimeHours: number;
    workString: string;
    overtimeString: string;
};

// 주간 현황 데이터 타입
export type WeeklyStatus = {
    date: string;
    workTime: string;
    overtime: string;
    totalTime: string;
    status: string;
};

// 최근 신청내역 데이터 타입
export type Application = {
    type: string;
    startDate: string;
    endDate: string;
    duration: string;
    requestDate: string;
    status: string;
};

// 출퇴근 기록 데이터 타입
export type AttendanceRecord = {
    date: string;
    dayOfWeek: string;
    clockInTime: string;
    clockInLocation: string;
    clockOutTime: string;
    clockOutLocation: string;
    count: string;
    totalWorkTime: string;
    status: string;
};