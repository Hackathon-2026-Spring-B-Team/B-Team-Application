// サンプルデータ（実際にはAPIから取得）
const progressData = {
    subjects: ['基礎理論', 'ネットワーク', 'ストレージ', 'セキュリティ'],
    data: [
        { notStarted: 10, unclear: 15, partial: 25, understood: 50 },
        { notStarted: 5, unclear: 20, partial: 20, understood: 55 },
        { notStarted: 15, unclear: 10, partial: 25, understood: 50 },
        { notStarted: 8, unclear: 18, partial: 22, understood: 52 }
    ]
};

let chart = null;

// Chart.jsの初期化
function initializeChart() {
    const ctx = document.getElementById('progressChart');
    
    // データセットの準備
    const datasets = [
        {
            label: '未実施',
            data: progressData.data.map(d => d.notStarted),
            backgroundColor: '#d1d5db',
            borderColor: '#9ca3af',
            borderWidth: 1
        },
        {
            label: 'わからない',
            data: progressData.data.map(d => d.unclear),
            backgroundColor: '#f87171',
            borderColor: '#dc2626',
            borderWidth: 1
        },
        {
            label: 'なんとなく',
            data: progressData.data.map(d => d.partial),
            backgroundColor: '#86efac',
            borderColor: '#22c55e',
            borderWidth: 1
        },
        {
            label: '理解した',
            data: progressData.data.map(d => d.understood),
            backgroundColor: '#15803d',
            borderColor: '#166534',
            borderWidth: 1
        }
    ];

    if (chart) {
        chart.destroy();
    }

    chart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: progressData.subjects,
            datasets: datasets
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        font: {
                            family: "'BIZ UDPGothic', sans-serif",
                            size: 14
                        },
                        padding: 15,
                        usePointStyle: true
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.dataset.label + ': ' + context.parsed.x + '%';
                        }
                    },
                    font: {
                        family: "'BIZ UDPGothic', sans-serif",
                        size: 12
                    }
                }
            },
            scales: {
                x: {
                    stacked: true,
                    max: 100,
                    ticks: {
                        callback: function(value) {
                            return value + '%';
                        },
                        font: {
                            family: "'BIZ UDPGothic', sans-serif",
                            size: 12
                        }
                    },
                    grid: {
                        color: '#f3f4f6'
                    }
                },
                y: {
                    stacked: true,
                    ticks: {
                        font: {
                            family: "'BIZ UDPGothic', sans-serif",
                            size: 14,
                            weight: 'bold'
                        }
                    }
                }
            }
        }
    });
}

// イベントリスナーの設定
document.addEventListener('DOMContentLoaded', function() {
    initializeChart();

    // ロードマップボタン
    document.getElementById('roadmapBtn').addEventListener('click', function() {
        alert('ロードマップ機能は準備中です');
    });

    // 進捗グラフボタン（既に選択状態）
    document.getElementById('progressBtn').addEventListener('click', function() {
        console.log('進捗グラフを表示中');
    });

    // ウィンドウサイズ変更時のリサイズ処理
    window.addEventListener('resize', function() {
        if (chart) {
            chart.resize();
        }
    });
});

// APIからデータを取得する関数（将来使用）
async function fetchProgressData() {
    try {
        const response = await fetch('/api/progress/');
        const data = await response.json();
        progressData.subjects = data.subjects;
        progressData.data = data.data;
        initializeChart();
    } catch (error) {
        console.error('データ取得エラー:', error);
    }
}
