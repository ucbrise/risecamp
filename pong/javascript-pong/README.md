# Pong

Play Pong against an RL Policy served from Clipper

## Instructions

#### Start Clipper for Testing

If you just want to test the Pong part, you can start Clipper and deploy a random policy with a simple Python script.

>Note that you must have `clipper_admin` installed

```sh
# If you need to install clipper_admin:
pip install git+https://github.com/ucbrise/clipper.git@develop#subdirectory=clipper_admin

# Start Clipper
python clipper_mock_pong_server.py
```

This script is just for testing purposes. The exercise in the [`/rl_exercise06.ipynb`](../rl_exercises06.ipynb) will walk you through the process of starting Clipper and deploying a real policy.

You can verify that Clipper is running with `docker ps`, you should see the four containers that Clipper launched. One container from each of the following images:

+ `clipper/query_frontend`
+ `clipper/management_frontend`
+ `redis:alpine`
+ `clipper/python-closure-container`

#### Start the Pong Server

The Pong game is an in-browser Javascript game, but we need to serve the site from a little HTTP server rather than opening the static files locally due to some CORS issues (the requests for the HTML/JS/CSS files need to go to the same resource as the requests for predictions from Clipper). This http server will both serve the site and act as a proxy for prediction requests to Clipper.

Start the server:

```sh
python pong-server.py
```

#### Play against the AI:

Go to <http://localhost:3000/index.html>. You should see the Pong game. Press "1" to play against the AI. Press "Escape" to stop the game.




*Pong game is lightly adapted from <https://github.com/jakesgordon/javascript-pong>*
