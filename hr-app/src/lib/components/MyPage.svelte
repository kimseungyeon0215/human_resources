<script lang="ts">
    import { onMount, createEventDispatcher } from 'svelte'; 
    import { user } from '$lib/stores'; 
    
    const dispatch = createEventDispatcher();

    $: employeeId = $user?.id || (typeof localStorage !== 'undefined' ? localStorage.getItem('user_id') : '') || 'EN202501';

    let currentTime = "로딩 중...";
    let workTimer = "00:00:00";
    let weeklyStatusData: any[] = []; 
    let recentApplications: any[] = [];
    let isWorking = false;
    let clockInTime: Date | null = null;
    let intervalId: any;
    let isDropdownOpen = false;

    let summary = {
        myRequestCount: 0,
        workTimeSummary: "-",
        leaveBalance: 15,
        outingCount: 0
    };

    onMount(() => {
        intervalId = setInterval(updateTime, 1000);
        
        if (employeeId) {
            fetchWeeklyStatus();
            fetchRecentApplications();
            fetchDashboardSummary();
        }

        document.addEventListener('click', closeDropdown);

        return () => {
            clearInterval(intervalId);
            document.removeEventListener('click', closeDropdown);
        };
    });

    $: if (employeeId) {
        fetchWeeklyStatus();
        fetchRecentApplications();
        fetchDashboardSummary();
    }

    function closeDropdown(event: any) {
        const target = event.target as HTMLElement;
        if (!target.closest('.dropdown-container')) {
            isDropdownOpen = false;
        }
    }

    function toggleDropdown() {
        isDropdownOpen = !isDropdownOpen;
    }

    function handleApply(type: string) {
        if (type === '휴가 신청') dispatch('navigate', 'leave-apply'); 
        else if (type === '연장근무 신청') dispatch('navigate', 'overtime-apply'); 
        else if (type === '비용 처리') dispatch('navigate', 'expense-claim'); 
        else alert(`${type} 화면은 준비 중입니다.`);
        isDropdownOpen = false; 
    }

    function updateTime() {
        const now = new Date();
        const options: Intl.DateTimeFormatOptions = {
            hour: '2-digit', minute: '2-digit', second: '2-digit',
            year: 'numeric', month: '2-digit', day: '2-digit',
            weekday: 'short', hour12: true
        };
        currentTime = now.toLocaleString('ko-KR', options);

        if (isWorking && clockInTime) {
            const diff = now.getTime() - clockInTime.getTime();
            const h = Math.floor(diff / 3600000);
            const m = Math.floor((diff % 3600000) / 60000);
            const s = Math.floor((diff % 60000) / 1000);
            workTimer = `${String(h).padStart(2,'0')}:${String(m).padStart(2,'0')}:${String(s).padStart(2,'0')}`;
        }
    }

    function getCurrentAddress(): Promise<string> {
        return new Promise((resolve) => {
            if (!navigator.geolocation) {
                resolve("위치 정보 권한 없음");
                return;
            }

            const options = {
                enableHighAccuracy: true, 
                timeout: 10000,           
                maximumAge: 0             
            };

            navigator.geolocation.getCurrentPosition(
                async (position) => {
                    const lat = position.coords.latitude;
                    const lon = position.coords.longitude;

                    try {
                        const url = `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lon}&zoom=18&addressdetails=1&accept-language=ko`;
                        const res = await fetch(url);
                        
                        if (!res.ok) throw new Error("주소 변환 실패");
                        const data = await res.json();
                        
                        if (data && data.address) {
                            const a = data.address;
                            const city = a.city || a.province || ''; 
                            const district = a.borough || a.district || a.county || '';
                            const neighborhood = a.quarter || a.neighbourhood || a.road || '';
                            
                            let fullAddress = `${city} ${district} ${neighborhood}`.trim();

                            if (!fullAddress && data.display_name) {
                                fullAddress = data.display_name.split(',').slice(0, 2).reverse().join(' ');
                            }
                            resolve(fullAddress || `위도:${lat.toFixed(4)}, 경도:${lon.toFixed(4)}`);
                        } else {
                            resolve(`위도:${lat.toFixed(4)}, 경도:${lon.toFixed(4)}`);
                        }
                    } catch (e) {
                        console.error(e);
                        resolve(`위도:${lat.toFixed(4)}, 경도:${lon.toFixed(4)}`);
                    }
                },
                (error) => {
                    console.error("위치 권한 에러:", error);
                    resolve("위치 확인 불가 (브라우저 권한 확인)");
                },
                options 
            );
        });
    }

    async function fetchWeeklyStatus() {
        if(!employeeId) return;
        try {
            const res = await fetch(`http://127.0.0.1:8000/api/attendance/weekly/${employeeId}`);
            if (res.ok) weeklyStatusData = await res.json();
        } catch (e) { console.error(e); }
    }

    async function fetchRecentApplications() {
        if(!employeeId) return;
        try {
            const res = await fetch(`http://127.0.0.1:8000/api/applications/recent/${employeeId}`);
            if (res.ok) recentApplications = await res.json();
        } catch (e) { console.error(e); }
    }

    async function fetchDashboardSummary() {
        if(!employeeId) return;
        try {
            const res = await fetch(`http://127.0.0.1:8000/api/dashboard/summary/${employeeId}`);
            if (res.ok) summary = await res.json();
        } catch (e) { console.error(e); }
    }

    // 출근 처리
    async function handleClockIn() {
        if (!confirm("출근 처리하시겠습니까?")) return;

        // 위치 가져오기 (정확도 옵션 적용됨)
        const address = await getCurrentAddress();

        try {
            const res = await fetch('http://127.0.0.1:8000/api/attendance/clock-in', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ employee_id: employeeId, location: address })
            });
            const result = await res.json();
            
            if (res.ok) {
                alert(`${result.message}\n(위치: ${address})`);
                isWorking = true;
                clockInTime = new Date();
                fetchWeeklyStatus();
                fetchDashboardSummary(); 
            } else {
                alert(result.detail || '오류가 발생했습니다.');
            }
        } catch (e) { alert('서버 연결 오류'); }
    }

    // 퇴근 처리
    async function handleClockOut() {
        if (!confirm("퇴근 처리하시겠습니까?")) return;

        const address = await getCurrentAddress();

        try {
            const res = await fetch('http://127.0.0.1:8000/api/attendance/clock-out', {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ employee_id: employeeId, location: address })
            });
            const result = await res.json();

            if (res.ok) {
                alert(`${result.message}\n(위치: ${address})\n총 근무시간: ${workTimer}`);
                isWorking = false;
                workTimer = "00:00:00";
                fetchWeeklyStatus();
                fetchDashboardSummary();
            } else {
                alert(result.detail || '오류가 발생했습니다.');
            }
        } catch (e) { alert('서버 연결 오류'); }
    }
