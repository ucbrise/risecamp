var express = require('express');
var app = express();

var fetch = require('node-fetch');

app.use(require('body-parser').json());

app.use(function(request, response, next) {
  response.set('Access-Control-Allow-Origin', '*');
  next();
});

app.post('/predict', function(request, response) {
  console.log(`Request body: ${JSON.stringify(request.body)}`);
  fetch('http://localhost:1337/pong/predict', {
    method: 'POST',
    mode: 'cors',
    redirect: 'follow',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(request.body)
  }).then(function(clipperResponse) {
    if (clipperResponse.status >= 400) {
      console.log(clipperResponse.body);
    }
    //   console.log(
    //       `${clipperResponse.status}:
    //       ${JSON.stringify(clipperResponse.body)}`);
    // }
    response.set('Content-Type', 'application/json');
    response.status(clipperResponse.status);
    response.send(clipperResponse.body);
    // console.log(response.json())
  });

  // console.log(request.body);
  // response.sendStatus(200);

});


app.use(express.static(__dirname + '/static'));

app.listen(3000);
console.log('Listening on port 3000');
