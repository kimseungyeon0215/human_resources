<script lang="ts">
    import { onMount, createEventDispatcher } from 'svelte';

    const dispatch = createEventDispatcher();

    let pendingList: any[] = [];
    let summary = { leave: 0, overtime: 0, expense: 0 };

    onMount(() => {
        fetchPendingApplications();
    });

    function goBack() {
        dispatch('goBack');
    }

    async function fetchPendingApplications() {
        try {
            const res = await fetch('http://127.0.0.1:8000/api/applications');
            if (res.ok) {
                const data = await res.json();
                pendingList = data
                    .filter((app: any) => app.status === '대기' || app.status === 'Pending')
                    .sort((a: any, b: any) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
                calculateSummary();
            } else {
                console.error("데이터 로딩 실패 Status:", res.status);
            }
        } catch (error) {
            console.error("데이터 로딩 실패:", error);
        }
    }

    function calculateSummary() {
        summary = { leave: 0, overtime: 0, expense: 0 };
        pendingList.forEach(app => {
            const type = app.application_type || "";
            if (type.includes('휴가') || type.includes('반차') || type.includes('병가') || type.includes('연차')) {
                summary.leave++;
            } else if (type.includes('근무')) {
                summary.overtime++;
            } else if (type.includes('비용')) {
                summary.expense++;
            }
        });
    }

    async function handleProcess(id: string, newStatus: string) {
        if (!id) { alert("신청 ID를 찾을 수 없습니다."); return; }
        if (!confirm(`${newStatus} 처리 하시겠습니까?`)) return;

        try {
            const res = await fetch(`http://127.0.0.1:8000/api/applications/${id}/status`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ status: newStatus })
            });
            if (res.ok) {
                alert(`${newStatus} 처리되었습니다.`);
                fetchPendingApplications();
            } else {
                const err = await res.json();
                alert(`처리 실패: ${err.detail}`);
            }
        } catch (e) {
            console.error(e);
            alert("서버 통신 오류");
        }
    }
</script>

<div class="approval-container">
    
    <div class="header-row">
        <button class="back-btn" on:click={goBack} aria-label="뒤로 가기">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="15 18 9 12 15 6"></polyline>
            </svg>
        </button>
        <h2 class="page-title">관리자 결재 대기 현황</h2>
    </div>

    <div class="summary-row">
        <div class="summary-card">
            <span class="label">휴가 승인 요청</span>
            <strong class="count leave">{summary.leave} 건</strong>
        </div>
        <div class="summary-card">
            <span class="label">추가 근무 승인 요청</span>
            <strong class="count overtime">{summary.overtime} 건</strong>
        </div>
        <div class="summary-card">
            <span class="label">비용 처리 승인 요청</span>
            <strong class="count expense">{summary.expense} 건</strong>
        </div>
    </div>

    <h3 class="section-title">전체 결재 대기 목록</h3>
    <div class="table-wrapper">
        <table>
            <thead>
                <tr>
                    <th>구분</th>
                    <th>요청자(ID)</th>
                    <th>상세 내용</th>
                    <th>기간/일시</th>
                    <th>요청일</th>
                    <th>처리</th>
                </tr>
            </thead>
            <tbody>
                {#if pendingList.length === 0}
                    <tr><td colspan="6" class="empty-msg">대기 중인 결재 내역이 없습니다.</td></tr>
                {:else}
                    {#each pendingList as item}
                    <tr>
                        <td><span class="type-badge">{item.application_type}</span></td>
                        <td>{item.employee_name || item.employee_id}</td> 
                        <td class="text-left" title={item.reason}>
                            {item.reason ? (item.reason.length > 30 ? item.reason.slice(0,30)+'...' : item.reason) : '-'}
                        </td>
                        <td>
                            {item.start_date} {#if item.start_date !== item.end_date} ~ {item.end_date}{/if}
                        </td>
                        <td>{item.created_at ? item.created_at.slice(0, 10) : '-'}</td>
                        <td>
                            <div class="action-buttons">
                                <button class="btn-approve" on:click={() => handleProcess(item.application_id, '승인')}>승인</button>
                                <button class="btn-reject" on:click={() => handleProcess(item.application_id, '반려')}>반려</button>
                            </div>
                        </td>
                    </tr>
                    {/each}
                {/if}
            </tbody>
        </table>
    </div>
</div>

<style>
    .approval-container { padding: 10px; }
    
    
    .header-row { 
        position: relative; 
        display: flex;
        align-items: center;
        justify-content: center; 
        margin-bottom: 40px;
        height: 40px;
    }

    .back-btn {
        position: absolute; 
        left: 0;
        background: none;
        border: none;
        cursor: pointer;
        padding: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #555;
        transition: color 0.2s, background-color 0.2s;
        border-radius: 50%;
    }
    .back-btn:hover {
        background-color: #f5f5f5;
        color: #333;
    }

    .page-title { 
        font-size: 20px; 
        font-weight: bold; 
        color: #333; 
        margin: 0; 
    }
    
    .summary-row { display: flex; gap: 20px; margin-bottom: 40px; }
    .summary-card {
        flex: 1; background-color: #fff; border: 1px solid #eee; border-radius: 8px; padding: 24px; display: flex; flex-direction: column; gap: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.03);
    }
    .summary-card .label { font-size: 14px; color: #666; font-weight: 600; }
    .summary-card .count { font-size: 28px; font-weight: bold; }
    .count.leave { color: #3c66f7; } .count.overtime { color: #f59f00; } .count.expense { color: #0ca678; }

    .section-title { font-size: 16px; font-weight: bold; margin-bottom: 16px; color: #333; }
    .table-wrapper { overflow-x: auto; border: 1px solid #eee; border-radius: 8px; }
    table { width: 100%; border-collapse: collapse; background-color: #fff; font-size: 14px; }
    th { background-color: #f8f9fa; color: #555; font-weight: 600; padding: 16px; text-align: center; border-bottom: 1px solid #eee; white-space: nowrap; }
    td { padding: 16px; border-bottom: 1px solid #f5f5f5; text-align: center; color: #333; vertical-align: middle; white-space: nowrap; }
    .text-left { text-align: left; }
    .empty-msg { padding: 40px; color: #888; text-align: center; }

    .type-badge { background-color: #f1f3f5; padding: 4px 8px; border-radius: 4px; font-size: 12px; color: #495057; font-weight: 600; }
    .action-buttons { display: flex; gap: 8px; justify-content: center; }
    .btn-approve { background-color: #fff; border: 1px solid #2b8a3e; color: #2b8a3e; padding: 6px 12px; border-radius: 4px; cursor: pointer; font-weight: 600; font-size: 13px; transition: all 0.2s; }
    .btn-approve:hover { background-color: #ebfbee; }
    .btn-reject { background-color: #fff; border: 1px solid #e03131; color: #e03131; padding: 6px 12px; border-radius: 4px; cursor: pointer; font-weight: 600; font-size: 13px; transition: all 0.2s; }
    .btn-reject:hover { background-color: #fff5f5; }
</style>