<script lang="ts">
    import { onMount } from 'svelte';

    const today = new Date();
    const y = today.getFullYear();
    const m = String(today.getMonth() + 1).padStart(2, '0');
    const lastDay = new Date(y, today.getMonth() + 1, 0).getDate();

    let startDate = `${y}-${m}-01`;
    let endDate = `${y}-${m}-${lastDay}`;
    let searchQuery = "";
    
    let list: any[] = [];
    let totalCount = 0;

    onMount(() => {
        fetchList();
    });

    async function fetchList() {
        try {
            const params = new URLSearchParams({
                start: startDate,
                end: endDate,
                query: searchQuery
            });

            const res = await fetch(`http://127.0.0.1:8000/api/applications/list?${params.toString()}`);
            if (res.ok) {
                list = await res.json();
                totalCount = list.length;
            }
        } catch (e) {
            console.error(e);
        }
    }

    function getCategoryColor(category: string) {
        if (category === '외근') return 'text-blue';
        if (category === '연장') return 'text-purple';
        if (category === '출장') return 'text-orange';
        if (category === '휴가') return 'text-green';
        return '';
    }

    function getStatusClass(status: string) {
        if (status === '승인완료') return 'status-approved';
        if (status === '반려') return 'status-rejected';
        return 'status-pending';
    }

    // ★ [핵심 추가] 시간 표시 예쁘게 다듬기
    function formatTime(time: string, category: string) {
        if (!time) return '-';
        
        // 휴가 신청 등은 시간이 00:00이면 의미 없으므로 '-' 표시
        if (category === '휴가' && time === '00:00') {
            return '-';
        }
        
        // 그 외(연장근무 등)는 00:00이라도 보여줌 (자정 근무일 수 있으니)
        return time;
    }
</script>

<div class="list-container">
    <div class="header-filter">
        <div class="list-summary">
            [총 <strong>{totalCount}건</strong>] {startDate} ~ {endDate} 근태신청내역
        </div>
        
        <div class="search-box">
            <span class="label">기간</span>
            <input type="date" bind:value={startDate} /> ~ <input type="date" bind:value={endDate} />
            <input type="text" placeholder="이름 검색" bind:value={searchQuery} class="text-search" />
            <button class="search-btn" on:click={fetchList}>검색</button>
        </div>
    </div>

    <div class="toolbar">
        <button class="tool-btn">전체</button>
        <button class="tool-btn icon">☰</button>
    </div>

    <div class="table-wrapper">
        <table>
            <thead>
                <tr>
                    <th>일자</th><th>이름</th><th>부서</th><th>직급</th>
                    <th>근태항목</th><th>신청구분</th><th>시작시간</th><th>종료시간</th>
                    <th>소요시간</th><th>상태</th>
                </tr>
            </thead>
            <tbody>
                {#if list.length === 0}
                    <tr><td colspan="10" class="empty-msg">내역이 없습니다.</td></tr>
                {:else}
                    {#each list as item}
                    <tr>
                        <td>{item.date}</td>
                        <td class="font-bold">{item.name}</td>
                        <td>{item.dept}</td>
                        <td>{item.rank}</td>
                        <td class="font-bold {getCategoryColor(item.category)}">{item.category}</td>
                        <td>{item.type}</td>
                        
                        <td>{formatTime(item.startTime, item.category)}</td>
                        <td>{formatTime(item.endTime, item.category)}</td>
                        
                        <td>{item.duration}</td>
                        <td>
                            <span class="status-badge {getStatusClass(item.status)}">{item.status}</span>
                        </td>
                    </tr>
                    {/each}
                {/if}
            </tbody>
        </table>
    </div>
</div>

<style>
    /* 스타일은 기존 그대로 유지 */
    .list-container { background-color: #fff; padding: 24px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.03); }
    .header-filter { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; flex-wrap: wrap; gap: 10px; }
    .list-summary { font-size: 15px; color: #333; font-weight: 600; }
    .list-summary strong { color: #3c66f7; }
    .search-box { display: flex; align-items: center; gap: 8px; }
    .label { font-size: 13px; color: #666; font-weight: 600; margin-right: 4px; }
    input[type="date"], .text-search { padding: 6px 10px; border: 1px solid #ddd; border-radius: 4px; font-size: 13px; }
    .text-search { width: 120px; }
    .search-btn { background-color: #333; color: white; border: none; padding: 6px 14px; border-radius: 4px; cursor: pointer; font-size: 13px; }
    .toolbar { display: flex; justify-content: flex-end; gap: 6px; margin-bottom: 10px; }
    .tool-btn { background-color: #fff; border: 1px solid #ddd; padding: 4px 10px; border-radius: 4px; font-size: 12px; cursor: pointer; color: #555; }
    .table-wrapper { overflow-x: auto; border-top: 1px solid #eee; }
    table { width: 100%; border-collapse: collapse; font-size: 13px; text-align: center; }
    th { padding: 14px 8px; background-color: #f9fafb; color: #555; font-weight: 600; border-bottom: 1px solid #eee; white-space: nowrap; }
    td { padding: 14px 8px; border-bottom: 1px solid #f5f5f5; color: #333; vertical-align: middle; white-space: nowrap; }
    .font-bold { font-weight: 600; }
    .text-blue { color: #339af0; } .text-purple { color: #7950f2; } .text-orange { color: #fd7e14; } .text-green { color: #40c057; }
    .status-badge { padding: 4px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; }
    .status-approved { background-color: #ebfbee; color: #2b8a3e; border: 1px solid #d3f9d8; }
    .status-rejected { background-color: #fff5f5; color: #fa5252; border: 1px solid #ffe3e3; }
    .status-pending { background-color: #fff9db; color: #f08c00; border: 1px solid #ffec99; }
    .empty-msg { padding: 40px; color: #999; }
</style>