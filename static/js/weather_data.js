

  $(document).ready(function () {
    if (labels != null && data != null) {
        console.log("Received sensorData :: " + labels + " :: " + data);

        const myChartTemperature = document.getElementById('myChartTemperature');
        new Chart(myChartTemperature, {
            type: 'line',
            data: {
            labels: labels,
            datasets: [{
                label: 'Temperature (°C)',
                data: data.TEMPERATURE,
                borderWidth: 1
            }]
            },
            options: {
                borderWidth: 3,
                borderColor: ['rgba(255, 99, 132, 1)',],
            }
        });

        const myChartPressure = document.getElementById('myChartPressure');
        new Chart(myChartPressure, {
            type: 'line',
            data: {
            labels: labels,
            datasets: [{
                label: 'Pressure (Pa)',
                data: data.PRESSURE,
                borderWidth: 1
            }]
            },
            options: {
                borderWidth: 3,
                borderColor: ['rgba(69, 131, 50, 1)',],
            }
        });


        const myChartHumidity = document.getElementById('myChartHumidity');
        new Chart(myChartHumidity, {
            type: 'line',
            data: {
            labels: labels,
            datasets: [{
                label: 'Humidity (%)',
                data: data.HUMIDITY,
                borderWidth: 1
            }]
            },
            options: {
                borderWidth: 3,
                borderColor: ['rgba(102, 99, 255, 1)',],
            }
        });

        const myChartWindSpeed = document.getElementById('myChartWindSpeed');
        new Chart(myChartWindSpeed, {
            type: 'line',
            data: {
            labels: labels,
            datasets: [{
                label: 'Wind speed (km/h)',
                data: data.WIND_SPEED,
                borderWidth: 1
            }]
            },
            options: {
                borderWidth: 3,
                borderColor: ['rgba(255, 238, 0, 1)',],
            }
        });

        const myChartInternalTemperature = document.getElementById('myChartInternalTemperature');
        new Chart(myChartInternalTemperature, {
            type: 'line',
            data: {
            labels: labels,
            datasets: [{
                label: 'Internal temperature (°C)',
                data: data.TEMPERATURE_INTERNAL,
                borderWidth: 1
            }]
            },
            options: {
                borderWidth: 3,
                borderColor: ['rgba(255, 99, 132, 1)',],
            }
        });
    }
});

