feather.replace({ 'aria-hidden': 'true' })
// Parse the data embedded in the HTML template
var daily_sales_data = JSON.parse('{{ daily_sales_data | tojson | safe }}');
var daily_expenses_data = JSON.parse('{{ daily_expenses_data | tojson | safe }}');

// Create the chart using Chart.js
var ctx1 = document.getElementById('myChart1').getContext('2d');
var myChart1 = new Chart(ctx1, {
    type: 'bar',
    data: {
        labels: daily_sales_data.labels,
        datasets: [{
            label: 'Sales',
            data: daily_sales_data.values,
            backgroundColor: 'rgba(54, 162, 235, 0.2)',
            borderColor: 'rgba(54, 162, 235, 1)',
            borderWidth: 1
        }]
    },
    options: {
        scales: {
            yAxes: [{
                ticks: {
                    beginAtZero: true
                }
            }]
        }
    }
});

var ctx2 = document.getElementById('myChart2').getContext('2d');
var myChart2 = new Chart(ctx2, {
    type: 'bar',
    data: {
        labels: daily_expenses_data.labels,
        datasets: [{
            label: 'Expenses',
            data: daily_expenses_data.values,
            backgroundColor: 'rgba(54, 162, 235, 0.2)',
            borderColor: 'rgba(54, 162, 235, 1)',
            borderWidth: 1
        }]
    },
    options: {
        scales: {
            yAxes: [{
                ticks: {
                    beginAtZero: true
                }
            }]
        }
    }
});
