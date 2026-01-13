<script lang="ts">
    import { onMount, createEventDispatcher } from 'svelte';
    import { user } from '$lib/stores'; // 로그인 정보 스토어 가져오기
    
    const dispatch = createEventDispatcher();

    let currentDate = new Date();
    let currentYear = currentDate.getFullYear();
    let currentMonth = currentDate.getMonth() + 1;

    let monthDisplay = ""; 
    let searchText = "";   
    let dateRangeText = "";

    let summary = { total: 0, normal: 0, unprocessed: 0, actual: 0 };
    let logs: any[] = [];
    let userName = "";

    onMount(() => {
        updateDateVariables(); // 초기 날짜 텍스트 설정
        
        // 스토어에 저장된 이름이 있으면 그걸 쓰고, 없으면 로컬스토리지에서 찾음
        if ($user && $user.name) {
            userName = $user.name;
        } else {
            userName = localStorage.getItem('user_id') || '사용자';
        }

        fetchAttendanceLogs(); 
    });

    // 날짜 변수 업데이트
    function updateDateVariables() {
        const m = String(currentMonth).padStart(2, '0');
        const lastDay = new Date(currentYear, currentMonth, 0).getDate();

        monthDisplay = `${currentYear}.${m}`;
        searchText = `${currentYear}.${m}`; 
        dateRangeText = `${currentYear}.${m}.01 ~ ${currentYear}.${m}.${lastDay}`;
    }

    async function fetchAttendanceLogs() {
        // 토큰 가져오기
        const token = localStorage.getItem('access_token');
        if (!token) {
            console.warn("토큰이 없어 데이터를 불러올 수 없습니다.");
            return;
        }

        // 사용자 ID 가져오기
        // 1순위: 스토어($user.id), 2순위: 로컬스토리지, 3순위: 기본값
        const userId = $user?.id || localStorage.getItem('user_id') || 'user1';

        try {

            const url = `http://127.0.0.1:8000/api/attendance/monthly/${userId}?year=${currentYear}&month=${currentMonth}`;
            
            const res = await fetch(url, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`, 
                    'Content-Type': 'application/json'
                }
            });

            if (res.ok) {
                const data = await res.json();
                
                if (data.records) {
                    logs = data.records;
                    summary = data.stats; 
                    if (data.userName) userName = data.userName;
                } else if (Array.isArray(data)) {
                    logs = data;
                    calculateSummary(logs);
                } else {
                    logs = [];
                    console.warn("데이터 형식이 예상과 다릅니다.", data);
                }
            } else {
                console.error("데이터 로드 실패:", res.status);
            }
        } catch (e) {
            console.error("API 에러:", e);
            alert("서버와 연결할 수 없습니다.");
        }
    }

    function calculateSummary(records: any[]) {
        const total = records.length;
        const normal = records.filter(r => r.status === '정상' || r.status === '정상처리').length;
        const unprocessed = records.filter(r => r.status === '결근' || r.status === '퇴근미처리' || r.status === '지각').length;
        
        summary = {
            total: total,
            normal: normal,
            unprocessed: unprocessed,
            actual: normal 
        };
    }

    function moveMonth(step: number) {
        const newDate = new Date(currentYear, currentMonth - 1 + step, 1);
        currentYear = newDate.getFullYear();
        currentMonth = newDate.getMonth() + 1;

        updateDateVariables();
        fetchAttendanceLogs();
    }

    function handleSearch() {
        const parts = searchText.split('.');
        if (parts.length === 2) {
            const y = parseInt(parts[0]);
            const m = parseInt(parts[1]);

            if (!isNaN(y) && !isNaN(m) && m >= 1 && m <= 12) {
                currentYear = y;
                currentMonth = m;
                updateDateVariables();
                fetchAttendanceLogs();
            } else {
                alert("올바른 형식(YYYY.MM)으로 입력해주세요.");
            }
        } else {
            alert("YYYY.MM 형식으로 입력해주세요.");
        }
    }
</script>

<div class="attendance-container">
    
    <div class="header">
        <button class="back-btn" on:click={() => dispatch('goBack')}>
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="15 18 9 12 15 6"></polyline>
            </svg>
        </button>
        <h2>출퇴근 기록 조회</h2>
    </div>

    <div class="filter-section">
        <div class="month-selector">
            <button on:click={() => moveMonth(-1)}>&lt;</button>
            <span class="current-month">{monthDisplay}</span>
            <button on:click={() => moveMonth(1)}>&gt;</button>
        </div>
        <div class="date-range">
            <input type="text" bind:value={searchText} placeholder="YYYY.MM" on:keydown={(e) => e.key === 'Enter' && handleSearch()} />
        </div>
        <button class="search-btn" on:click={handleSearch}>검색</button>
    </div>

    <div class="summary-cards">
        <div class="s-card">
            <span class="label">전체</span>
            <span class="value">{summary.total} <span class="unit">건</span></span>
        </div>
        <div class="s-card">
            <span class="label">정상근무일</span>
            <span class="value">{summary.normal} <span class="unit">건</span></span>
        </div>
        <div class="s-card">
            <span class="label">미처리/결근</span>
            <span class="value">{summary.unprocessed} <span class="unit">건</span></span>
        </div>
        <div class="s-card active">
            <span class="label">실제 출퇴근등록일</span>
            <span class="value">{summary.actual} <span class="unit">건</span></span>
            <div class="progress-bar">
                <div class="fill" style="width: {summary.total > 0 ? (summary.actual / summary.total) * 100 : 0}%"></div>
            </div>
        </div>
    </div>

    <div class="list-title">{userName}님의 {dateRangeText} 출퇴근기록</div>

    <div class="table-container">
        <table>
            <thead>
                <tr>
                    <th>일자</th>
                    <th>요일</th>
                    <th>출근시각</th>
                    <th>출근위치</th>
                    <th>퇴근시각</th>
                    <th>퇴근위치</th>
                    <th>총 근무시간</th>
                    <th>상태</th>
                </tr>
            </thead>
            <tbody>
                {#if logs.length === 0}
                    <tr>
                        <td colspan="8" style="padding: 30px; text-align: center; color: #999;">
                            해당 기간의 기록이 없습니다.
                        </td>
                    </tr>
                {:else}
                    {#each logs as log}
                    <tr>
                        <td>{log.date}</td>
                        <td>{log.dayOfWeek || '-'}</td>
                        <td>{log.check_in_time || log.clockInTime || '-'}</td>
                        <td>{log.check_in_location || log.clockInLocation || '-'}</td>
                        <td>{log.check_out_time || log.clockOutTime || '-'}</td>
                        <td>{log.check_out_location || log.clockOutLocation || '-'}</td>
                        <td>{log.total_work_time || log.totalWorkTime || '-'}</td>
                        <td>
                            <span class="status-badge {
                                (log.status === '결근' || log.status === '퇴근미처리' || log.status === '지각') ? 'absent' : 
                                (log.status === '정상' || log.status === '정상처리') ? 'normal' : ''
                            }">
                                {log.status}
                            </span>
                        </td>
                    </tr>
                    {/each}
                {/if}
            </tbody>
        </table>
    </div>
</div>

<style>
    .attendance-container { padding: 24px; background-color: #fff; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.05); }
    .header { display: flex; align-items: center; justify-content: center; position: relative; margin-bottom: 32px; }
    .back-btn { position: absolute; left: 0; background: none; border: none; cursor: pointer; color: #666; padding: 8px; }
    .header h2 { font-size: 20px; font-weight: bold; margin: 0; color: #333; }
    .filter-section { display: flex; gap: 12px; margin-bottom: 24px; align-items: center; background-color: #f8f9fa; padding: 20px; border-radius: 8px; }
    .month-selector { display: flex; align-items: center; gap: 12px; font-weight: bold; font-size: 18px; margin-right: 12px; }
    .month-selector button { border: none; background: none; font-size: 18px; cursor: pointer; color: #888; }
    .date-range input { padding: 10px; border: 1px solid #ddd; border-radius: 6px; width: 250px; text-align: center; background-color: #fff; }
    .search-btn { background-color: #3c66f7; color: white; border: none; padding: 10px 24px; border-radius: 6px; cursor: pointer; font-weight: bold; }
    .summary-cards { display: flex; gap: 16px; margin-bottom: 32px; }
    .s-card { flex: 1; background-color: #f8f9fa; border-radius: 8px; padding: 20px; display: flex; flex-direction: column; gap: 8px; }
    .s-card.active { background-color: #f0f4ff; border: 1px solid #e0e7ff; }
    .s-card .label { font-size: 13px; color: #666; }
    .s-card .value { font-size: 24px; font-weight: bold; color: #333; }
    .s-card .unit { font-size: 16px; font-weight: normal; color: #666; }
    .progress-bar { height: 4px; background-color: #ddd; border-radius: 2px; margin-top: 8px; overflow: hidden; }
    .progress-bar .fill { height: 100%; background-color: #3c66f7; transition: width 0.3s ease; }
    .list-title { font-size: 14px; color: #666; margin-bottom: 12px; }
    .table-container { overflow-x: auto; }
    table { width: 100%; border-collapse: collapse; font-size: 14px; }
    th { background-color: #f9f9f9; color: #555; padding: 14px; border-bottom: 1px solid #eee; font-weight: 600; text-align: center; }
    td { padding: 16px; border-bottom: 1px solid #f5f5f5; text-align: center; color: #333; }
    .status-badge { padding: 6px 16px; border-radius: 20px; font-size: 12px; font-weight: bold; color: #888; background-color: #f5f5f5; }
    .status-badge.absent { background-color: #fff0f0; color: #e03131; }
    .status-badge.normal { background-color: #ebfbee; color: #2b8a3e; }
</style>