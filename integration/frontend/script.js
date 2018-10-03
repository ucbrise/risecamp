var myCanvas = document.getElementById("graph");
myCanvas.width = 300;
myCanvas.height = 300;
   
var ctx = myCanvas.getContext("2d");
 
function drawLine(ctx, startX, startY, endX, endY,color){
    ctx.save();
    ctx.strokeStyle = color;
    ctx.beginPath();
    ctx.moveTo(startX,startY);
    ctx.lineTo(endX,endY);
    ctx.stroke();
    ctx.restore();
}
 
function drawBar(ctx, upperLeftCornerX, upperLeftCornerY, width, height,color){
    ctx.save();
    ctx.fillStyle=color;
    ctx.fillRect(upperLeftCornerX,upperLeftCornerY,width,height);
    ctx.restore();
}
 
var globalData = {
    "Imitation (Small)": 0,
    "Imitation (Large)": 0,
    "RL": 0
};
 
var Barchart = function(options){
    this.options = options;
    this.canvas = options.canvas;
    this.ctx = this.canvas.getContext("2d");
    this.colors = options.colors;
    this.drawLegend = options.drawLegend;
  
    this.draw = function(){
        var maxValue = 0;
        for (var categ in this.options.data){
            maxValue = Math.max(maxValue,this.options.data[categ]);
        }
        var canvasActualHeight = this.canvas.height - this.options.padding * 2;
        var canvasActualWidth = this.canvas.width - this.options.padding * 2;
 
        //drawing the grid lines
        var gridValue = 0;
        while (gridValue <= maxValue){
            var gridY = canvasActualHeight * (1 - gridValue/maxValue) + this.options.padding;
            drawLine(
                this.ctx,
                0,
                gridY,
                this.canvas.width,
                gridY,
                this.options.gridColor
            );
             
            //writing grid markers
            this.ctx.save();
            this.ctx.fillStyle = this.options.gridColor;
            this.ctx.textBaseline="bottom"; 
            this.ctx.font = "bold 10px Arial";
            this.ctx.fillText(gridValue, 10,gridY - 2);
            this.ctx.restore();
 
            gridValue+=this.options.gridScale;
        }     
  
        //drawing the bars
        var barIndex = 0;
        var numberOfBars = Object.keys(this.options.data).length;
        var barSize = (canvasActualWidth)/numberOfBars;
 
        for (categ in this.options.data){
            var val = this.options.data[categ];
            var barHeight = Math.round( canvasActualHeight * val/maxValue) ;
            drawBar(
                this.ctx,
                this.options.padding + barIndex * barSize,
                this.canvas.height - barHeight - this.options.padding,
                barSize,
                barHeight,
                this.colors[barIndex%this.colors.length]
            );
 
            barIndex++;
        }
 
        //drawing series name
        this.ctx.save();
        this.ctx.textBaseline="bottom";
        this.ctx.textAlign="center";
        this.ctx.fillStyle = "#000000";
        this.ctx.font = "bold 14px Arial";
        this.ctx.fillText(this.options.seriesName, this.canvas.width/2,this.canvas.height);
        this.ctx.restore();  
         
        //draw legend
        if (this.drawLegend) {
          barIndex = 0;
          var legend = document.querySelector("legend[for='myCanvas']");
          var ul = document.createElement("ul");
          legend.append(ul);
          for (categ in this.options.data){
            var li = document.createElement("li");
            li.style.listStyle = "none";
            li.style.borderLeft = "20px solid "+this.colors[barIndex%this.colors.length];
            li.style.padding = "5px";
            li.textContent = categ;
            ul.append(li);
            barIndex++;
          }
        }
    }
}
 
 
function updateGraph(drawLegend) {
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
  
  var myBarchart = new Barchart(
    {
      canvas:myCanvas,
      drawLegend: drawLegend,
      seriesName:"Vinyl records",
      padding:20,
      gridScale:5,
      gridColor:"#eeeeee",
      data:globalData,
      colors:["#a55ca5","#67b6c7", "#bccd7a","#eb9743"]
    }
  );

  ctx.clearRect(0, 0, myCanvas.width, myCanvas.height);
  myBarchart.draw()
}

updateGraph(true);

var id = setInterval(function() { updateGraph(false); }, 1000);
