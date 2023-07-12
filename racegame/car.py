import numpy as np
import pyglet
from racegame.config import windowWidth, windowHeight
from vector_math import *

class Car:

    def __init__(self, neural_network, initial_x: int, initial_y: int, initial_heading: float, is_champion: bool = False):

        self.brain                      = neural_network    # Neural Network controller
        self.x                          = initial_x         # Start X position
        self.y                          = initial_y         # Start Y position
        self.v                          = 0                 # Velocity
        self.a                          = 0                 # Acceleration
        self.w                          = 10                # Width of the vehicle
        self.l                          = 20                # Length of the vehicle
        self.heading                    = initial_heading   # Start heading

        self.turning_rate               = 5.0 / self.l      # Turning rate of the vehicle while steering fully to one side
        self.friction                   = 0.98              # Friction (for slowing down while in neutral)
        self.max_speed                  = self.l / 2        # Max allowable speed
        self.max_reverse_speed          = -1 * self.l / 2   # Max allowable reverse speed
        self.a_speed                    = self.l / 160      # Change in acceleration
        self.active                     = True              # Is this agent active?
        self.drift_momentum             = 0                 # Accumulated drift momentum
        self.drift_friction             = 0.87              # Friction during drift (drift decay)
        self.line_collision_points      = []                # List of points where distance measurements cross track limits
        self.collision_line_distances   = []                # Distances of those points to the car
        self.is_idling                  = 0                 # Number of timesteps the agent has been idling for (standing still)
        self.next_sector                = 0                 # Index of next sector
        self.laps                       = 0                 # Number of laps completed by the agent
        self.n_look_directions          = 8                 # Number of directions for the measurement 'beams'
        self.max_radar_distance         = 300               # Max measurable distance (further away gets capped by this number)
        
        self.steer_input                = 0                 # Action vector: steer input
        self.throttle_input             = 0                 # Action vector: throttle input

        # Pick the correct car livery
        if not is_champion:
            self.vehicle_pixel_art = pyglet.image.load("./racegame/assets/racecar-pixel-art.png")
        else:
            self.vehicle_pixel_art = pyglet.image.load("./racegame/assets/racecar-pixel-art-v2.png")

        # Create sprite from pixel art
        self.vehicle_sprite = pyglet.sprite.Sprite(self.vehicle_pixel_art, x = 2 * windowWidth, y = 2 * windowHeight)


    # Draw the car to the window
    def draw(self):

        # Sideways pointing vector
        side_vector = self.heading.rotate(90)

        # Calculate X and Y anchor points for sprite (self.x and self.y are mid point of vehicle)
        anchor_x2 = self.x - (self.heading.x * 0.5 * self.l - side_vector.x * 0.5 * self.w)
        anchor_y2 = self.y - (self.heading.y * 0.5 * self.l - side_vector.y * 0.5 * self.w)

        # Calculate right angle to angle the sprite correctly
        rotation_angle2 = calc_angle(self.heading) + 270

        # Update sprite position and rotation
        self.vehicle_sprite.position = (anchor_x2, anchor_y2)
        self.vehicle_sprite.rotation = -rotation_angle2

        # Draw sprite to screen
        self.vehicle_sprite.draw()


    # Update radar measurements
    def update_radar(self, track_limits: list):

        # Empty the lists from the previous time-step
        self.line_collision_points[:] = []
        self.collision_line_distances[:] = []

        # Loop through the number of directions
        for i in range(self.n_look_directions):

            # Calculate corresponding relative angle
            relative_angle = -90 + i * (180 / (self.n_look_directions - 1))

            # Perform measurement
            self.radar_measurement(relative_angle, track_limits)

    # Raycast to find next collision with a line (track limit)
    def find_closest_object(self, x1: int, y1: int, x2: int, y2: int, track_limits: list):

        # Placeholder for closest collision point distance. Initiate as very far distance.
        minimal_distance = 2 * windowWidth

        # Create vec2 to hold collision point
        closest_collision_point = vec2(0, 0)

        # Loop through track limits
        for track_limit in track_limits:

            # Determine collision point with track limit
            collision_point = get_collision_point(x1, y1, x2, y2, track_limit['x'], track_limit['y'], track_limit['x2'], track_limit['y2'])

            # If no such collision point exists, go to next track limit in loop
            if collision_point == None:
                continue

            # If the distance is below the minimal distance, we have a new closest point
            if dist(x1, y1, collision_point.x, collision_point.y) < minimal_distance:

                # Update minimal distance and collision point vec2
                minimal_distance = dist(x1, y1, collision_point.x, collision_point.y)
                closest_collision_point = vec2(collision_point)

        # Return closest point
        return closest_collision_point

    # Perform a single radar measurement
    def radar_measurement(self, relative_angle: float, track_limits: list):

        # Transform relative radar heading to absolute window frame heading
        absolute_radar_heading = self.heading.rotate(relative_angle)

        # Create vector pointing in the right direction, with max allowable length
        absolute_radar_heading = absolute_radar_heading.normalize() * self.max_radar_distance

        # Find collision point
        collision_point = self.find_closest_object(self.x, self.y, self.x + absolute_radar_heading.x, self.y + absolute_radar_heading.y, track_limits)

        # If no collision point exists (too far away or nothing in its way), set to max distance
        if collision_point.x == 0 and collision_point.y == 0:
            self.collision_line_distances.append(self.max_radar_distance)

        # Else we do have a collision between the raycast line and track limit.
        # Add collision distance to list
        else:
            self.collision_line_distances.append(dist(self.x, self.y, collision_point.x, collision_point.y))

        # Add collision point to list too, for visualisation purposes
        self.line_collision_points.append(collision_point)


    # Compute next action from observations using network (brain)
    def compute(self, measured_state: list):

        # Feed state to network and obtain output
        outputs = self.brain.feed_forward(measured_state)

        # Throttle and steering input come directly from network output
        self.throttle_input = outputs[0]
        self.steer_input = outputs[1]

        # speed output node between -1 and 1, -1 is full reverse, 1 is full speed
        # steer output node between -1 and 1, -1 full left and 1 full right

    # Measure current state
    def measure_state(self, track_limits, next_reward_sector):

        # First, simply update radar measurements
        self.update_radar(track_limits)

        # Get center of next reward gate, and get vector from self towards it. Then determine target heading
        gate_center = vec2((next_reward_sector['x'] + next_reward_sector['x2']) / 2, (next_reward_sector['y'] + next_reward_sector['y2']) / 2)
        relative_position = gate_center - vec2(self.x, self.y)
        normalized_target_heading = (calc_angle(self.heading) - calc_angle(relative_position)) % 360
        if normalized_target_heading > 180:
            normalized_target_heading = -1 * (360 - normalized_target_heading)
        normalized_target_heading /= 180

        # Then, normalise radar distances so they are in [0, 1]
        normalised_radar_distances = [(max(1, distance) / self.max_radar_distance) for distance in self.collision_line_distances]

        # Then, normalise speed and drift speed
        normalised_speed = self.v / self.max_speed
        normalised_drift_speed = self.drift_momentum / 5

        # Create list of normalized state
        normalized_state = [*normalised_radar_distances, normalised_speed, normalised_drift_speed, normalized_target_heading]

        # Return as numpy array
        return np.array(normalized_state)

    # Update movement during time-step
    def update_movement(self):

        # Reset drift factor
        drift_factor = 1

        # Logic to determine drift factor according to speed
        if abs(self.v) < 5:
            drift_factor = abs(self.v) / 5.0
        if self.v < 0:
            drift_factor *= -1

        # Calculate drift momentum change
        drift_momentum_change = self.v * self.turning_rate * self.w  / (9.0 * 4.0)
        if self.v < 5:
            drift_momentum_change = 0

        # When steering, update heading
        self.heading = self.heading.rotate(rad_to_deg(self.turning_rate) * drift_factor * self.steer_input)

        # When steering, update drift momentum
        self.drift_momentum -= drift_momentum_change * np.sign(self.steer_input)

        # Reset acceleration
        self.a = 0

        # Set acceleration according to throttle
        self.a = self.a_speed * self.throttle_input
        if (self.v < 0 and self.throttle_input > 0) or (self.v > 0 and self.throttle_input < 0):
            self.a *= 3

        # Update speed according to friction and acceleration. Also limit it by max speeds
        self.v += self.a
        self.v *= self.friction
        self.v = np.clip(self.v, self.max_reverse_speed, self.max_speed)

        # If the agent is pretty much standing still, add one to idling counter
        if abs(self.v) < 0.01:
            self.is_idling += 1
        else:
            self.is_idling = 0

        # Create drift vector
        drift_vector = vec2(self.heading).rotate(90)

        # Create vector to hold position change, and add changes to it
        position_change = vec2(0, 0)
        position_change.x += self.drift_momentum * drift_vector.x + self.v * self.heading.x
        position_change.y += self.drift_momentum * drift_vector.y + self.v * self.heading.y

        # Also update drift momentum decay
        self.drift_momentum *= self.drift_friction

        # Normalize position change so we can multiply it by speed later
        if position_change.length() != 0:
            position_change.normalize()

        # Then multiply by speed
        position_change.x * abs(self.v)
        position_change.y * abs(self.v)

        # Update location
        self.x += position_change.x
        self.y += position_change.y

    # Update full state of vehicle
    def update(self, track_limits: list, next_reward_sector: list):

        # Measure state and obtain it
        measured_state = self.measure_state(track_limits, next_reward_sector)

        # Compute and take action
        self.compute(measured_state)

        # Update state
        self.update_movement()

    # (UNUSED) visualisation: show collision points between radar and track limits
    def show_radar(self):
        for point in self.line_collision_points:
            point = pyglet.shapes.Circle(point.x, point.y, 3, color = (255, 0, 0))
            point.draw()
