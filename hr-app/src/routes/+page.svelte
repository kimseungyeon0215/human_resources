<script lang="ts">
    import { onMount } from 'svelte';
    import { user } from '$lib/stores'; 
    import { page } from '$app/stores'; 
    import { goto } from '$app/navigation'; // 페이지 이동 도구

    import MyPage from '$lib/components/MyPage.svelte';
    import AttendanceLog from '$lib/components/attendance/AttendanceLog.svelte';
    import LeavePage from '$lib/components/LeavePage.svelte';
    
    import LeaveApplicationForm from '$lib/components/LeaveApplicationForm.svelte';
    import OvertimeApplicationForm from '$lib/components/OvertimeApplicationForm.svelte';
    import ExpenseClaimForm from '$lib/components/ExpenseClaimForm.svelte';

    let currentView = 'dashboard'; 

    // 주소창에 따라 화면 전환
    $: viewParam = $page.url.searchParams.get('view');
    $: {
        if (viewParam === 'attendance') currentView = 'attendance-log';
        else if (viewParam === 'leave') currentView = 'leave-info';
        else currentView = 'dashboard'; 
    }

    onMount(() => {
        const token = localStorage.getItem('access_token');
        
        if (!token) {
            goto('/login');
        }
    });

    function handleNavigation(event: CustomEvent) {
        const target = event.detail;
        if (target === 'leave-apply') currentView = 'leave';
        else if (target === 'overtime-apply') currentView = 'overtime';
        else if (target === 'expense-claim') currentView = 'expense-claim';
        else if (target === 'attendance-log') currentView = 'attendance-log';
        else if (target === 'leave-info') currentView = 'leave-info';
        window.scrollTo(0, 0);
    }

    function goBack() {
        window.location.href = "/";
    }
</script>

<div class="app-container">
    {#if currentView === 'dashboard'}
        <div class="content-area">
            <MyPage on:navigate={handleNavigation} />
        </div>

    {:else if currentView === 'attendance-log'}
        <div class="content-area full-page">
            <div class="card full-page-card">
                <AttendanceLog on:goBack={goBack} />
            </div>
        </div>

    {:else if currentView === 'leave-info'}
        <div class="content-area full-page">
            <div class="card full-page-card">
                <LeavePage on:goBack={goBack} />
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

<style>
    .app-container { font-family: 'Pretendard', sans-serif; background-color: #f4f7fe; min-height: calc(100vh - 60px); }
    .content-area { padding: 24px 48px 100px 48px; }
    .full-page { padding: 24px 48px 100px 48px; display: block; }
    .card { background-color: #fff; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.05); overflow: hidden; }
    .full-page-card { width: 100%; background: #fff; margin-top: 10px; }
</style>