</script>

<div class="dashboard-content">
    
    <div class="card status-card">
        <div class="time-section">
            <p>{currentTime}</p>
            <h2>{workTimer}</h2>
            <div class="status-buttons">
                <button class="btn-check in" on:click={handleClockIn} disabled={isWorking}>출근</button>
                <button class="btn-check out" on:click={handleClockOut} disabled={!isWorking}>퇴근</button>
            </div>
        </div>
        
        <div class="summary-section">
            <ul>
                <li>
                    <span>내가 작성한 근태계</span>
                    <strong>{summary.myRequestCount}건</strong>
                </li>
                <li>
                    <span>일반/연장</span>
                    <strong>{summary.workTimeSummary}</strong>
                </li>
                <li>
                    <span>남은휴가</span>
                    <strong>{summary.leaveBalance}일</strong>
                </li>
                <li>
                    <span>이석/외출근태</span>
                    <strong>{summary.outingCount}건</strong>
                </li>
            </ul>
        </div>
    </div>

    <div class="apply-button-container dropdown-container">
        <button class="btn-apply" on:click={toggleDropdown}>
            신청하기 <span class="arrow">▼</span>
        </button>
        
        {#if isDropdownOpen}
            <div class="dropdown-menu">
                <button on:click={() => handleApply('휴가 신청')}>휴가 신청</button>
                <button on:click={() => handleApply('연장근무 신청')}>연장근무 신청</button>
                <button on:click={() => handleApply('비용 처리')}>비용 처리</button>
            </div>
        {/if}
    </div>

    <div class="card">
        <h3>주간현황</h3>
        <div class="table-responsive">
            <table>
                <thead>
                    <tr>
                        <th class="header-cell">일자(요일)</th>
                        {#each weeklyStatusData as item}
                            <th>{item.date}</th>
                        {/each}
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td class="header-cell">근무시간</td>
                        {#each weeklyStatusData as item}<td>{item.workTime}</td>{/each}
                    </tr>
                    <tr>
                        <td class="header-cell">연장근무시간</td>
                        {#each weeklyStatusData as item}<td>{item.overtime}</td>{/each}
                    </tr>
                    <tr>
                        <td class="header-cell">총 근무시간</td>
                        {#each weeklyStatusData as item}<td class="bold-text">{item.totalTime}</td>{/each}
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
    
    <div class="card">
        <h3>최근 신청내역</h3>
        <div class="table-responsive">
            <table>
                <thead>
                    <tr>
                        <th>상태</th><th>신청구분</th><th>시작일자</th><th>종료일자</th><th>소요시간</th><th>작성일</th>
                    </tr>
                </thead>
                <tbody>
                    {#each recentApplications as app}
                    <tr>
                        <td><span class="status-badge {app.status === '승인' ? 'approved' : 'rejected'}">{app.status}</span></td>
                        <td>{app.type}</td><td>{app.startDate}</td><td>{app.endDate}</td><td>{app.duration}</td><td>{app.requestDate}</td>
                    </tr>
                    {/each}
                </tbody>
            </table>
        </div>
    </div>
</div>

<style>
    /* 기존 스타일 그대로 유지 */
    .dashboard-content { 
        display: flex; 
        flex-direction: column; 
        gap: 24px; 
    }
    
    .card { background-color: #fff; border-radius: 12px; padding: 24px; box-shadow: 0 4px 20px rgba(0,0,0,0.05); }
    .card h3 { font-size: 1.1rem; font-weight: bold; margin: 0 0 16px 0; }
    
    .status-card { display: flex; align-items: center; justify-content: space-between; padding: 32px; }
    .time-section h2 { font-size: 48px; font-weight: 300; margin: 8px 0; }
    .status-buttons { display: flex; gap: 8px; }
    
    .btn-check { padding: 10px 28px; border-radius: 20px; border: none; font-size: 16px; font-weight: 600; cursor: pointer; transition: 0.2s; }
    .btn-check.in { background-color: #3c66f7; color: white; }
    .btn-check.in:hover { background-color: #254eda; }
    .btn-check.out { background-color: #f1f3f5; color: #333; }
    .btn-check.out:hover { background-color: #e9ecef; }
    .btn-check:disabled { background-color: #e9ecef; color: #adb5bd; cursor: not-allowed; }

    .summary-section ul { list-style: none; padding: 0; }
    .summary-section li { display: flex; justify-content: space-between; min-width: 200px; margin: 12px 0; }
    .summary-section li strong { font-weight: bold; }

    .dropdown-container { position: relative; display: flex; justify-content: center; margin-bottom: 10px; }
    .btn-apply { background-color: #3c66f7; color: white; padding: 14px 40px; border: none; border-radius: 8px; font-size: 16px; cursor: pointer; display: flex; align-items: center; gap: 8px; }
    .arrow { font-size: 12px; }

    .dropdown-menu {
        position: absolute;
        top: 110%;
        background-color: white;
        border: 1px solid #eee;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        display: flex;
        flex-direction: column;
        min-width: 160px;
        overflow: hidden;
        z-index: 10;
    }
    .dropdown-menu button {
        background: none;
        border: none;
        padding: 12px 16px;
        text-align: left;
        cursor: pointer;
        font-size: 14px;
        color: #333;
    }
    .dropdown-menu button:hover {
        background-color: #f8f9fa;
        color: #3c66f7;
    }
    
    .table-responsive { overflow-x: auto; }
    table { width: 100%; border-collapse: collapse; font-size: 14px; }
    th, td { padding: 16px; border-bottom: 1px solid #eee; text-align: center; white-space: nowrap; }
    thead th { color: #888; font-weight: normal; border-bottom: 2px solid #f1f3f5; background-color: #fcfcfc; }
    
    .header-cell { text-align: left; font-weight: 600; color: #555; background-color: #f8f9fa; padding-left: 20px; width: 120px; }
    tbody td:first-child { text-align: left; }
    .bold-text { font-weight: 700; color: #3c66f7; }
    
    .status-badge { padding: 4px 10px; border-radius: 12px; font-size: 12px; }
    .status-badge.approved { background-color: #e7f4e8; color: #4caf50; }
    .status-badge.rejected { background-color: #fdecea; color: #f44336; }
</style>