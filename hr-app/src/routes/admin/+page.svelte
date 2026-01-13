<script lang="ts">
    import { onMount } from 'svelte';

    // 직원용 컴포넌트 
    import Login from '$lib/components/Login.svelte';
    import MyPage from '$lib/components/MyPage.svelte';
    import LeavePage from '$lib/components/LeavePage.svelte';
    import AttendanceLog from '$lib/components/attendance/AttendanceLog.svelte';
    import LeaveApplicationForm from '$lib/components/LeaveApplicationForm.svelte';
    import OvertimeApplicationForm from '$lib/components/OvertimeApplicationForm.svelte';
    import ExpenseClaimForm from '$lib/components/ExpenseClaimForm.svelte';

    // 관리자용 컴포넌트
    import AdminLeaveDashboard from '$lib/components/AdminDashboard/AdminLeaveDashboard.svelte';
    import AdminAttendanceView from '$lib/components/AdminDashboard/AdminAttendanceView.svelte';
    // import AdminApprovalStatus 삭제 (직접 구현함)
    import AdminApplicationList from '$lib/components/AdminDashboard/AdminApplicationList.svelte';

    let isLoggedIn = false;
    let currentView = 'dashboard'; 
    let attendanceSubView = 'my'; 
    let leaveSubView = 'my';

    // ★ 관리자 대시보드용 데이터
    let waitingApps: any[] = [];
    let stats = { leave: 0, overtime: 0, expense: 0 };

    onMount(() => {
        const token = localStorage.getItem('access_token');
        if (token) {
            isLoggedIn = true;
            // 로그인 되어 있다면 결재 대기 목록도 미리 불러옴
            fetchWaitingApplications();
        }
    });

    // ★ [핵심 1] 결재 대기 목록 불러오기
    async function fetchWaitingApplications() {
        try {
            const res = await fetch('http://127.0.0.1:8000/api/applications');
            if (res.ok) {
                const data = await res.json();
                waitingApps = data.filter((app: any) => app.status === '대기');
                calculateStats();
            }
        } catch (e) { console.error(e); }
    }

    function calculateStats() {
        stats.leave = waitingApps.filter(a => a.application_type.includes('휴가') || a.application_type.includes('연차')).length;
        stats.overtime = waitingApps.filter(a => a.application_type.includes('근무')).length;
        stats.expense = waitingApps.filter(a => a.application_type.includes('비용')).length;
    }

    // ★ [핵심 2] 날짜/시간 예쁘게 보여주는 함수 (여기가 문제 해결 포인트!)
    function formatPeriod(start: string, end: string, type: string) {
        if (!start) return '-';
        const s = new Date(start);
        const e = new Date(end);

        // 날짜 (2026-01-09)
        const dateStr = s.toLocaleDateString('ko-KR', { year: 'numeric', month: '2-digit', day: '2-digit' }).replace(/\./g, '-').replace(/ /g, '').slice(0, -1);
        
        // 시간 (19:00)
        const startTime = s.toTimeString().slice(0, 5);
        const endTime = e.toTimeString().slice(0, 5);

        // 휴가는 시간 숨김
        if (type.includes('휴가') || type.includes('연차')) return dateStr;
        
        // 연장근무인데 시간이 00:00이면(옛날 데이터) 날짜만 표시
        if (startTime === '00:00' && endTime === '00:00') return dateStr;

        // 정상적인 연장근무는 시간까지 표시
        return `${dateStr} ${startTime}~${endTime}`;
    }

    // ★ [핵심 3] 승인/반려 처리
    async function updateStatus(appId: string, newStatus: string) {
        if (!confirm(`${newStatus} 처리하시겠습니까?`)) return;
        try {
            const res = await fetch(`http://127.0.0.1:8000/api/applications/${appId}/status`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ status: newStatus })
            });
            if (res.ok) {
                alert("처리되었습니다.");
                fetchWaitingApplications(); // 목록 새로고침
            }
        } catch (e) { alert("오류 발생"); }
    }

    function handleLoginSuccess() {
        isLoggedIn = true;
        currentView = 'dashboard'; 
        fetchWaitingApplications(); // 로그인 직후 데이터 로드
        window.scrollTo(0, 0);
    }

    function handleLogout() {
        localStorage.removeItem('access_token');
        localStorage.removeItem('savedUsername');
        isLoggedIn = false;
        currentView = 'dashboard';
        alert("관리자 로그아웃 되었습니다.");
        window.location.href = "/";
    }

    function switchView(viewName: string) {
        currentView = viewName;
        if (viewName === 'attendance-log') attendanceSubView = 'my';
        if (viewName === 'leave-mgmt') leaveSubView = 'my';
        if (viewName === 'approvals') fetchWaitingApplications(); // 탭 이동 시 데이터 갱신
        window.scrollTo(0, 0);
    }

    function handleNavigation(event: CustomEvent) {
        const target = event.detail;
        if (target === 'leave-apply') currentView = 'leave';
        else if (target === 'overtime-apply') currentView = 'overtime';
        else if (target === 'expense-claim') currentView = 'expense-claim';
        else if (target === 'attendance-log') currentView = 'attendance-log';
        else if (target === 'leave-mgmt') currentView = 'leave-mgmt';
        window.scrollTo(0, 0);
    }

    function goBack() {
        currentView = 'dashboard';
        window.scrollTo(0, 0);
    }
