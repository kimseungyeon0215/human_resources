<script>
    // 부모 컴포넌트(MyPage.svelte)로부터 데이터를 전달받기 위한 변수 선언
    export let currentTime = "";
    export let workTimer = "00:00:00";
</script>

<div class="card status-card">
    <div class="time-section">
        <p>{currentTime}</p>
        <h2>{workTimer}</h2>
        <div class="status-buttons">
            <button class="btn-check-in">출근</button>
            <button class="btn-check-out">퇴근</button>
        </div>
    </div>
    <div class="summary-section">
        <p>내가 작성한 근태계</p>
        <ul>
            <li><span>일반/연장</span><strong>-</strong></li>
            <li><span>남은휴가</span><strong>12일</strong></li>
            <li><span>이석/외출근태</span><strong>10건</strong></li>
        </ul>
    </div>
</div>

<style>
    .card { background-color: #fff; border-radius: 12px; padding: 24px; box-shadow: 0 4px 20px rgba(0,0,0,0.05); }
    .status-card { display: flex; align-items: center; justify-content: space-around; }
    .time-section h2 { font-size: 48px; font-weight: 300; margin: 8px 0; }
    .status-buttons button { padding: 8px 24px; border-radius: 20px; border: 1px solid #ddd; margin-right: 8px; cursor: pointer; }
    .summary-section ul { list-style: none; padding: 0; }
    .summary-section li { display: flex; justify-content: space-between; min-width: 180px; margin: 12px 0; }
</style>