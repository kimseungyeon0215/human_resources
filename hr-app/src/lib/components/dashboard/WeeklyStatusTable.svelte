<script lang="ts">
    import type { WeeklyStatus } from '$lib/types';
    export let data: WeeklyStatus[] = [];
</script>

<h3>주간현황</h3>
<div class="table-wrapper">
    <table>
        <thead>
            <tr>
                <th>일자(요일)</th>
                {#each data as item}
                    <th>{item.date}</th>
                {/each}
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><strong>근무시간</strong></td>
                {#each data as item}
                    <td>{item.workTime}</td>
                {/each}
            </tr>
            <tr>
                <td><strong>연장근무시간</strong></td>
                {#each data as item}
                    <td>{item.overtime}</td>
                {/each}
            </tr>
            <tr>
                <td><strong>총 근무시간</strong></td>
                {#each data as item}
                    <td>{item.totalTime}</td>
                {/each}
            </tr>
            <tr>
                <td><strong>상태</strong></td>
                {#each data as item}
                    <td>{item.status}</td>
                {/each}
            </tr>
        </tbody>
    </table>
</div>

<style>
    h3 { font-size: 18px; margin-top: 0; margin-bottom: 20px; }
    .table-wrapper { overflow-x: auto; }
    table { width: 100%; border-collapse: collapse; font-size: 14px; }
    th, td { padding: 16px; border-bottom: 1px solid #eee; text-align: center; white-space: nowrap; }
    thead th { color: #888; font-weight: 500; }
    tbody td:first-child { text-align: left; font-weight: bold; color: #555; }
</style>