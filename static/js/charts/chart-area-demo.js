'use strict';
// Set new default font family and font color to mimic Bootstrap's default styling
Chart.defaults.global.defaultFontFamily = 'Nunito', '-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
Chart.defaults.global.defaultFontColor = '#858796';

const chartColors = {
    red: 'rgb(255, 99, 132)',
    orange: 'rgb(255, 159, 64)',
    yellow: 'rgb(255, 205, 86)',
    green: 'rgb(0,192,38)',
    cyan: 'rgb(75, 192, 192)',
    blue: 'rgb(54, 162, 235)',
    purple: 'rgb(153, 102, 255)',
    grey: 'rgb(201, 203, 207)'
};


const MONTHS = [
    'Январь',
    'Февраль',
    'Март',
    'Апрель',
    'Май',
    'Июнь',
    'Июль',
    'Август',
    'Сентрябрь',
    'Октябрь',
    'Ноябрь',
    'Декабрь'
];

const COLORS = [
    '#4dc9f6',
    '#f67019',
    '#f53794',
    '#537bc4',
    '#acc236',
    '#166a8f',
    '#00a950',
    '#58595b',
    '#8549ba'
];

function getDateRange(day) {
    let datenow = new Date();
    let currentMonth = datenow.getMonth();
    let dates = [];
    let startDate = 0;
    if (day >= 14)
        startDate = day - 14;
    for (let j = startDate; j < day; ++j) {
        console.log(j);
        dates.push((j + 1).toString() + ' ' + MONTHS[currentMonth])
    }
    return dates;
}


function clearCanvas() {
    var canvas = document.getElementById("statsChart");
    var ctx = canvas.getContext("2d");
    ctx.clearRect(0, 0, canvas.width, canvas.height);

}

function drawChart(chart_id, nfollowers, nfollowing, nlikes, days) {
    const config = {
        type: 'line',
        data: {
            labels: getDateRange(days),
            datasets: [
                {
                    label: 'Количество подписчиков',
                    backgroundColor: chartColors.blue,
                    borderColor: chartColors.blue,
                    data: nfollowers,
                    lineTension: 0,
                    fill: false,
                }, {
                    label: 'Количество подписок',
                    backgroundColor: chartColors.green,
                    borderColor: chartColors.green,
                    data: nfollowing,
                    lineTension: 0,
                    fill: false,
                }, {
                    label: 'Количество лайков',
                    backgroundColor: chartColors.red,
                    borderColor: chartColors.red,
                    data: nlikes,
                    lineTension: 0,
                    fill: false,
                }]
        },
        options: {
            responsive: true,
            bezierCurve: false,
            borderJoinStyle: 'mitter',
            title: {
                display: true,
                text: 'Статистика'
            },
            tooltips: {
                mode: 'index',
                intersect: false,
            },
            hover: {
                mode: 'nearest',
                intersect: true
            },
            scales: {
                x: {
                    display: true,
                    scaleLabel: {
                        display: true,
                        labelString: 'Month'
                    }
                },
                y: {
                    display: true,
                    scaleLabel: {
                        display: true,
                        labelString: 'Value'
                    }
                }
            },
        plugins: {
            zoom: {
                // Container for pan options
                pan: {
                    // Boolean to enable panning
                    enabled: true,

                    // Panning directions. Remove the appropriate direction to disable
                    // Eg. 'y' would only allow panning in the y direction
                    mode: 'xy'
                },

                // Container for zoom options
                zoom: {
                    // Boolean to enable zooming
                    enabled: true,

                    // Zooming directions. Remove the appropriate direction to disable
                    // Eg. 'y' would only allow zooming in the y direction
                    mode: 'xy',
                }
            }
        }
        }
    };

    const ctx = document.getElementById(chart_id).getContext('2d');

    let myLine = new Chart(ctx, config);
}

// let ctx = document.getElementById("statsChart").getContext('2d');