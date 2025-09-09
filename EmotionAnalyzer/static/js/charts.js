document.addEventListener('DOMContentLoaded', function() {
    // Check if the chart elements exist on the page
    const emotionChartElement = document.getElementById('emotionChart');
    const emotionBarChartElement = document.getElementById('emotionBarChart');
    
    if (emotionChartElement && emotions && counts) {
        // Emotion distribution pie chart
        const emotionChart = new Chart(emotionChartElement, {
            type: 'pie',
            data: {
                labels: JSON.parse(emotions),
                datasets: [{
                    data: JSON.parse(counts),
                    backgroundColor: [
                        '#dc3545', // angry - red
                        '#20c997', // disgust - teal
                        '#6f42c1', // fear - purple
                        '#ffc107', // happy - yellow
                        '#0dcaf0', // sad - cyan
                        '#fd7e14', // surprise - orange
                        '#6c757d'  // neutral - gray
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right',
                    },
                    title: {
                        display: true,
                        text: 'Emotion Distribution',
                        font: {
                            size: 16
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.raw || 0;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = Math.round((value / total) * 100);
                                return `${label}: ${value} (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });
    }
    
    if (emotionBarChartElement && emotions && counts) {
        // Emotion distribution bar chart
        const emotionBarChart = new Chart(emotionBarChartElement, {
            type: 'bar',
            data: {
                labels: JSON.parse(emotions),
                datasets: [{
                    label: 'Number of Detections',
                    data: JSON.parse(counts),
                    backgroundColor: [
                        '#dc3545', // angry - red
                        '#20c997', // disgust - teal
                        '#6f42c1', // fear - purple
                        '#ffc107', // happy - yellow
                        '#0dcaf0', // sad - cyan
                        '#fd7e14', // surprise - orange
                        '#6c757d'  // neutral - gray
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                indexAxis: 'y',
                plugins: {
                    legend: {
                        display: false
                    },
                    title: {
                        display: true,
                        text: 'Emotion Frequency',
                        font: {
                            size: 16
                        }
                    }
                },
                scales: {
                    x: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Number of Detections'
                        }
                    }
                }
            }
        });
    }
    
    // Fetch updated statistics every 30 seconds if on dashboard
    if (window.location.pathname.includes('dashboard')) {
        setInterval(updateCharts, 30000);
    }
    
    function updateCharts() {
        fetch('/api/emotion-stats')
            .then(response => response.json())
            .then(data => {
                // Update charts if they exist
                if (typeof emotionChart !== 'undefined') {
                    const keys = Object.keys(data);
                    const values = Object.values(data);
                    
                    emotionChart.data.labels = keys;
                    emotionChart.data.datasets[0].data = values;
                    emotionChart.update();
                }
                
                if (typeof emotionBarChart !== 'undefined') {
                    const keys = Object.keys(data);
                    const values = Object.values(data);
                    
                    emotionBarChart.data.labels = keys;
                    emotionBarChart.data.datasets[0].data = values;
                    emotionBarChart.update();
                }
            })
            .catch(error => console.error('Error updating charts:', error));
    }
});
