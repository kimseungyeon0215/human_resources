<script>
    import Login from '$lib/components/Login.svelte';
    import { goto } from '$app/navigation';

    // 로그인 성공하면 메인으로 이동
    function handleLoginSuccess() {
        goto('/');
    }
</script>

<Login on:loginSuccess={handleLoginSuccess} />