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
        backgroundColor = [0, 0, 0, 255]
        backgroundColor = [i / 255 for i in backgroundColor]
        self.state = "track"
        glClearColor(*backgroundColor)
        self.background = pyglet.shapes.Rectangle(0, 0, windowWidth, windowHeight, color=(0, 0, 0))
        self.pic = pyglet.image.load('./racegame/tracks/Spa/spa-resized.png')
        self.track_name = "spa"
        self.select_line = None
        self.mouse_x = windowWidth / 2
        self.mouse_y = windowHeight / 2
        self.anchor_x = None
        self.anchor_y = None
        self.anchor_dot = None
        self.cursor_dot = None
        self.screenshot = False
        self.track = []
        self.gates = []

    def on_close(self):
        self.close()


    def export(self):
        track_data = [{"x": line.x, "y": line.y, "x2": line.x2, "y2": line.y2} for line in self.track]
        gate_data = [{"x": line.x, "y": line.y, "x2": line.x2, "y2": line.y2} for line in self.gates]
        bg_name = self.track_name + "_image.png"
        start_pos = {"x": None, "y": None, "heading": None}
        track_data = {
            "track_limits": track_data,
            "reward_gates": gate_data,
            "bg_name": bg_name,
            "start_pos": start_pos
        }
        with open(self.track_name + ".json", 'w') as f:
            json.dump(track_data, f, indent=2) 

    def on_key_press(self, symbol, modifiers):
        if symbol == key.ESCAPE:
            self.close()
        elif symbol == key.ENTER:
            if self.state == "track":
                self.state = "gate"
            elif self.state == "gate":
                self.export()
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
        elif symbol == key.RSHIFT:
            self.screenshot = True

    def on_mouse_press(self, x, y, button, modifiers):
        if button == pyglet.window.mouse.LEFT:

            if self.anchor_x == None:
                self.anchor_x = self.mouse_x
                self.anchor_y = self.mouse_y
                self.select_line = pyglet.shapes.Line(self.anchor_x, self.anchor_y, self.mouse_x, self.mouse_y, 3, color = (80, 225, 30))
                self.anchor_dot = pyglet.shapes.Circle(self.anchor_x, self.anchor_y, 5, color=(255, 0, 0))
            else:
                x1 = self.anchor_x
                y1 = self.anchor_y
                x2, y2 = self.snap_to_point(x, y)
                if self.state == "track":
                    new_line = pyglet.shapes.Line(x1, y1, x2, y2, 3, color = (0, 0, 255))
                    self.track.append(new_line)
                    self.anchor_x = x2
                    self.anchor_y = y2
                    self.anchor_dot.x = self.anchor_x
                    self.anchor_dot.y = self.anchor_y

                    self.select_line.x = self.anchor_x
                    self.select_line.y = self.anchor_y

                if self.state == "gate":
                    new_line = pyglet.shapes.Line(x1, y1, x2, y2, 3, color = (0, 255, 0))
                    self.gates.append(new_line)
                    self.anchor_x = None
                    self.anchor_y = None
                    self.select_line = None
                    self.anchor_dot = None

        if button == pyglet.window.mouse.RIGHT:
            
            self.anchor_x = None
            self.anchor_y = None
            self.select_line = None
            self.anchor_dot = None

    def on_key_release(self, symbol, modifiers):
        pass

    def snap_to_point(self, mx, my):
        new_x, new_y = mx, my
        for line in self.track:
            if m.sqrt((line.x2 - mx)**2 + (line.y2 - my)**2) < 10:
                new_x, new_y = line.x2, line.y2
            elif m.sqrt((line.x - mx)**2 + (line.y - my)**2) < 10:
                new_x, new_y = line.x, line.y
        return new_x, new_y
        

    def on_mouse_motion(self, x, y, dx, dy):
        self.mouse_x = x
        self.mouse_y = y

        if not self.cursor_dot:
            self.cursor_dot = pyglet.shapes.Circle(x, y, 5, color=(255, 0, 0))

        if self.select_line:

            x, y = self.snap_to_point(x, y)
            self.select_line.x2 = x
            self.select_line.y2 = y

        x, y = self.snap_to_point(x, y)

        self.cursor_dot.x = x
        self.cursor_dot.y = y
        self.mouse_x = x
        self.mouse_y = y

    def on_draw(self):
        glPushMatrix()
        self.background.draw()

        if not self.screenshot:

            self.pic.blit(0, 0)

        if self.select_line and not self.screenshot:
            self.select_line.draw()

        if not self.screenshot:
            for gate in self.gates:
                gate.draw()
        
        for track in self.track:
            track.draw()

        if self.anchor_dot and not self.screenshot:
            self.anchor_dot.draw()

        if self.cursor_dot and not self.screenshot:
            self.cursor_dot.draw()

        glPopMatrix()

        if self.screenshot:
            pyglet.image.get_buffer_manager().get_color_buffer().save(self.track_name + '_image.png')
            self.screenshot = False

    def update(self, dt):

        pass

if __name__ == "__main__":
    window = GameWindow(windowWidth, windowHeight, "Track Generator", resizable=False)
    # pyglet.clock.schedule_interval(window.update, 1 / frame_rate)
    pyglet.app.run()