<script lang="ts">
    import { onMount, createEventDispatcher } from 'svelte';

    const dispatch = createEventDispatcher();

    let employeeId = 'EN202501';
    let summary = { used: 0.0, remaining: 15.0 };
    
    let leaveTypes = [
        { name: '연차휴가', typeCode: 'annual', total: 15, used: 0, remaining: 15 },
        { name: '경조사휴가', typeCode: 'family', total: 0, used: 0, remaining: 0 },
        { name: '병가휴가', typeCode: 'sick', total: 0, used: 0, remaining: 0 },
        { name: '공가 휴가', typeCode: 'official', total: 0, used: 0, remaining: 0 },
    ];

    onMount(() => {
        const savedId = localStorage.getItem("savedUsername");
        if (savedId) employeeId = savedId;
        fetchLeaveData();
    });

    async function fetchLeaveData() {
        try {
            let totalLeaves = 15.0;
            try {
                const resEmp = await fetch(`http://127.0.0.1:8000/api/employees/${employeeId}`);
                if (resEmp.ok) {
                    const empData = await resEmp.json();
                    if (empData.total_leave_days) totalLeaves = empData.total_leave_days;
                }
            } catch (e) { console.log("직원 정보 로드 실패, 기본값 사용"); }

            const resApp = await fetch(`http://127.0.0.1:8000/api/applications/recent/${employeeId}`);
            if (resApp.ok) {
                const apps = await resApp.json();
                const approvedApps = apps.filter((app: any) => app.status === '승인');

                let usedTotal = 0;
                
                // 데이터 초기화
                const newLeaveTypes = leaveTypes.map(type => ({ ...type, total: 0, used: 0, remaining: 0 }));
                newLeaveTypes[0].total = totalLeaves; 

                approvedApps.forEach((app: any) => {
                    const duration = parseFloat(app.duration) || 0;
                    usedTotal += duration;
                    
                    if (app.type.includes('연차') || app.type.includes('반차')) {
                        newLeaveTypes[0].used += duration;
                    } else if (app.type.includes('경조사')) {
                        newLeaveTypes[1].used += duration;
                    } else if (app.type.includes('병가')) {
                        newLeaveTypes[2].used += duration;
                    } else if (app.type.includes('공가')) {
                        newLeaveTypes[3].used += duration;
                    }
                });

                newLeaveTypes.forEach(type => {
                    type.remaining = type.total - type.used;
                });
                leaveTypes = newLeaveTypes;

                summary = {
                    used: usedTotal,
                    remaining: totalLeaves - usedTotal
                };
            }
        } catch (error) {
            console.error("데이터 로딩 중 에러:", error);
        }
    }
</script>

<div class="leave-container">
    <div class="header">
        <button class="back-btn" on:click={() => dispatch('goBack')}>
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="15 18 9 12 15 6"></polyline>
            </svg>
        </button>
        <h2>휴가</h2>
    </div>

    <div class="summary-card">
        <p class="summary-text">
            사용한 휴가는 <span class="highlight">{summary.used.toFixed(1)}일</span>입니다.
        </p>
        <div class="icon-wrapper">
            🏖️
        </div>
    </div>

    <div class="section-title">나의 휴가</div>

    <div class="leave-list">
        {#each leaveTypes as type}
        <div class="leave-item {type.typeCode}">
            <div class="leave-info">
                <div class="leave-name">{type.name}</div>
                {#if type.total > 0}
                    <div class="leave-detail">
                        {type.remaining.toFixed(1)}일 신청 가능합니다.
                    </div>
                {/if}
                <div class="leave-used">
                    ✓ 사용 : {type.used.toFixed(1)}일
                </div>
            </div>
        </div>
        {/each}
    </div>
</div>

<style>
    .leave-container {
        background-color: #fff;
        padding: 24px;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.05);
    }

    .header {
        display: flex;
        align-items: center;
        justify-content: center; 
        position: relative;
        margin-bottom: 24px;
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
    .header h2 {
        font-size: 20px;
        font-weight: bold;
        margin: 0;
    }
    
    .summary-card {
        background-color: #f4f7fe;
        border-radius: 12px;
        padding: 24px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 24px;
    }
    .summary-text { font-size: 16px; color: #333; }
    .highlight { color: #2196f3; font-weight: bold; font-size: 20px; }
    .icon-wrapper {
        font-size: 40px;
        background-color: #fff;
        border-radius: 50%;
        width: 64px;
        height: 64px;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }

    .section-title {
        font-size: 18px;
        font-weight: bold;
        margin-bottom: 16px;
    }

    .leave-list {
        display: flex;
        flex-direction: column;
        gap: 16px;
    }

    .leave-item {
        border-radius: 12px;
        padding: 24px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        transition: transform 0.2s, box-shadow 0.2s;
        border: none; 
    }
    .leave-item:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }

    .leave-item.annual {
        background-color: #e7f5ff; 
    }
    .leave-item.family {
        background-color: #e6fcf5; 
    }
    .leave-item.sick {
        background-color: #fff9db; 
    }
    .leave-item.official {
        background-color: #f3f0ff; 
    }

    .leave-name {
        font-weight: bold;
        font-size: 17px;
        margin-bottom: 8px;
        color: #333; 
    }
    .leave-detail {
        color: #555; 
        font-size: 14px;
        margin-bottom: 4px;
    }
    .leave-used {
        color: #888; 
        font-size: 13px;
        font-weight: 500;
    }
</style>