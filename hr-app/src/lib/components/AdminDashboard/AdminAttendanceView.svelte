<script lang="ts">
    import { onMount } from 'svelte';

    // UTC(표준시)가 아닌 사용자의 한국 시간 기준으로 오늘 날짜를 가져옴
    const getToday = () => {
        const now = new Date();
        const year = now.getFullYear();
        const month = String(now.getMonth() + 1).padStart(2, '0');
        const day = String(now.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
    };

    let historyDate = getToday(); 
    
    let records: any[] = [];
    
    let displayDate = historyDate;

    let summaryCounts = { total: 0, normal: 0, issue: 0 };

    onMount(() => {
        fetchHistory();
    });

    // 출퇴근 내역 조회 
    async function fetchHistory() {
        try {
            const res = await fetch(`http://127.0.0.1:8000/api/attendance/all?date=${historyDate}`);
            if (res.ok) {
                records = await res.json();
                
                displayDate = historyDate;

                summaryCounts = {
                    total: records.length,
                    normal: records.filter((r: any) => r.status === '정상처리').length,
                    issue: records.filter((r: any) => r.status === '지각' || r.status === '결근' || r.status === '퇴근미처리').length
                };
            }
        } catch (e) { console.error("출퇴근 내역 로드 실패", e); }
    }

    // 화살표 버튼 클릭 시 날짜 변경 함수
    function changeDate(offset: number) {
        const date = new Date(historyDate);
        date.setDate(date.getDate() + offset);
        
        // 날짜 변경 후에도 YYYY-MM-DD 형식으로 포맷팅 
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        historyDate = `${year}-${month}-${day}`;
        
        fetchHistory(); 
    }
</script>

<div class="container">
    <div class="header">
        <div class="title-section">
            <h4>[총 {summaryCounts.total}명]</h4>
            <div class="date-nav">
                <button class="arrow-btn" on:click={() => changeDate(-1)}>&lt;</button>
                <span>{displayDate} 출퇴근 내역</span>
                <button class="arrow-btn" on:click={() => changeDate(1)}>&gt;</button>
            </div>
        </div>
        <div class="top-filter">
            <span class="label">날짜 선택</span>
            <input type="date" bind:value={historyDate} class="date-input" />
            <button class="btn search-btn" on:click={fetchHistory}>조회</button>
        </div>
    </div>
    
    <div class="summary-cards">
        <button class="card active">
            <div class="icon-wrapper total">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>
            </div>
            전체
        </button>
        <button class="card">
                <div class="icon-wrapper normal">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>
            </div>
            <span>정상출근 <strong class="count normal">{summaryCounts.normal}건</strong></span>
        </button>
        <button class="card">
                <div class="icon-wrapper issue">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>
            </div>
            <span>근태이상 <strong class="count issue">{summaryCounts.issue}건</strong></span>
        </button>
        </div>

    <div class="table-wrapper">
        <table>
            <thead>
                <tr>
                    <th>일자</th><th>이름</th><th>부서</th><th>직급</th>
                    <th>출근시각</th><th>출근위치</th><th>퇴근시각</th><th>퇴근위치</th><th>상태</th>
                </tr>
            </thead>
            <tbody>
                {#if records.length === 0}
                    <tr><td colspan="9" style="padding: 40px; color: #999;">해당 날짜의 기록이 없습니다.</td></tr>
                {:else}
                    {#each records as record, i}
                        <tr class:striped={i % 2 === 1}>
                            <td>{record.date}</td>
                            <td>{record.name}</td>
                            <td class="department">{record.dept}</td>
                            <td>{record.rank}</td>
                            <td>{record.in}</td>
                            <td>{record.inLoc}</td>
                            <td>{record.out}</td>
                            <td>{record.outLoc}</td>
                            <td>
                                {#if record.status && record.status !== '-'}
                                    <span class="status-badge">{record.status}</span>
                                {/if}
                            </td>
                        </tr>
                    {/each}
                {/if}
            </tbody>
        </table>
    </div>
</div>

<style>
    .container { padding: 24px; background-color: #fff; font-family: sans-serif; }

    .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
    .title-section { display: flex; align-items: center; gap: 16px; }
    .top-filter { display: flex; align-items: center; gap: 8px; }
    
    .label { font-size: 14px; }
    .date-input { border: 1px solid #ccc; border-radius: 4px; padding: 6px 10px; }
    .btn { border: 1px solid #ccc; background-color: #f8f9fa; border-radius: 4px; padding: 6px 12px; cursor: pointer; }
    .search-btn { background-color: #555; color: white; border-color: #555; }
    h4 { margin: 0; font-size: 14px; }
    .date-nav { display: flex; align-items: center; gap: 16px; font-size: 18px; font-weight: 500; }
    .arrow-btn { background: none; border: none; cursor: pointer; font-size: 20px; padding: 0 10px; color: #555; }
    .arrow-btn:hover { color: #000; }

    .summary-cards { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 16px; }
    .card { display: flex; align-items: center; gap: 12px; padding: 16px; border: 1px solid #e0e0e0; border-radius: 8px; background-color: #fff; font-size: 15px; cursor: pointer; }
    .card.active { background-color: #0d99ff; color: white; border-color: #0d99ff; }
    .card.active .icon-wrapper { background-color: white; }
    .card.active .icon-wrapper.total { color: #0d99ff; }
    .icon-wrapper { width: 40px; height: 40px; border-radius: 50%; display: grid; place-content: center; }
    .icon-wrapper.total { background-color: #e7f5ff; color: #0d99ff; }
    .icon-wrapper.normal { background-color: #e6f4ea; color: #38a169; }
    .icon-wrapper.issue { background-color: #fee2e2; color: #ef4444; }
    
    .count { font-weight: bold; }
    .count.normal { color: #38a169; }
    .count.issue { color: #ef4444; }
    
    .table-wrapper { overflow-x: auto; margin-top: 16px; }
    table { width: 100%; border-collapse: collapse; font-size: 14px; text-align: center; }
    th, td { padding: 12px; border: 1px solid #e9ecef; white-space: nowrap; }
    thead { background-color: #f8f9fa; }
    .striped { background-color: #f8f9fa; }
    .department { max-width: 200px; overflow: hidden; text-overflow: ellipsis; }
    .status-badge { background-color: #e6f4ea; color: #38a169; padding: 4px 10px; border-radius: 12px; font-size: 12px; }

</style>