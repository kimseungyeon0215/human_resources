<script lang="ts">
    import { onMount } from 'svelte';

    let currentDate = new Date(); 
    let viewMode = 'monthly'; 
    
    let dateDisplayText = ""; 

    let leaveList: any[] = [];
    let summary: any = {}; 

    onMount(() => {
        updateDateDisplay();
        fetchSchedule();
    });

    // 날짜 범위 계산, 텍스트 업데이트
    function updateDateDisplay() {
        const year = currentDate.getFullYear();
        const month = String(currentDate.getMonth() + 1).padStart(2, '0');
        const day = String(currentDate.getDate()).padStart(2, '0');

        if (viewMode === 'monthly') {
            dateDisplayText = `${year}.${month}`;
        } else if (viewMode === 'daily') {
            dateDisplayText = `${year}.${month}.${day}`;
        } else if (viewMode === 'weekly') {
            // 이번 주 일요일 ~ 토요일 계산
            const curr = new Date(currentDate);
            const first = curr.getDate() - curr.getDay(); // 일요일
            const last = first + 6; // 토요일

            const firstDay = new Date(curr.setDate(first));
            const lastDay = new Date(curr.setDate(last));

            const fMonth = String(firstDay.getMonth() + 1).padStart(2, '0');
            const fDate = String(firstDay.getDate()).padStart(2, '0');
            const lMonth = String(lastDay.getMonth() + 1).padStart(2, '0');
            const lDate = String(lastDay.getDate()).padStart(2, '0');

            dateDisplayText = `${firstDay.getFullYear()}.${fMonth}.${fDate} ~ ${lMonth}.${lDate}`;
        }
    }

    async function fetchSchedule() {
        const format = (d: Date) => {
            return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
        };

        let query = "";

        if (viewMode === 'monthly') {
            const y = currentDate.getFullYear();
            const m = currentDate.getMonth() + 1;
            query = `year=${y}&month=${m}`;
        } 
        else if (viewMode === 'daily') {
            const dStr = format(currentDate);
            query = `start=${dStr}&end=${dStr}`;
        } 
        else if (viewMode === 'weekly') {
            const curr = new Date(currentDate);
            const first = curr.getDate() - curr.getDay(); // 일요일
            const last = first + 6; // 토요일
            
            const start = new Date(curr.setDate(first));
            const end = new Date(new Date(start).setDate(start.getDate() + 6)); // 시작 기준 6일 뒤

            query = `start=${format(start)}&end=${format(end)}`;
        }

        try {
            const res = await fetch(`http://127.0.0.1:8000/api/leaves/schedule?${query}`);
            if (res.ok) {
                leaveList = await res.json();
                calculateSummary();
            } else {
                console.error("휴가 일정 로드 실패");
            }
        } catch (e) {
            console.error(e);
        }
    }

    function calculateSummary() {
        const counts: {[key: string]: number} = {};
        leaveList.forEach(item => {
            const type = item.type || "기타";
            counts[type] = (counts[type] || 0) + 1;
        });
        summary = counts;
    }

    // 날짜 이동 (< > 버튼)
    function moveDate(step: number) {
        if (viewMode === 'monthly') {
            currentDate.setMonth(currentDate.getMonth() + step);
        } else if (viewMode === 'weekly') {
            currentDate.setDate(currentDate.getDate() + (step * 7));
        } else if (viewMode === 'daily') {
            currentDate.setDate(currentDate.getDate() + step);
        }
        currentDate = new Date(currentDate); 
        updateDateDisplay();
        fetchSchedule();
    }

    function changeView(mode: string) {
        viewMode = mode;
        currentDate = new Date(); 
        updateDateDisplay();
        fetchSchedule();
    }
</script>

