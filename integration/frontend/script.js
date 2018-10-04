var myCanvas = document.getElementById("graph");
myCanvas.width = 500;
myCanvas.height = 500;

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
            maxValue = Math.max(maxValue, this.options.data[categ]);
        }
        
        var minValue = 0;
        for (var categ in this.options.data){
            minValue = Math.min(minValue, this.options.data[categ]);
        }

        var canvasActualHeight = this.canvas.height - this.options.padding * 2;
        var canvasActualWidth = this.canvas.width - this.options.padding * 2;
 
        // drawing the grid lines
        var gridValue = minValue;
        var gridIncrement = canvasActualHeight / (Math.abs(minValue) + Math.abs(maxValue));
       
        var offset = 30;
        var gridY = canvasActualHeight + offset;
        
        var zHeight = (Math.abs(maxValue) / (Math.abs(minValue) + Math.abs(maxValue))) * canvasActualHeight + offset;

        while (gridValue <= maxValue){
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
            this.ctx.font = "bold 10px Helvetica";
            this.ctx.fillText(gridValue, 10, gridY - 2);
            this.ctx.restore();
 
            gridValue+=this.options.gridScale;
            gridY -= this.options.gridScale * gridIncrement;
        }     
  
        //drawing the bars
        var barIndex = 0;
        var numberOfBars = Object.keys(this.options.data).length;
        var barSize = (canvasActualWidth)/numberOfBars;

        var posHeight = canvasActualHeight - zHeight;
 
        for (categ in this.options.data){
            var val = this.options.data[categ];
            console.log(categ);
            
            if (val > 0) {
              console.log(val/maxValue * (canvasActualHeight - zHeight) );
              var topLeft = posHeight - Math.round(val/maxValue * (canvasActualHeight - zHeight)) + offset;
              var barHeight = zHeight - topLeft;
            } else if (val < 0) {
              var topLeft = zHeight;
              var barHeight = Math.round(val/minValue * zHeight) - offset;
            } else {
              var topLeft = zHeight;
              var barHeight = 0;
            }
          
            console.log(val);
            console.log(barHeight);
            console.log(topLeft);
              
            drawBar(
              this.ctx,
              this.options.padding + barIndex * barSize,
              topLeft,
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
        this.ctx.font = "bold 14px Helvetica";
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
      padding:50,
      gridScale:5,
      gridColor:"black",
      data:globalData,
      colors:["#a55ca5","#67b6c7", "#bccd7a","#eb9743"]
    }
  );

  ctx.clearRect(0, 0, myCanvas.width, myCanvas.height);
  myBarchart.draw()
}

updateGraph(true);

var id = setInterval(function() { updateGraph(false); }, 1000);