</script>

{#if !isLoggedIn}
    <Login on:loginSuccess={handleLoginSuccess} />
{:else}
    <div class="app-container">
        
        <header class="global-header">
            <h1>근태관리 <span style="font-size: 0.6em; color: #3c66f7; vertical-align: middle;">(ADMIN)</span></h1>
            <nav>
                <a href="#" class:active={currentView === 'dashboard'} on:click|preventDefault={() => switchView('dashboard')}>마이페이지</a>
                <a href="#" class:active={currentView === 'approvals'} on:click|preventDefault={() => switchView('approvals')}>결재 대기 현황</a>
                <a href="#" class:active={currentView === 'attendance-log'} on:click|preventDefault={() => switchView('attendance-log')}>출퇴근기록</a>
                <a href="#" class:active={currentView === 'leave-mgmt'} on:click|preventDefault={() => switchView('leave-mgmt')}>휴가관리</a>
                <a href="#" class:active={currentView === 'app-list'} on:click|preventDefault={() => switchView('app-list')}>신청내역</a>
            </nav>
            <div class="header-right">
                <button class="logout-btn" on:click={handleLogout}>로그아웃</button>
            </div>
        </header>

        {#if currentView === 'dashboard'}
            <div class="content-area">
                <MyPage on:navigate={handleNavigation} />
            </div>

        {:else if currentView === 'approvals'}
            <div class="content-area full-page">
                <div class="stats-grid">
                    <div class="stat-card">
                        <h4>휴가 승인 요청</h4>
                        <div class="count blue">{stats.leave} <span class="unit">건</span></div>
                    </div>
                    <div class="stat-card">
                        <h4>추가 근무 승인 요청</h4>
                        <div class="count orange">{stats.overtime} <span class="unit">건</span></div>
                    </div>
                    <div class="stat-card">
                        <h4>비용 처리 승인 요청</h4>
                        <div class="count green">{stats.expense} <span class="unit">건</span></div>
                    </div>
                </div>

                <div class="card full-page-card">
                    <div class="card-padding">
                        <h3 class="table-title">관리자 결재 대기 목록</h3>
                        <table>
                            <thead>
                                <tr>
                                    <th>구분</th><th>요청자(ID)</th><th>상세 내용</th>
                                    <th>기간/일시</th><th>요청일</th><th>처리</th>
                                </tr>
                            </thead>
                            <tbody>
                                {#if waitingApps.length === 0}
                                    <tr><td colspan="6" class="empty-msg">대기 중인 요청이 없습니다.</td></tr>
                                {:else}
                                    {#each waitingApps as app}
                                    <tr>
                                        <td><span class="type-badge">{app.application_type}</span></td>
                                        <td>{app.employee_id}</td>
                                        <td class="text-left">{app.reason}</td>
                                        
                                        <td class="date-col">{formatPeriod(app.start_date, app.end_date, app.application_type)}</td>
                                        
                                        <td>{new Date(app.created_at).toLocaleDateString()}</td>
                                        <td>
                                            <div class="action-btns">
                                                <button class="btn-approve" on:click={() => updateStatus(app.application_id, '승인')}>승인</button>
                                                <button class="btn-reject" on:click={() => updateStatus(app.application_id, '반려')}>반려</button>
                                            </div>
                                        </td>
                                    </tr>
                                    {/each}
                                {/if}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

        {:else if currentView === 'attendance-log'}
            <div class="content-area full-page">
                <div class="sub-nav-container">
                    <button class="sub-nav-btn {attendanceSubView === 'my' ? 'active' : ''}" on:click={() => attendanceSubView = 'my'}>나의 출퇴근기록</button>
                    <button class="sub-nav-btn {attendanceSubView === 'all' ? 'active' : ''}" on:click={() => attendanceSubView = 'all'}>출퇴근내역 (전체)</button>
                </div>
                <div class="card full-page-card">
                    {#if attendanceSubView === 'my'} <AttendanceLog on:goBack={goBack} />
                    {:else} <AdminAttendanceView /> {/if}
                </div>
            </div>

        {:else if currentView === 'leave-mgmt'}
            <div class="content-area full-page">
                <div class="sub-nav-container">
                    <button class="sub-nav-btn {leaveSubView === 'my' ? 'active' : ''}" on:click={() => leaveSubView = 'my'}>나의 휴가</button>
                    <button class="sub-nav-btn {leaveSubView === 'all' ? 'active' : ''}" on:click={() => leaveSubView = 'all'}>휴가일정조회</button>
                </div>
                <div class="card full-page-card">
                    {#if leaveSubView === 'my'} <LeavePage on:goBack={goBack} />
                    {:else} <AdminLeaveDashboard /> {/if}
                </div>
            </div>

        {:else if currentView === 'app-list'}
            <div class="content-area full-page">
                <div class="card full-page-card">
                    <AdminApplicationList />
                </div>
            </div>

        {:else if currentView === 'leave'}
            <div class="content-area full-page"><div class="card full-page-card"><LeaveApplicationForm on:goBack={goBack} /></div></div>
        {:else if currentView === 'overtime'}
            <div class="content-area full-page"><div class="card full-page-card"><OvertimeApplicationForm on:goBack={goBack} /></div></div>
        {:else if currentView === 'expense-claim'}
            <div class="content-area full-page"><div class="card full-page-card"><ExpenseClaimForm on:goBack={goBack} /></div></div>
        {/if}
    </div>
{/if}

<style>
    /* 기존 스타일 유지 */
    .app-container { font-family: 'Pretendard', sans-serif; background-color: #f4f7fe; min-height: 100vh; }
    .global-header { display: flex; align-items: center; padding: 24px 48px; background-color: #f4f7fe; }
    .global-header h1 { font-size: 24px; font-weight: bold; margin-right: 40px; color: #000; white-space: nowrap; }
    .global-header nav { display: flex; gap: 20px; flex-grow: 1; }
    .global-header a { text-decoration: none; color: #555; font-weight: 600; font-size: 16px; transition: color 0.2s; white-space: nowrap; }
    .global-header a.active { color: #3c66f7; }
    .global-header a:hover { color: #3c66f7; }
    .header-right { margin-left: auto; }
    .logout-btn { background-color: #fff; border: 1px solid #ddd; padding: 8px 16px; border-radius: 6px; cursor: pointer; font-size: 14px; color: #555; transition: all 0.2s; font-weight: 500; }
    .logout-btn:hover { background-color: #ffeef0; color: #d6336c; border-color: #d6336c; }
    .content-area { padding: 0 48px 100px 48px; }
    .full-page { padding: 0 48px 100px 48px; display: block; }
    .card { background-color: #fff; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.05); overflow: hidden; }
    .full-page-card { width: 100%; background: #fff; margin-top: 10px; }
    .sub-nav-container { display: flex; gap: 24px; margin-bottom: 16px; border-bottom: 1px solid #e0e4f0; padding-bottom: 0; }
    .sub-nav-btn { background: none; border: none; padding: 12px 4px; font-size: 16px; color: #888; cursor: pointer; font-weight: 600; position: relative; transition: color 0.2s; }
    .sub-nav-btn:hover { color: #3c66f7; }
    .sub-nav-btn.active { color: #3c66f7; }
    .sub-nav-btn.active::after { content: ''; position: absolute; bottom: -1px; left: 0; width: 100%; height: 3px; background-color: #3c66f7; border-radius: 3px 3px 0 0; }

    /* ★ 추가된 대시보드 스타일 */
    .stats-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-bottom: 24px; }
    .stat-card { background: white; padding: 24px; border-radius: 12px; box-shadow: 0 2px 12px rgba(0,0,0,0.05); }
    .stat-card h4 { margin: 0 0 12px 0; color: #666; font-size: 14px; }
    .count { font-size: 32px; font-weight: bold; }
    .count .unit { font-size: 16px; color: #333; font-weight: normal; }
    .blue { color: #3c66f7; } .orange { color: #f08c00; } .green { color: #2b8a3e; }

    .card-padding { padding: 24px; }
    .table-title { font-size: 16px; font-weight: bold; margin-bottom: 16px; }
    table { width: 100%; border-collapse: collapse; font-size: 14px; text-align: center; }
    th { background: #f8f9fa; padding: 12px; font-weight: 600; color: #555; border-bottom: 1px solid #eee; }
    td { padding: 14px 12px; border-bottom: 1px solid #f5f5f5; color: #333; vertical-align: middle; }
    .empty-msg { padding: 40px; color: #999; }
    .type-badge { background: #f1f3f5; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: 600; color: #495057; }
    .text-left { text-align: left; }
    .date-col { font-family: monospace; font-size: 13px; color: #555; }
    .action-btns { display: flex; justify-content: center; gap: 6px; }
    .btn-approve, .btn-reject { padding: 6px 12px; border-radius: 4px; border: 1px solid #ddd; background: white; cursor: pointer; font-size: 12px; font-weight: 600; }
    .btn-approve { color: #2b8a3e; border-color: #2b8a3e; }
    .btn-approve:hover { background-color: #ebfbee; }
    .btn-reject { color: #fa5252; border-color: #fa5252; }
    .btn-reject:hover { background-color: #fff5f5; }
</style>