<div class="dashboard-container">
    <h2 class="page-title">휴가일정조회</h2>

    <div class="controls-header">
        <div class="date-navigator">
            <button class="nav-btn" on:click={() => moveDate(-1)}>&lt;</button>
            <span class="current-date">{dateDisplayText}</span>
            <button class="nav-btn" on:click={() => moveDate(1)}>&gt;</button>
        </div>
        
        <div class="view-buttons">
            <button class="view-btn {viewMode === 'daily' ? 'active' : ''}" on:click={() => changeView('daily')}>오늘</button>
            <button class="view-btn {viewMode === 'weekly' ? 'active' : ''}" on:click={() => changeView('weekly')}>주간</button>
            <button class="view-btn {viewMode === 'monthly' ? 'active' : ''}" on:click={() => changeView('monthly')}>월간</button>
        </div>
    </div>

    <div class="summary-text">
        {#if Object.keys(summary).length === 0}
            <span class="summary-item">일정이 없습니다.</span>
        {:else}
            {#each Object.entries(summary) as [type, count]}
                <span class="summary-item" class:red-text={type.includes('취소')}>
                    [{type}] {count}명
                </span>
            {/each}
        {/if}
    </div>

    <div class="table-wrapper">
        <table>
            <thead>
                <tr>
                    <th>일자</th>
                    <th>이름</th>
                    <th>부서</th>
                    <th>직급</th>
                    <th>근태항목</th>
                    <th>신청구분</th>
                    <th>시작시간</th>
                    <th>종료시간</th>
                    <th>소요시간</th>
                    <th>상태</th>
                </tr>
            </thead>
            <tbody>
                {#if leaveList.length === 0}
                    <tr>
                        <td colspan="10" class="empty-msg">해당 기간에 휴가 일정이 없습니다.</td>
                    </tr>
                {:else}
                    {#each leaveList as item}
                    <tr>
                        <td>{item.date}</td>
                        <td class="font-bold">{item.name}</td>
                        <td>{item.dept}</td>
                        <td>{item.rank}</td>
                        <td class="{item.item === '휴가취소' ? 'text-red' : 'text-orange'} font-bold">
                            {item.item}
                        </td>
                        <td>{item.type}</td>
                        <td>{item.startTime}</td>
                        <td>{item.endTime}</td>
                        <td>{item.duration}</td>
                        <td>
                            <span class="status-badge">{item.status}</span>
                        </td>
                    </tr>
                    {/each}
                {/if}
            </tbody>
        </table>
    </div>
</div>

<style>
    .dashboard-container {
        background-color: #fff;
        border-radius: 8px;
        padding: 30px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.03);
    }
    .page-title { font-size: 20px; font-weight: bold; color: #333; margin-bottom: 24px; }

    .controls-header {
        display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;
        border-bottom: 1px solid #f0f0f0; padding-bottom: 15px;
    }
    .date-navigator { display: flex; align-items: center; gap: 15px; }
    .nav-btn { background: none; border: none; font-size: 18px; cursor: pointer; color: #888; }
    .current-date { font-size: 20px; font-weight: bold; color: #333; min-width: 100px; text-align: center; }
    
    .view-buttons { display: flex; gap: 5px; }
    .view-btn {
        padding: 6px 16px; border: 1px solid #ddd; background-color: #fff;
        border-radius: 4px; font-size: 13px; cursor: pointer; transition: all 0.2s;
    }
    .view-btn.active { background-color: #3c66f7; color: white; border-color: #3c66f7; }

    .summary-text { margin-bottom: 20px; font-size: 13px; color: #666; display: flex; gap: 15px; }
    .summary-item { display: inline-block; }
    .red-text { color: #fa5252; }

    .table-wrapper { overflow-x: auto; }
    table { width: 100%; border-collapse: collapse; font-size: 14px; text-align: center; }
    th { padding: 16px; background-color: #f9fafb; color: #555; font-weight: 600; border-bottom: 1px solid #eee; white-space: nowrap; }
    td { padding: 16px; border-bottom: 1px solid #f5f5f5; color: #333; white-space: nowrap; }
    
    .empty-msg { padding: 50px; color: #999; }
    .font-bold { font-weight: 600; }
    .text-orange { color: #fd7e14; }
    .text-red { color: #fa5252; }

    .status-badge {
        background-color: #e6fcf5; color: #0ca678; padding: 4px 10px; border-radius: 20px; font-size: 12px; font-weight: 600;
    }
</style>