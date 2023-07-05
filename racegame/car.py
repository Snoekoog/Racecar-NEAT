import numpy as np
import pyglet
from racegame.config import windowWidth, windowHeight
from vector_math import *

class Car:

    def __init__(self, neural_network, initial_x, initial_y, initial_heading):
        self.brain = neural_network
        self.x = initial_x
        self.y = initial_y
        self.v = 0
        self.a = 0
        self.w = 10
        self.l = 20
        self.heading = initial_heading
        self.fitness = 0

        self.turning_rate = 5.0 / self.l
        self.friction = 0.98
        self.max_speed = self.l / 2
        self.max_reverse_speed = -1 * self.l / 2
        self.a_speed = self.l / 160
        self.active = True
        self.drift_momentum = 0
        self.drift_friction = 0.87
        self.line_collision_points = []
        self.collision_line_distances = []
        self.vector_length = 300
        self.color = (200, 20, 20)
        self.is_idling = 0

        self.next_sector = 0
        self.laps = 0
        self.n_look_directions = 8
        self.max_radar_distance = 300
        self.gas_magnitude = 0
        self.is_steering_left = 0
        
        self.steer_input = 0
        self.throttle_input = 0

        self.state = 'idle'

        self.vehicle_pixel_art = pyglet.image.load("./racegame/assets/racecar-pixel-art.png")
        self.vehicle_sprite = pyglet.sprite.Sprite(self.vehicle_pixel_art, x = 2 * windowWidth, y = 2 * windowHeight)

        self.reset_controls()

        self.vehicle = pyglet.shapes.Rectangle(self.x - 0.5 * self.w, self.y - 0.5 * self.l, self.l, self.w, color = self.color)
        # self.test = pyglet.shapes.Rectangle(windowWidth / 2, windowHeight / 2, 20, 80, color=(0, 0, 255))
        self.view_vector = pyglet.shapes.Line(self.x, self.y, self.x + self.heading.x * 40, self.y + self.heading.y * 40, color = self.color)

    def draw(self):

        # self.vehicle.delete()
        side_vector = self.heading.rotate(90)
        # anchor_x = self.x - (self.heading.x * 0.5 * self.l + side_vector.x * 0.5 * self.w)
        # anchor_y = self.y - (self.heading.y * 0.5 * self.l + side_vector.y * 0.5 * self.w)
        anchor_x2 = self.x - (self.heading.x * 0.5 * self.l - side_vector.x * 0.5 * self.w)
        anchor_y2 = self.y - (self.heading.y * 0.5 * self.l - side_vector.y * 0.5 * self.w)
        # rotation_angle = calc_angle(self.heading)
        rotation_angle2 = calc_angle(self.heading) + 270
        # self.vehicle.position = (anchor_x, anchor_y)
        # self.vehicle.rotation = -rotation_angle
        self.vehicle_sprite.position = (anchor_x2, anchor_y2)
        self.vehicle_sprite.rotation = -rotation_angle2
        # self.vehicle.draw()
        self.vehicle_sprite.draw()

        # self.view_vector.x = self.x
        # self.view_vector.y = self.y
        # self.view_vector.x2 = self.x + self.heading.x * 40
        # self.view_vector.y2 = self.y + self.heading.y * 40
        # self.view_vector.draw()

        # self.test.rotation = -rotation_angle
        # self.test.draw()

    def update_radar(self, track_limits):
        self.line_collision_points[:] = []
        self.collision_line_distances[:] = []

        for i in range(self.n_look_directions):
            relative_angle = -90 + i * (180 / (self.n_look_directions - 1))
            self.radar_measurement(relative_angle, track_limits)

    def find_closest_object(self, x1, y1, x2, y2, track_limits):
        minimal_distance = 2 * windowWidth
        closest_collision_point = vec2(0, 0)
        for track_limit in track_limits:
            collision_point = getCollisionPoint(x1, y1, x2, y2, track_limit['x'], track_limit['y'], track_limit['x2'], track_limit['y2'])
            if collision_point == None:
                continue
            if dist(x1, y1, collision_point.x, collision_point.y) < minimal_distance:
                minimal_distance = dist(x1, y1, collision_point.x, collision_point.y)
                closest_collision_point = vec2(collision_point)
        return closest_collision_point

    def radar_measurement(self, relative_angle, track_limits):

        absolute_radar_heading = self.heading.rotate(relative_angle)
        absolute_radar_heading = absolute_radar_heading.normalize() * self.max_radar_distance
        collision_point = self.find_closest_object(self.x, self.y, self.x + absolute_radar_heading.x, self.y + absolute_radar_heading.y, track_limits)

        if collision_point.x == 0 and collision_point.y == 0:
            self.collision_line_distances.append(self.max_radar_distance)
        else:
            self.collision_line_distances.append(dist(self.x, self.y, collision_point.x, collision_point.y))

        self.line_collision_points.append(collision_point)

        for i in range(self.n_look_directions):
            angle = -90 + i * (180 / (self.n_look_directions - 1))


    def update_control_state(self):

        self.reset_controls()
        if 'accelerating' in self.state:
            self.is_accelerating = True
        if 'left' in self.state:
            self.is_steering_left = True
        if 'right' in self.state:
            self.is_steering_right = True
        if 'reversing' in self.state:
            self.is_reversing = True

    def reset_controls(self):
        self.is_accelerating    = False
        self.is_reversing       = False
        self.is_steering_left   = False
        self.is_steering_right  = False

    def compute(self, measured_state):
        outputs = self.brain.feed_forward(measured_state)

        gas = outputs[0]
        if gas >= 0:
            self.is_accelerating = True
        else:
            self.is_reversing = True
        self.gas_magnitude = abs(gas)
        self.throttle_input = gas

        steering_angle = outputs[1]
        self.steer_input = steering_angle

        if steering_angle >= 0:
            self.is_steering_right = True
        else:
            self.is_steering_left = True
        self.steer_magnitude = abs(steering_angle)

        # speed output node between -1 and 1, -1 is full reverse, 1 is full speed
        # steer output node between -1 and 1, -1 full left and 1 full right

    def measure_state(self, track_limits, next_reward_sector):
        self.update_radar(track_limits)

        gate_center = vec2((next_reward_sector['x'] + next_reward_sector['x2']) / 2, (next_reward_sector['y'] + next_reward_sector['y2']) / 2)
        relative_position = gate_center - vec2(self.x, self.y)

        # normalised_radar_distances = [1 - (max(1, distance) / self.max_radar_distance) for distance in self.collision_line_distances]
        normalised_radar_distances = [(max(1, distance) / self.max_radar_distance) for distance in self.collision_line_distances]

        normalised_speed = self.v / self.max_speed
        normalised_drift_speed = self.drift_momentum / 5

        normalized_target_heading = (calc_angle(self.heading) - calc_angle(relative_position)) % 360
        if normalized_target_heading > 180:
            normalized_target_heading = -1 * (360 - normalized_target_heading)
        normalized_target_heading /= 180

        normalized_state = [*normalised_radar_distances, normalised_speed, normalised_drift_speed, normalized_target_heading]

        return np.array(normalized_state)

    def update_movement(self):
        drift_factor = 1
        if abs(self.v) < 5:
            drift_factor = abs(self.v) / 5.0
        if self.v < 0:
            drift_factor *= -1

        drift_momentum_change = self.v * self.turning_rate * self.w  / (9.0 * 4.0)
        if self.v < 5:
            drift_momentum_change = 0

        # if self.is_steering_left:
        #     self.heading = self.heading.rotate(rad_to_deg(self.turning_rate) * drift_factor * self.steer_magnitude)
        #     self.drift_momentum -= drift_momentum_change

        # elif self.is_steering_right:
        #     self.heading = self.heading.rotate(-rad_to_deg(self.turning_rate) * drift_factor * self.steer_magnitude)
        #     self.drift_momentum += drift_momentum_change

        self.heading = self.heading.rotate(rad_to_deg(self.turning_rate) * drift_factor * self.steer_input)
        self.drift_momentum -= drift_momentum_change * np.sign(self.steer_input)

        self.a = 0
        # if self.is_accelerating:
        #     if self.v < 0:
        #         self.a = 3 * self.a_speed
        #     else:
        #         self.a = 1 * self.a_speed
        # if self.is_reversing:
        #     if self.v > 0:
        #         self.a = -3 * self.a_speed
        #     else:
        #         self.a = -1 * self.a_speed

        self.a = self.a_speed * self.throttle_input
        if (self.v < 0 and self.throttle_input > 0) or (self.v > 0 and self.throttle_input < 0):
            self.a *= 3

        # self.v += self.a * self.gas_magnitude
        self.v += self.a
        self.v *= self.friction
        self.v = np.clip(self.v, self.max_reverse_speed, self.max_speed)

        if abs(self.v) < 0.01:
            self.is_idling += 1
        else:
            self.is_idling = 0

        drift_vector = vec2(self.heading).rotate(90)
        position_change = vec2(0, 0)
        position_change.x += self.v * self.heading.x
        position_change.x += self.drift_momentum * drift_vector.x
        position_change.y += self.v * self.heading.y
        position_change.y += self.drift_momentum * drift_vector.y
        self.drift_momentum *= self.drift_friction

        if position_change.length() != 0:
            position_change.normalize()

        position_change.x * abs(self.v)
        position_change.y * abs(self.v)

        self.x += position_change.x
        self.y += position_change.y

    def update(self, track_limits, next_reward_sector):
        self.reset_controls()
        # print('measuring state')
        measured_state = self.measure_state(track_limits, next_reward_sector)
        # print('Done measuring. Going to compute')
        self.compute(measured_state)
        # self.think()
        # self.update_control_state()
        self.update_movement()
        # print('Done updating movement')
        # check wall hit --> death
        # check reward --> update score
        # set new vision vectors
        pass

    def show_radar(self):
        for point in self.line_collision_points:
            point = pyglet.shapes.Circle(point.x, point.y, 3, color = (255, 0, 0))
            point.draw()


# my_car = Car([], [], 'a')
# print(my_car.is_accelerating)