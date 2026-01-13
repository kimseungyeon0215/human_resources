<script lang="ts">
    import { onMount, createEventDispatcher } from 'svelte';
    import { goto } from '$app/navigation'; 
    import { user } from '$lib/stores'; 

    const dispatch = createEventDispatcher();

    let username = "";
    let password = "";
    let rememberMe = false;
    let isLoading = false; 

    onMount(() => {
        const savedId = localStorage.getItem("savedUsername");
        const savedPw = localStorage.getItem("savedPassword");

        if (savedId && savedPw) {
            username = savedId;
            password = savedPw;
            rememberMe = true;
        }
    });

    async function attemptLogin() {
        if (!username || !password) {
            alert("아이디와 비밀번호를 입력해주세요.");
            return;
        }

        isLoading = true; 

        try {
            const params = new URLSearchParams();
            params.append('username', username);
            params.append('password', password);

            const response = await fetch('http://localhost:8000/api/auth/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: params
            });

            if (response.ok) {
                const data = await response.json();
                
                localStorage.setItem('access_token', data.access_token);
                localStorage.setItem('user_id', username);

                user.set({
                    id: username,
                    name: data.name || username,
                    role: data.role || 'user'
                });

                if (rememberMe) {
                    localStorage.setItem("savedUsername", username);
                    localStorage.setItem("savedPassword", password);
                } else {
                    localStorage.removeItem("savedUsername");
                    localStorage.removeItem("savedPassword");
                }

                alert(`${data.name || username}님 환영합니다!`); 
                
                dispatch('loginSuccess'); 
                goto('/'); 

            } else {
                alert("로그인 실패: 아이디 또는 비밀번호를 확인해주세요.");
            }
        } catch (error) {
            console.error(error);
            alert("서버 연결 실패: 백엔드 서버가 켜져 있는지 확인해주세요.");
        } finally {
            isLoading = false; 
        }
    }
</script>

<div class="login-background">
    <div class="login-card">
        <div class="avatar-circle">
            <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4"/><polyline points="10 17 15 12 10 7"/><line x1="15" y1="12" x2="3" y2="12"/></svg>
        </div>
        
        <h2 class="login-title">근태관리 시스템</h2>

        <div class="input-group">
            <span class="icon">
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>
            </span>
            <input type="text" placeholder="사원번호 (ID)" bind:value={username} disabled={isLoading}>
        </div>
        
        <div class="input-group">
            <span class="icon">
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 10 0v4"></path></svg>
            </span>
            <input type="password" placeholder="비밀번호" bind:value={password} on:keydown={(e) => e.key === 'Enter' && attemptLogin()} disabled={isLoading}>
        </div>

        <div class="options">
            <label class="checkbox-label">
                <input type="checkbox" bind:checked={rememberMe}> 로그인 정보 기억하기
            </label>
        </div>
        
        <button on:click={attemptLogin} disabled={isLoading}>
            {#if isLoading}로그인 중...{:else}로그인{/if}
        </button>
    </div>
</div>

<style>
    .login-background { 
        display: flex; 
        justify-content: center; 
        align-items: center; 
        width: 100vw;
        min-height: 100vh;
        margin: 0;
        padding: 0;
        background-color: #f4f7fe; 
        box-sizing: border-box;
        font-family: 'Pretendard', sans-serif;
    }

    .login-card { 
        width: 380px; 
        padding: 48px 40px; 
        background: #ffffff; 
        border-radius: 16px; 
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05); 
        text-align: center; 
        border: 1px solid #f0f0f0;
    }

    .avatar-circle { 
        width: 64px; 
        height: 64px; 
        border-radius: 50%; 
        background-color: #f0f4ff; 
        margin: 0 auto 20px auto; 
        display: flex; 
        justify-content: center; 
        align-items: center; 
        color: #3c66f7; 
    }

    .login-title {
        font-size: 20px;
        font-weight: bold;
        color: #333;
        margin: 0 0 32px 0;
    }

    .input-group { position: relative; margin-bottom: 20px; }
    
    .input-group .icon { 
        position: absolute; 
        left: 16px; 
        top: 50%; 
        transform: translateY(-50%); 
        color: #3c66f7;
        opacity: 0.8;
    }

    .input-group input { 
        width: 100%; 
        padding: 14px 14px 14px 44px; 
        border: 1px solid #e0e0e0; 
        border-radius: 8px; 
        background-color: #fff; 
        box-sizing: border-box; 
        font-size: 15px;
        transition: border-color 0.2s;
        outline: none;
    }

    .input-group input:focus {
        border-color: #3c66f7;
        box-shadow: 0 0 0 3px rgba(60, 102, 247, 0.1);
    }
    
    .options { 
        display: flex; 
        justify-content: flex-start; 
        align-items: center; 
        font-size: 14px; 
        margin-bottom: 32px; 
        color: #666; 
        padding-left: 2px;
    }
    
    .checkbox-label { display: flex; align-items: center; cursor: pointer; }
    .checkbox-label input { margin-right: 8px; accent-color: #3c66f7; }

    button { 
        width: 100%; 
        padding: 14px; 
        border: none; 
        border-radius: 8px; 
        background-color: #3c66f7; 
        color: white; 
        font-size: 16px; 
        font-weight: 600; 
        cursor: pointer; 
        transition: background-color 0.2s; 
    }
    
    button:hover:not(:disabled) { background-color: #254eda; }
    button:disabled { background-color: #a0b1f0; cursor: not-allowed; }
</style>