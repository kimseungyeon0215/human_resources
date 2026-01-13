<script>
  import { page } from '$app/stores'; 
  import Header from '$lib/components/common/Header.svelte';
</script>

{#if $page.url.pathname !== '/login' && !$page.url.pathname.startsWith('/admin')}
  <Header />
{/if}

{#if $page.url.pathname === '/login'}
  <div class="login-wrapper">
    <slot />
  </div>
{:else}
  <div class="main-content">
    <slot />
  </div>
{/if}

<style>
  :global(body) {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
    overflow-x: hidden;
  }

  .login-wrapper {
    width: 100vw;
    height: 100vh;
    overflow: hidden;
  }

  .main-content {
    max-width: 1400px;
    margin: 0 auto;
    min-height: 100vh; 
    background-color: #f4f7fe;
  }
</style>