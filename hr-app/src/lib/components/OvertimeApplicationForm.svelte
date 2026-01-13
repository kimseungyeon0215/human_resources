<script lang="ts">
    import { onMount, createEventDispatcher } from 'svelte';
    import { user } from '$lib/stores'; // ★ 스토어 가져오기

    const dispatch = createEventDispatcher();

    // 초기값: 스토어 -> 로컬스토리지 -> 빈값
    let employeeId = '';
    let workType = '연장근무';
    
    let targetDate = new Date().toISOString().slice(0, 10);
    let startTime = '19:00';
    let endTime = '22:00';
    
    let reason = '';
    let files: FileList | null = null;

    onMount(() => {
        // 로그인한 사용자 ID 설정
        if ($user && $user.id) {
            employeeId = $user.id;
        } else {
            employeeId = localStorage.getItem('user_id') || '';
        }
    });

    async function handleSubmit() {
        if (!reason) return alert("근무 사유를 입력해주세요.");

        // ★ [핵심 수정] 날짜와 시간을 합쳐서 'YYYY-MM-DD HH:mm' 포맷으로 만듦
        const startDateTime = `${targetDate} ${startTime}`;
        const endDateTime = `${targetDate} ${endTime}`;

        try {
            const response = await fetch('http://127.0.0.1:8000/api/applications', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    employee_id: employeeId,
                    application_type: workType,
                    // ★ 날짜만 보내던 것을 '날짜+시간'으로 변경
                    start_date: startDateTime, 
                    end_date: endDateTime,
                    reason: reason 
                })
            });

            const result = await response.json();
            if (response.ok) {
                alert("연장근무 신청이 완료되었습니다.");
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
        <h2>연장근무 신청 작성</h2>
    </header>

    <form class="application-form" on:submit|preventDefault={handleSubmit}>
        <div class="form-group">
            <label for="workType">근무 종류</label>
            <select id="workType" bind:value={workType}>
                <option value="연장근무">연장근무</option>
                <option value="야간근무">야간근무</option>
                <option value="휴일근무">휴일근무</option>
            </select>
        </div>

        <div class="form-group">
            <label for="workDate">근무 일시</label>
            <div class="date-range-wrapper">
                <input type="date" id="workDate" bind:value={targetDate} style="flex: 1;">
                <div class="time-inputs">
                    <input type="time" bind:value={startTime}>
                    <span>~</span>
                    <input type="time" bind:value={endTime}>
                </div>
            </div>
        </div>

        <div class="form-group">
            <label for="workReason">사유</label>
            <textarea id="workReason" rows="4" placeholder="근무 내용 및 사유를 입력하세요." bind:value={reason}></textarea>
        </div>
        
        <div class="form-group">
            <label for="workAttachment">증빙 파일</label>
            <input type="file" id="workAttachment" bind:files={files}>
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
    
    .form-group input, .form-group select, .form-group textarea {
        width: 100%; padding: 12px; border: 1px solid #e2e8f0; border-radius: 8px; font-size: 1rem; box-sizing: border-box;
    }
    
    .date-range-wrapper { display: flex; gap: 12px; flex-wrap: wrap; }
    .time-inputs { display: flex; align-items: center; gap: 12px; flex: 2; }
    .time-inputs span { color: #9ca3af; }
    .time-inputs input { min-width: 100px; }

    .form-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 16px; }
    .btn-submit { background-color: #3c66f7; color: white; padding: 12px 24px; border: none; border-radius: 8px; font-size: 1rem; font-weight: 600; cursor: pointer; }
    .btn-cancel { background-color: #f1f5f9; color: #475569; padding: 12px 24px; border: none; border-radius: 8px; font-size: 1rem; font-weight: 600; cursor: pointer; }
</style>