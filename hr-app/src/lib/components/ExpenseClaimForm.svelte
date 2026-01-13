<script lang="ts">
    import { onMount, createEventDispatcher } from 'svelte';

    const dispatch = createEventDispatcher();

    let employeeId = 'EN202501'; //나중에는 빈 문자열 ''로 두거나 해야 함!!!
    let expenseDate = new Date().toISOString().slice(0, 10);
    let paymentMethod = '법인카드';
    let item = '';
    let amount = '';
    let details = '';
    let files: FileList | null = null;

    onMount(() => {
        const savedId = localStorage.getItem("savedUsername");
        if (savedId) employeeId = savedId;
    });

    async function handleSubmit() {
        if (!item || !amount) return alert("비용 항목과 금액을 입력해주세요.");

        try {
            const response = await fetch('http://127.0.0.1:8000/api/applications', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    employee_id: employeeId,
                    application_type: '비용처리',
                    start_date: expenseDate,
                    end_date: expenseDate,
                    reason: `[${paymentMethod}] ${item} - ${amount}원 / ${details}`
                })
            });

            const result = await response.json();
            if (response.ok) {
                alert("비용 처리 신청이 완료되었습니다.");
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
        dispatch('goBack'); // 취소 시 뒤로가기
    }
</script>

<div class="card">
    <header class="form-header">
        <button class="back-btn" on:click={handleCancel}>
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="15 18 9 12 15 6"></polyline>
            </svg>
        </button>
        <h2>비용 처리 신청</h2>
    </header>

    <form class="application-form" on:submit|preventDefault={handleSubmit}>
        
        <div class="form-row">
            <div class="form-group half">
                <label for="expenseDate">비용 발생일</label>
                <input type="date" id="expenseDate" bind:value={expenseDate}>
            </div>
            <div class="form-group half">
                <label for="paymentMethod">결제 수단</label>
                <select id="paymentMethod" bind:value={paymentMethod}>
                    <option value="법인카드">법인카드</option>
                    <option value="개인카드">개인카드</option>
                    <option value="현금">현금</option>
                </select>
            </div>
        </div>

        <div class="form-row">
            <div class="form-group half">
                <label for="expenseItem">비용 항목</label>
                <input type="text" id="expenseItem" placeholder="식대, 교통비 등" bind:value={item}>
            </div>
            <div class="form-group half">
                <label for="expenseAmount">금액</label>
                <input type="text" id="expenseAmount" placeholder="숫자만 입력하세요" bind:value={amount}>
            </div>
        </div>

        <div class="form-group">
            <label for="expenseDetails">상세 내용</label>
            <textarea id="expenseDetails" rows="4" placeholder="상세 사용 내역을 입력하세요." bind:value={details}></textarea>
        </div>
        
        <div class="form-group">
            <label for="expenseAttachment">증빙 파일 (영수증)</label>
            <input type="file" id="expenseAttachment" bind:files={files}>
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
        display: flex; align-items: center; justify-content: center; position: relative; margin-bottom: 32px; 
    }
    .back-btn { 
        position: absolute; left: 0; background: none; border: none; cursor: pointer; color: #666; padding: 8px; 
    }
    .form-header h2 { font-size: 20px; font-weight: bold; margin: 0; color: #333; }
    
    .application-form { display: flex; flex-direction: column; gap: 20px; }
    .form-group { display: flex; flex-direction: column; }
    
    .form-row { display: flex; gap: 20px; }
    .half { flex: 1; }

    .form-group label { font-weight: 600; margin-bottom: 8px; font-size: 14px; color: #333; }
    
    .form-group input, .form-group select, .form-group textarea {
        width: 100%; padding: 12px; border: 1px solid #e2e8f0; border-radius: 8px; font-size: 1rem; box-sizing: border-box;
    }
    
    .form-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 16px; }
    .btn-submit { background-color: #3c66f7; color: white; padding: 12px 24px; border: none; border-radius: 8px; font-size: 1rem; font-weight: 600; cursor: pointer; }
    .btn-cancel { background-color: #f1f5f9; color: #475569; padding: 12px 24px; border: none; border-radius: 8px; font-size: 1rem; font-weight: 600; cursor: pointer; }
</style>