import pyglet
from pyglet.gl import *
from pyglet.window import key
import math as m
import json
# from game import Game
from racegame.config import windowHeight, windowWidth, frame_rate

class GameWindow(pyglet.window.Window):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.state          = "track"           # State of track building
        self.select_line    = None              # To hold object of current line
        self.mouse_x        = windowWidth / 2   # Initiate mouse at middle
        self.mouse_y        = windowHeight / 2  # " "
        self.anchor_x       = None              # Anchor point x
        self.anchor_y       = None              # Anchor point y
        self.anchor_dot     = None              # Anchor dot object
        self.cursor_dot     = None              # Cursor dot object
        self.screenshot     = False             # Make screenshot?
        self.track          = []                # List of track limits
        self.gates          = []                # List of sector gates

        # Background picture (1280x720 image of a track, for example)
        self.background     = pyglet.shapes.Rectangle(0, 0, windowWidth, windowHeight, color=(0, 0, 0))
        self.pic            = pyglet.image.load('./racegame/assets/white_bg.jpg')
        self.track_name     = "obstacle_run"    # Name of track (CHANGE WHEN MAKING NEW TRACK)

    # End process when you attempt to close the window
    def on_close(self):
        self.close()

    # Export track data to file
    def export(self):

        # Track limits and sector gates, dict for each one
        track_data = [{"x": line.x, "y": line.y, "x2": line.x2, "y2": line.y2} for line in self.track]
        gate_data = [{"x": line.x, "y": line.y, "x2": line.x2, "y2": line.y2} for line in self.gates]

        # Name of generated background
        bg_name = self.track_name + "_image.png"

        # Start position - initiate as template (has to be set by user later)
        start_pos = {"x": None, "y": None, "heading": None}

        # Store in one big dict
        track_data = {
            "track_limits": track_data,
            "reward_gates": gate_data,
            "bg_name": bg_name,
            "start_pos": start_pos
        }

        # Dump to json file
        with open(self.track_name + ".json", 'w') as f:
            json.dump(track_data, f, indent=2) 

    # Key press event
    def on_key_press(self, symbol, modifiers):

        # If escape, end process
        if symbol == key.ESCAPE:
            self.close()

        # If enter, switch to next state OR export
        elif symbol == key.ENTER:
            if self.state == "track":
                self.state = "gate"
            elif self.state == "gate":
                self.export()

        # If backspace, sort of 'undo'
        elif symbol == key.BACKSPACE:
            if self.state == "track" and len(self.track) > 1:
                self.track.pop()
                x = self.track[-1].x2
                y = self.track[-1].y2
                self.anchor_x = x
                self.anchor_y = y
                self.select_line.x = x
                self.select_line.y = y
                self.anchor_dot.x = x
                self.anchor_dot.y = y
            elif self.state == "gate" and len(self.gates) > 0:
                self.gates.pop()

        # If RSHIFT, make screenshot of screen for track image
        elif symbol == key.RSHIFT:
            self.screenshot = True

    # Mouse press event
    def on_mouse_press(self, x, y, button, modifiers):

        # If user presses left mouse button
        if button == pyglet.window.mouse.LEFT:

            # If no anchor yet exists, create one here
            if self.anchor_x == None:
                self.anchor_x = self.mouse_x
                self.anchor_y = self.mouse_y
                self.select_line = pyglet.shapes.Line(self.anchor_x, self.anchor_y, self.mouse_x, self.mouse_y, 3, color = (80, 225, 30))
                self.anchor_dot = pyglet.shapes.Circle(self.anchor_x, self.anchor_y, 5, color=(255, 0, 0))
            
            # Else we already have an achor so we can create a new line with it
            else:
                x1 = self.anchor_x
                y1 = self.anchor_y

                # Snap to points nearby
                x2, y2 = self.snap_to_point(x, y)

                # Of course, if we are in the track building state, create a new track limit line
                if self.state == "track":
                    
                    # For visualisation: add to screen as new line
                    new_line = pyglet.shapes.Line(x1, y1, x2, y2, 3, color = (0, 0, 255))
                    self.track.append(new_line)

                    # Update anchor point
                    self.anchor_x = x2
                    self.anchor_y = y2
                    self.anchor_dot.x = self.anchor_x
                    self.anchor_dot.y = self.anchor_y

                    self.select_line.x = self.anchor_x
                    self.select_line.y = self.anchor_y

                # If we are in the sector gate building state
                if self.state == "gate":

                    # Create new sector gate line and draw to screen
                    new_line = pyglet.shapes.Line(x1, y1, x2, y2, 3, color = (0, 255, 0))
                    self.gates.append(new_line)

                    # Update anchor points
                    self.anchor_x = None
                    self.anchor_y = None
                    self.select_line = None
                    self.anchor_dot = None

        # If we press right mouse button, we can add discontinuities
        if button == pyglet.window.mouse.RIGHT:
            
            self.anchor_x = None
            self.anchor_y = None
            self.select_line = None
            self.anchor_dot = None

    # Snap to a previously defined point
    def snap_to_point(self, mx, my):

        # The original position of the mouse
        new_x, new_y = mx, my

        # Loop through all track limit lines
        for line in self.track:

            # If cursor is close to end point of line, snap to that point
            if m.sqrt((line.x2 - mx)**2 + (line.y2 - my)**2) < 10:
                new_x, new_y = line.x2, line.y2

            # If cursor is close to start point of line, snap to that point
            elif m.sqrt((line.x - mx)**2 + (line.y - my)**2) < 10:
                new_x, new_y = line.x, line.y

        # Return coordinates
        return new_x, new_y
        

    # Mouse motion event
    def on_mouse_motion(self, x, y, dx, dy):

        # Update mouse positions
        self.mouse_x = x
        self.mouse_y = y

        # If we do not have a cursor dot draw object yet, create one
        if not self.cursor_dot:
            self.cursor_dot = pyglet.shapes.Circle(x, y, 5, color=(255, 0, 0))

        # If we have a display line, update its coordinates
        if self.select_line:

            x, y = self.snap_to_point(x, y)
            self.select_line.x2 = x
            self.select_line.y2 = y

        # Snap cursor to point though
        x, y = self.snap_to_point(x, y)

        # Update cursor dot coordinates
        self.cursor_dot.x = x
        self.cursor_dot.y = y
        self.mouse_x = x
        self.mouse_y = y

    # Draw event
    def on_draw(self):

        # Start drawing
        glPushMatrix()

        # Draw empty background
        self.background.draw()

        # If we are not making a screenshot, just put the track background behind
        if not self.screenshot:

            self.pic.blit(0, 0)

        # If we are not making a screenshot, show the display line
        if self.select_line and not self.screenshot:
            self.select_line.draw()

        # only draw gates when we are not making a screenshot
        if not self.screenshot:
            for gate in self.gates:
                gate.draw()
        
        # Draw all track limits
        for track in self.track:
            track.draw()

        # Only draw anchor point dot if we are not making a screenshot
        if self.anchor_dot and not self.screenshot:
            self.anchor_dot.draw()

        # Only draw cursor dot if we are not making a screenshot
        if self.cursor_dot and not self.screenshot:
            self.cursor_dot.draw()

        # Stop drawing
        glPopMatrix()

        # Save screenshot under track name
        if self.screenshot:
            pyglet.image.get_buffer_manager().get_color_buffer().save(self.track_name + '_image.png')
            self.screenshot = False

if __name__ == "__main__":
    window = GameWindow(windowWidth, windowHeight, "Track Generator", resizable=False)
    pyglet.app.run()