// SOURCE: https://canvasjs.com/html5-javascript-bar-chart/

var globalData = {
    "Imitation (Small)": 0,
    "Imitation (Large)": 0,
    "RL": 0
};

var chart = null;

const sleep = (milliseconds) => {
  return new Promise(resolve => setTimeout(resolve, milliseconds))
}

function drawGraph(dataPoints, animation) {
  if (chart != null) {
    chart.destroy();
  }

  chart = new CanvasJS.Chart("chartContainer", {
    animationEnabled: animation,

    title:{
      text:"Pong AI Scoreboard"
    },
    axisX:{
      interval: 1
    },
    axisY2:{
      interlacedColor: "rgba(1,77,101,.2)",
      gridColor: "rgba(1,77,101,.1)",
      title: "Point Differential"
    },
    data: [{
      type: "bar",
      name: "companies",
      axisYType: "secondary",
      color: "#014D65",
      dataPoints: dataPoints
    }]
  });

  chart.render();
}

function updateGraph(animation) {
  var results = fetch('http://localhost:2000/results', {method: 'GET'}).then(function(data)
    {
      data.json().then(function(info)
        {
          for(var key in info) {
            if(key === "small") {
              globalData["Imitation (Small)"] = info[key];
            }
            if(key === "large") {
              globalData["Imitation (Large)"] = info[key];
            }
            if(key === "rl") {
              globalData["RL"] = info[key];
            }
          }
        });
    });
  

  var dataPoints = [];
  for (var key in globalData) {
    dataPoints.push({y: globalData[key], label: key})
  }

  drawGraph(dataPoints, animation);
}

window.onload = updateGraph(true);

var id = setInterval(function() { updateGraph(false); }, 1000);

