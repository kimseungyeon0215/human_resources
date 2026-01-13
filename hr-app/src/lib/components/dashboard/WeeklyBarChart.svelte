<script lang="ts">
    type WeeklyData = {
    day: string;
    work: number;
    color: string;
  };

    export let weeklyData: WeeklyData[] = [];

</script>

<div class="card chart-card">
    <div class="card-header">
        <h3>총 근무시간</h3>
        <span>2025.09.08 - 2025.09.14</span>
    </div>
    <div class="bar-chart">
        {#each weeklyData as day}
        <div class="bar-wrapper">
            <div class="bar-bg">
                <div class="bar-value" style="height: {day.work * 8}%; background-color: {day.color};"></div>
            </div>
            <span class="day-label">{day.day}</span>
            <span class="hour-label">{day.work > 0 ? `${day.work}시간` : '-'}</span>
        </div>
        {/each}
    </div>
    <div class="legend">
        <span class="legend-item"><span class="color-box" style="background-color: #5a82f0;"></span>근무시간</span>
        <span class="legend-item"><span class="color-box" style="background-color: #8563d3;"></span>연장근무</span>
        <span class="legend-item"><span class="color-box" style="background-color: #f06292;"></span>휴가</span>
    </div>
</div>

<style>
    /* ... (원본 코드의 .card, .chart-card, .bar-chart 등 관련 스타일만 복사) ... */
    .card { background-color: #fff; /* ... */ }
    .card-header { display:flex; /* ... */ }
    .bar-chart { display: flex; /* ... */ }
    /* ... 이하 생략 ... */
</style>