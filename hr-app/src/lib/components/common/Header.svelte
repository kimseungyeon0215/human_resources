<script lang="ts">
    import { onMount } from 'svelte';
    import { user } from '$lib/stores';
    import { goto } from '$app/navigation';
    import { page } from '$app/stores';

    onMount(() => {
        const token = localStorage.getItem('access_token');
        const savedId = localStorage.getItem('user_id');

        // 토큰은 있는데 스토어가 비어있다면? -> 다시 채워넣어서 "로그인 상태"로 만듦
        if (token && savedId && !$user) {
            user.set({
                id: savedId,
                name: savedId, // 이름은 일단 ID로 표시
                role: 'user'
            });
        }
    });

    // 로그아웃 기능
    function handleLogout() {
        if (confirm("로그아웃 하시겠습니까?")) {
            // 1. 저장된 정보 싹 지우기
            localStorage.removeItem('access_token');
            localStorage.removeItem('user_id');
            
            // 2. 스토어 비우기
            user.set(null);
            
            // 3. 로그인 페이지로 이동 -> layout 설정 덕분에 '꽉 찬 화면'으로 나옴
            goto('/login');
        }
    }
</script>

<header class="page-header">
    <div class="header-left">
        <h1><a href="/" class="logo-link">근태관리</a></h1>
        <nav class="main-nav">
            <a href="/" class:active={$page.url.searchParams.get('view') === null}>마이페이지</a>
            <a href="/?view=attendance" class:active={$page.url.searchParams.get('view') === 'attendance'}>출퇴근기록</a>
            <a href="/?view=leave" class:active={$page.url.searchParams.get('view') === 'leave'}>휴가관리</a>
            
            <a href="/admin" class="admin-link">관리자</a>
        </nav>
    </div>

    <div class="header-right">
        {#if $user}
            <span class="user-info">
                <strong class="text-primary">{$user.name}</strong>님
            </span>
            <button class="logout-btn" on:click={handleLogout}>로그아웃</button>
        {:else}
            <a href="/login" class="login-link">로그인</a>
        {/if}
    </div>
</header>

<style>
    .page-header { display: flex; align-items: center; justify-content: space-between; padding: 0 20px; margin-bottom: 24px; height: 60px; border-bottom: 1px solid #eee; background-color: #fff; }
    .header-left { display: flex; align-items: center; }
    .page-header h1 { font-size: 24px; font-weight: bold; margin-right: 40px; margin-bottom: 0; }
    .logo-link { text-decoration: none; color: #333; }
    
    .main-nav a { margin: 0 15px; color: #555; text-decoration: none; font-size: 15px; transition: color 0.2s; }
    .main-nav a:hover, .main-nav a.active { color: #3c66f7; font-weight: bold; }

    .admin-link { color: #e03131 !important; font-weight: bold; }

    .header-right { display: flex; align-items: center; gap: 15px; font-size: 14px; }
    .text-primary { color: #3c66f7; }
    
    /* 로그아웃 버튼 스타일 */
    .logout-btn { 
        background: white; 
        border: 1px solid #ddd; 
        padding: 5px 12px; 
        border-radius: 4px; 
        font-size: 13px; 
        color: #666; 
        cursor: pointer; 
        transition: all 0.2s;
    }
    .logout-btn:hover { 
        background-color: #f5f5f5; 
        color: #333; 
        border-color: #ccc;
    }
    
    .login-link { text-decoration: none; color: #3c66f7; font-weight: bold; }
</style>