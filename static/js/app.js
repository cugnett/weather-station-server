$(document).ready(function () {
  const ctxTemperature = document.getElementById("myChartTemperature").getContext("2d");
  const ctxPressure = document.getElementById("myChartPressure").getContext("2d");
  const ctxHumidity = document.getElementById("myChartHumidity").getContext("2d");
  const ctxWindSpeed = document.getElementById("myChartWindSpeed").getContext("2d");
  const ctxInternalTemperature = document.getElementById("myChartInternalTemperature").getContext("2d");

  const myChartTemperature = new Chart(ctxTemperature, {
    type: "line",
    data: {
      datasets: [{ label: "Temperature",  }],
    },
    options: {
      borderWidth: 3,
      borderColor: ['rgba(255, 99, 132, 1)',],
    },
  });

  const myChartPressure = new Chart(ctxPressure, {
    type: "line",
    data: {
      datasets: [{ label: "Pressure",  }],
    },
    options: {
      borderWidth: 3,
      borderColor: ['rgba(69, 131, 50, 1)',],
    },
  });

  const myChartHumidity = new Chart(ctxHumidity, {
    type: "line",
    data: {
      datasets: [{ label: "Humidity",  }],
    },
    options: {
      borderWidth: 3,
      borderColor: ['rgba(102, 99, 255, 1)',],
    },
  });

  const myChartWindSpeed = new Chart(ctxWindSpeed, {
    type: "line",
    data: {
      datasets: [{ label: "Wind Speed",  }],
    },
    options: {
      borderWidth: 3,
      borderColor: ['rgba(255, 238, 0, 1)',],
    },
  });

  const myChartInternalTemperature = new Chart(ctxInternalTemperature, {
    type: "line",
    data: {
      datasets: [{ label: "Internal Temperature",  }],
    },
    options: {
      borderWidth: 3,
      borderColor: ['rgba(255, 99, 132, 1)',],
    },
  });

  function addData(label, data, myChart) {
    myChart.data.labels.push(label);
    myChart.data.datasets.forEach((dataset) => {
      dataset.data.push(data);
    });
    myChart.update();
  }

  function removeFirstData(myChart) {
    myChart.data.labels.splice(0, 1);
    myChart.data.datasets.forEach((dataset) => {
      dataset.data.shift();
    });
  }

  const MAX_DATA_COUNT = 100;
  //connect to the socket server.
  //   var socket = io.connect("http://" + document.domain + ":" + location.port);
  var socket = io.connect();

  //receive details from server
  socket.on("updateSensorData", function (msg) {
    console.log("Received sensorData :: " + msg.date + " :: " + msg.value + " :: " + msg.label);

    if (msg.label == "TEMPERATURE") {
      myChart = myChartTemperature
    } else if (msg.label == "PRESSURE") {
      myChart = myChartPressure
    } else if (msg.label == "HUMIDITY"){
      myChart = myChartHumidity
    } else if (msg.label == "WIND_SPEED"){
      myChart = myChartWindSpeed
    } else if (msg.label == "TEMPERATURE_INTERNAL"){
      myChart = myChartInternalTemperature
    } else {
      return 0
    }

      // Show only MAX_DATA_COUNT data
    if (myChart.data.labels.length > MAX_DATA_COUNT) {
      removeFirstData(myChart);
    }
    addData(msg.date, msg.value, myChart);
    
  });
});
