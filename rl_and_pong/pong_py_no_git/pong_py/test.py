from pongjs import PongJS
import matplotlib as mpl
import time
# mpl.use("MacOSX")

import matplotlib.pyplot as plt

game = PongJS()
terminated = False
state = game.init()
animation = True

x = []
y = []

if animation:
    plt.ion()
    plt.figure()
    plt.show()
    plt.pause(0.05)
step = 0

while not terminated:
    step += 1
    ns, r, terminated = game.step(0)

    #game.step(ACTION)

    ###### CHEAT #######
    game.left_pad.set_position(game.left_pad.x, ns[1])
    ####################

    if animation:
        x.append(ns[0])
        y.append(ns[1])
        print(ns[0], ns[1])

        plt.plot([game.right_pad.x, game.left_pad.x],
                [game.right_pad.y, game.left_pad.y], 'o')
        if step % 5 == 0:
            for line in plt.axes().lines:
                line.remove()
            plt.plot(x, y, c='black')
            plt.draw()
            plt.pause(0.01)

print("XXX", step)
