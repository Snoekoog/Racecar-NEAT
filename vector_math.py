import numpy as np
import math as m
import pygame
import pyglet

vec2 = pygame.math.Vector2

# Calculate absolute angle of a vector
def calc_angle(vector):
    if vector.length() == 0:
        return 0
    return m.degrees(m.atan2(vector.y, vector.x))

# Transform radians to degrees
def rad_to_deg(alpha):
    return alpha / m.pi * 180

# Transform degrees to radians
def deg_to_rad(theta):
    return theta / 180 * m.pi

# Get unit vector from angle
def unit_vector_from_angle(theta):
    theta_rad = deg_to_rad(theta)

    return vec2(m.cos(theta_rad), m.sin(theta_rad))

# Check if two lines collide or not
def lines_collided(x1, y1, x2, y2, x3, y3, x4, y4):

    # Yeah this below is a mess but somehow it gave errors sometimes if I did not do this
    # Should probably debug some more
    x1 += 0.01
    x2 -= 0.01
    x3 += 0.01
    x4 -= 0.01
    y1 += 0.01
    y2 -= 0.01
    y3 += 0.01
    y4 -= 0.01
    uA = ((x4 - x3) * (y1 - y3) - (y4 - y3) * (x1 - x3)) / ((y4 - y3) * (x2 - x1) - (x4 - x3) * (y2 - y1))
    uB = ((x2 - x1) * (y1 - y3) - (y2 - y1) * (x1 - x3)) / ((y4 - y3) * (x2 - x1) - (x4 - x3) * (y2 - y1))
    if 0 <= uA <= 1 and 0 <= uB <= 1:
        return True
    return False

# Get actual collision point between two lines
def get_collision_point(x1, y1, x2, y2, x3, y3, x4, y4):

    # Yeah this below is a mess but somehow it gave errors sometimes if I did not do this
    # Should probably debug some more
    x1 += 0.01
    x2 -= 0.01
    x3 += 0.01
    x4 -= 0.01
    y1 += 0.01
    y2 -= 0.01
    y3 += 0.01
    y4 -= 0.01
    uA = ((x4 - x3) * (y1 - y3) - (y4 - y3) * (x1 - x3)) / ((y4 - y3) * (x2 - x1) - (x4 - x3) * (y2 - y1))
    uB = ((x2 - x1) * (y1 - y3) - (y2 - y1) * (x1 - x3)) / ((y4 - y3) * (x2 - x1) - (x4 - x3) * (y2 - y1))
    if 0 <= uA <= 1 and 0 <= uB <= 1:
        intersectionX = x1 + (uA * (x2 - x1))
        intersectionY = y1 + (uA * (y2 - y1))
        return vec2(intersectionX, intersectionY)
    return None

# Check if a car collides with a track limit
def do_collide(track_limit, car):
    w = car.w
    h = car.l

    forward_vector = car.heading
    sideways_vector = vec2(car.heading).rotate(90)
    position = vec2(car.x, car.y)

    corners = []
    corner_multipliers = [[1, 1], [1, -1], [-1, -1], [-1, 1]]

    if track_limit['x'] == track_limit['x2']:
        track_limit['x'] += 1
    if track_limit['y'] == track_limit['y2']:
        track_limit['y'] += 1

    for i in range(4):
        corners.append(position + (sideways_vector * w / 2 * corner_multipliers[i][0]) + (forward_vector * h / 2 * corner_multipliers[i][1]))

    for i in range(4):
        j = i + 1
        j = j % 4
        if lines_collided(track_limit['x'], track_limit['y'], track_limit['x2'], track_limit['y2'], corners[i].x, corners[i].y, corners[j].x, corners[j].y):
            return True
    return False

# Get Euclidean distance between two points
def dist(x1, y1, x2, y2):
    return m.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)