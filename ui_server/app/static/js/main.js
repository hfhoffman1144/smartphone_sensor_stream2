$(document).ready(function() {

    // Global variable to store actice devices
    var currentDevices = [];
    var currentChartConfigs = {};
    var currentCharts = {};

    function createDeviceCharts(event) {

        // Parse event data
        const data = JSON.parse(event.data);
        console.log(data);

        // Unpack elements in the message
        id = data[0];
        time = data[1];
        x = data[2];
        y = data[3];
        z = data[4];

        // Update charts if they exist
        if (currentDevices.includes(id)) {

            currentChartConfigs[id].data.labels.push(time);
            currentChartConfigs[id].data.datasets[0].data.push(x);
            currentChartConfigs[id].data.datasets[1].data.push(y);
            currentChartConfigs[id].data.datasets[2].data.push(z);

            // Remove the first elemnt of the array if they array is longer than 100
            if (currentChartConfigs[id].data.labels.length > 100) {

                currentChartConfigs[id].data.labels.shift();
                currentChartConfigs[id].data.datasets[0].data.shift();
                currentChartConfigs[id].data.datasets[1].data.shift();
                currentChartConfigs[id].data.datasets[2].data.shift();

            }

            currentCharts[id].update();

            return

        }

        let canvas = document.createElement('canvas');
        canvas.setAttribute('id', id);
        canvas.setAttribute('width', '100');
        canvas.setAttribute('height', '50');
        let canvasContainer = document.createElement('div');
        canvasContainer.appendChild(canvas);
        document.getElementById("main-container").appendChild(canvasContainer);

        currentDevices.push(id);

        var ctx = document.getElementById(id).getContext("2d");

        currentChartConfigs[id] = {
            type: 'line',
            data: {
                labels: [time],
                datasets: [{
                    label: "X",
                    backgroundColor: 'blue',
                    borderColor: 'blue',
                    data: [x],
                    fill: false,
                }, {
                    label: "Y",
                    backgroundColor: 'orange',
                    borderColor: 'orange',
                    data: [y],
                    fill: false,
                }, {
                    label: "Z",
                    backgroundColor: 'green',
                    borderColor: 'green',
                    data: [z],
                    fill: false,
                }],
            },
            options: {
                responsive: true,
                title: {
                    display: true,
                    text: 'Accelerometer signal for ' + id
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
                    xAxes: [{
                        display: true,
                        scaleLabel: {
                            display: true,
                            labelString: 'Time'
                        }
                    }],
                    yAxes: [{
                        display: true,
                        scaleLabel: {
                            display: true,
                            labelString: 'Value'
                        }
                    }]
                }
            }
        };

        currentCharts[id] = new Chart(ctx, currentChartConfigs[id]);

    }

    const source = new EventSource("http://127.0.0.1:5000/chart-data");

    source.addEventListener("new_message", function(event) {

        createDeviceCharts(event);

    });

});