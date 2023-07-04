import pyglet
from vector_math import *

class TrackLimit:

    def __init__(self, x, y, x2, y2):
        self.x = x
        self.y = y
        self.x2 = x2
        self.y2 = y2

    def do_collide(self, car):
        w = car.width
        h = car.height

        forward_vector = car.heading
        sideways_vector = vec2(car.heading).rotate(90)
        position = vec2(car.x, car.y)

        corners = []
        corner_multipliers = [[1, 1], [1, -1], [-1, -1], [-1, 1]]

        for i in range(4):
            corners.append(position + (sideways_vector * w / 2 * corner_multipliers[i][0]) + (forward_vector * h / 2 * corner_multipliers[i][1]))

        for i in range(4):
            j = i + 1
            j = j % 4
            if linesCollided(self.x1, self.y1, self.x2, self.y2, corners[i].x, corners[i].y, corners[j].x, corners[j].y):
                return True
        return False