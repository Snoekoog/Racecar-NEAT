import numpy as np
import math as m
import pygame
import pyglet

vec2 = pygame.math.Vector2
# vec2 = pyglet.math.Vec2

def calc_angle(vector):
    if vector.length() == 0:
        return 0
    return m.degrees(m.atan2(vector.y, vector.x))

def rad_to_deg(alpha):
    return alpha / m.pi * 180

def deg_to_rad(theta):
    return theta / 180 * m.pi

def unit_vector_from_angle(theta):
    theta_rad = deg_to_rad(theta)

    return vec2(m.cos(theta_rad), m.sin(theta_rad))

def linesCollided(x1, y1, x2, y2, x3, y3, x4, y4):
    # print(x1, y1, x2, y2, x3, y3, x4, y4)
    x1 += 0.01
    uA = ((x4 - x3) * (y1 - y3) - (y4 - y3) * (x1 - x3)) / ((y4 - y3) * (x2 - x1) - (x4 - x3) * (y2 - y1))
    uB = ((x2 - x1) * (y1 - y3) - (y2 - y1) * (x1 - x3)) / ((y4 - y3) * (x2 - x1) - (x4 - x3) * (y2 - y1))
    if 0 <= uA <= 1 and 0 <= uB <= 1:
        return True
    return False

def getCollisionPoint(x1, y1, x2, y2, x3, y3, x4, y4):
    global vec2
    # print(x1, y1, x2, y2, x3, y3, x4, y4)
    x1 += 0.01
    uA = ((x4 - x3) * (y1 - y3) - (y4 - y3) * (x1 - x3)) / ((y4 - y3) * (x2 - x1) - (x4 - x3) * (y2 - y1))
    uB = ((x2 - x1) * (y1 - y3) - (y2 - y1) * (x1 - x3)) / ((y4 - y3) * (x2 - x1) - (x4 - x3) * (y2 - y1))
    if 0 <= uA <= 1 and 0 <= uB <= 1:
        intersectionX = x1 + (uA * (x2 - x1))
        intersectionY = y1 + (uA * (y2 - y1))
        return vec2(intersectionX, intersectionY)
    return None

def dist(x1, y1, x2, y2):
    return m.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)