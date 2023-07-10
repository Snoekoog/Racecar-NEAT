import pyglet
from pyglet.gl import *
from pyglet.window import key
from game import Game
import json
from racegame.config import windowHeight, windowWidth, frame_rate
import time
import os

class GameWindow(pyglet.window.Window):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fps_display = pyglet.window.FPSDisplay(self)
        backgroundColor = [0, 0, 0, 255]
        backgroundColor = [i / 255 for i in backgroundColor]
        glClearColor(*backgroundColor)
        track_data = None
        self.mouse_x = int(windowWidth / 2)
        self.mouse_y = int(windowHeight / 2)
        self.asset_directory = None
        with open("./racegame/tracks/Silverstone/silverstone.json", 'r') as f:
            track_data = json.load(f)
            self.asset_directory = os.path.dirname(f.name)
        self.track_image = pyglet.image.load(self.asset_directory + "/" + track_data['bg_name'])
        self.game = Game(40, 20, track_data['track_limits'], track_data['reward_gates'], track_data['start_pos']['x'], track_data['start_pos']['y'], track_data['start_pos']['heading'], self)

    def on_close(self):
        self.close()

    def my_draw(self, game):
        self.switch_to()
        pyglet.clock.tick()
        self.dispatch_events()
        glPushMatrix()
        self.clear()
        self.track_image.blit(0, 0)
        game.render()
        self.fps_display.draw()
        glPopMatrix()
        self.flip() 

    def on_key_press(self, symbol, modifiers):
        # if symbol == key.RIGHT:
        #     self.game.car.is_steering_right = True
        # if symbol == key.LEFT:
        #     self.game.car.is_steering_left = True
        # if symbol == key.UP:
        #     self.game.car.is_accelerating = True
        # if symbol == key.DOWN:
        #     self.game.car.is_reversing = True
        if symbol == key.ESCAPE:
            self.close()

    # def on_key_release(self, symbol, modifiers):
    #     if symbol == key.RIGHT:
    #         self.game.car.is_steering_right = False
    #     if symbol == key.LEFT:
    #         self.game.car.is_steering_left = False
    #     if symbol == key.UP:
    #         self.game.car.is_accelerating = False
    #     if symbol == key.DOWN:
    #         self.game.car.is_reversing = False

    # def on_mouse_motion(self, x, y, dx, dy):
    #     self.mouse_x = x
    #     self.mouse_y = y

if __name__ == "__main__":
    window = GameWindow(windowWidth, windowHeight, "Racecar game", resizable=False)
    pyglet.app.run()