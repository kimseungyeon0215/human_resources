<script lang="ts">
    import { onMount, createEventDispatcher } from 'svelte';

    const dispatch = createEventDispatcher();

    let employeeId = 'EN202501'; //나중에는 빈 문자열 ''로 두거나 해야 함!!!
    let leaveType = '연차';
    
    let startDate = new Date().toISOString().slice(0, 10);
    let endDate = new Date().toISOString().slice(0, 10);
    
    let reason = '';
    let files: FileList | null = null;

    onMount(() => {
        const savedId = localStorage.getItem("savedUsername");
        if (savedId) employeeId = savedId;
    });

    async function handleSubmit() {
        if (!reason) return alert("휴가 사유를 입력해주세요.");

        try {
            const response = await fetch('http://127.0.0.1:8000/api/applications', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    employee_id: employeeId,
                    application_type: leaveType,
                    start_date: startDate,
                    end_date: endDate,
                    reason: reason
                })
            });

            const result = await response.json();
            if (response.ok) {
                alert("휴가 신청이 완료되었습니다.");
                dispatch('goBack');
            } else {
                alert("신청 실패: " + result.detail);
            }
        } catch (error) {
            console.error(error);
            alert("서버 연결 오류");
        }
    }

    function handleCancel() {
        dispatch('goBack');
    }
</script>

<div class="card">
    <header class="form-header">
        <button class="back-btn" on:click={handleCancel}>
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="15 18 9 12 15 6"></polyline>
            </svg>
        </button>
        <h2>휴가 신청 작성</h2>
    </header>

    <form class="application-form" on:submit|preventDefault={handleSubmit}>
        <div class="form-group">
            <label for="leaveType">휴가 종류</label>
            <select id="leaveType" bind:value={leaveType}>
                <option value="연차">연차</option>
                <option value="오전반차">오전 반차</option>
                <option value="오후반차">오후 반차</option>
                <option value="병가">병가</option>
                <option value="경조사">경조사 휴가</option>
            </select>
        </div>

        <div class="form-group">
            <label for="leavePeriod">휴가 기간</label>
            <div class="date-range-wrapper">
                <input type="date" id="leavePeriod" bind:value={startDate}>
                <span>~</span>
                <input type="date" bind:value={endDate}>
            </div>
        </div>

        <div class="form-group">
            <label for="leaveReason">사유</label>
            <textarea id="leaveReason" rows="4" placeholder="휴가 사유를 입력하세요." bind:value={reason}></textarea>
        </div>
        
        <div class="form-group">
            <label for="leaveAttachment">증빙 파일</label>
            <input type="file" id="leaveAttachment" bind:files={files}>
        </div>

        <div class="form-actions">
            <button type="button" class="btn-cancel" on:click={handleCancel}>취소</button>
            <button type="submit" class="btn-submit">신청하기</button>
        </div>
    </form>
</div>

<style>
    .card { 
        background-color: #fff; 
        border-radius: 12px; 
        padding: 32px; 
        box-shadow: 0 4px 20px rgba(0,0,0,0.05); 
        width: 100%;
        box-sizing: border-box; 
    }
    
    .form-header { 
        display: flex; 
        align-items: center; 
        justify-content: center; 
        position: relative; 
        margin-bottom: 32px; 
    }
    .back-btn { 
        position: absolute; 
        left: 0; 
        background: none; 
        border: none; 
        cursor: pointer; 
        color: #666; 
        padding: 8px; 
    }
    .form-header h2 { 
        font-size: 20px; 
        font-weight: bold; 
        margin: 0; 
        color: #333; 
    }
    
    .application-form { display: flex; flex-direction: column; gap: 20px; }
    .form-group { display: flex; flex-direction: column; }
    .form-group label { font-weight: 600; margin-bottom: 8px; font-size: 14px; color: #333; }
    
    .form-group input,
    .form-group select,
    .form-group textarea {
        width: 100%;
        padding: 12px;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        font-size: 1rem;
        box-sizing: border-box; 
    }
    .date-range-wrapper { display: flex; align-items: center; gap: 12px; }
    .date-range-wrapper span { color: #9ca3af; }
    
    .form-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 16px; }
    .btn-submit {
        background-color: #3c66f7; color: white; padding: 12px 24px;
        border: none; border-radius: 8px; font-size: 1rem; font-weight: 600; cursor: pointer;
    }
    .btn-cancel {
        background-color: #f1f5f9; color: #475569; padding: 12px 24px;
        border: none; border-radius: 8px; font-size: 1rem; font-weight: 600; cursor: pointer;
    }
</style>