import pygame
import numpy as np
vec2 = pygame.math.Vector2
import math as m
import random
from itertools import count

# node_3_input = 1 * -1.3163 + 1 * 1.10248 + 0 * 7.82985
# node_3_output = (1.0 / (1.0 + np.exp(-node_3_input/0.0981948))) * 2.0 - 1.0
# print(node_3_output)
n_look_directions = 8
for i in range(n_look_directions):
    relative_angle = -90 + i * (180 / (n_look_directions - 1))
    print(relative_angle)