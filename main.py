import pyglet
from pyglet.gl import *
from pyglet.window import key
from game import Game
import json
from racegame.config import windowHeight, windowWidth, frame_rate
import os

class GameWindow(pyglet.window.Window):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fps_display            = pyglet.window.FPSDisplay(self)    # FPS display object

        with open("./racegame/tracks/Obstaclerun/obstacle_run.json", 'r') as f:
            track_data              = json.load(f)                      # Data for track
            self.asset_directory    = os.path.dirname(f.name)           # Directory of track data file

        # Obtain track image as listed in track data file
        self.track_image = pyglet.image.load(self.asset_directory + "/" + track_data['bg_name'])

        # Create a Game instance for this window
        self.game = Game(40, 50, track_data['track_limits'], track_data['reward_gates'], track_data['start_pos']['x'], track_data['start_pos']['y'], track_data['start_pos']['heading'], self)

    # When closing the window, stop the program
    def on_close(self):
        self.close()

    # Custom draw function so we can do the drawing out of the on_draw event loop
    def my_draw(self, game: Game):

        # Necessary Pyglet stuff
        self.switch_to()
        pyglet.clock.tick()
        self.dispatch_events()

        # Start drawing
        glPushMatrix()

        # Clear screen
        self.clear()

        # Place track sprite in lower left corner
        self.track_image.blit(0, 0)

        # Render everything of the game
        game.render()

        # Draw FPS display
        self.fps_display.draw()

        # Stop drawing
        glPopMatrix()

        # Flip screen (from buffer, push pixel data to screen)
        self.flip() 

    # Key press event
    def on_key_press(self, symbol, modifiers):

        # If we press escape, close that thing!
        if symbol == key.ESCAPE:
            self.close()

if __name__ == "__main__":
    window = GameWindow(windowWidth, windowHeight, "Driving a race-car around a track with NEAT!", resizable=False)
    pyglet.app.run()