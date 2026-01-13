<script lang="ts">
    import type { Application } from '$lib/types';
    export let data: Application[] = [];
</script>

<h3>최근 신청내역</h3>
<div class="table-wrapper">
    <table>
        <thead>
            <tr>
                <th>상태</th>
                <th>신청구분</th>
                <th>시작일자</th>
                <th>종료일자</th>
                <th>소요시간</th>
                <th>작성일</th>
            </tr>
        </thead>
        <tbody>
            {#each data as app}
            <tr>
                <td><span class="status-badge" class:approved={app.status === '승인'} class:rejected={app.status === '반려'}>{app.status}</span></td>
                <td>{app.type}</td>
                <td>{app.startDate}</td>
                <td>{app.endDate}</td>
                <td>{app.duration}</td>
                <td>{app.requestDate}</td>
            </tr>
            {/each}
        </tbody>
    </table>
</div>

<style>
    h3 { font-size: 18px; margin-top: 0; margin-bottom: 20px; }
    .table-wrapper { overflow-x: auto; }
    table { width: 100%; border-collapse: collapse; font-size: 14px; }
    th, td { padding: 16px; border-bottom: 1px solid #eee; text-align: center; white-space: nowrap; }
    thead th { color: #888; font-weight: 500; }
    tbody td { color: #333; }
    .status-badge { padding: 4px 10px; border-radius: 12px; font-size: 12px; display: inline-block; font-weight: 500; }
    .status-badge.approved { background-color: #e7f4e8; color: #4caf50; }
    .status-badge.rejected { background-color: #fdecea; color: #f44336; }
</style>