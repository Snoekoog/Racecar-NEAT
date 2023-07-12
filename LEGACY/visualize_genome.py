import pyglet
from pyglet.gl import *
from pyglet.window import key
import json
from racegame.config import windowHeight, windowWidth, frame_rate
import time
import os
import pickle

class NetworkWindow(pyglet.window.Window):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        backgroundColor = [255, 255, 255, 255]
        # backgroundColor = [i / 255 for i in backgroundColor]
        glClearColor(*backgroundColor)
        genome_file = open('./Results/silverstone-FDNEAT-run-3', 'rb')
        genome = pickle.load(genome_file)
        genome_file.close()
        self.genome = genome

    def on_close(self):
        self.close()

    def on_draw(self):
        self.clear()
        glPushMatrix()
        layers = set()
        draw_objects = []
        node_lookup = {}
        for node in self.genome.nodes:
            layers.add(node.layer)
        for layer in list(layers):
            x_pos = windowWidth - 30 - (1 - layer) * 1200
            layer_nodes = self.genome.get_nodes_by_layer(layer)
            num_nodes = len(layer_nodes)
            for i in range(num_nodes):
                y_pos = windowHeight - 10 - ((i + 1) / (num_nodes + 1)) * 700
                node_lookup[layer_nodes[i].ID] = {"x": x_pos, "y": y_pos}
                if layer_nodes[i].type == "input" or layer_nodes[i].type == "output" or layer_nodes[i].type == "hidden":
                    color = (0, 0, 255)
                elif layer_nodes[i].type == "bias":
                    color = (248, 255, 48)
                node_circle = pyglet.shapes.Circle(x_pos, y_pos, 20, color = color)
                draw_objects.append(node_circle)

        for connection in self.genome.connections:
            origin_node = node_lookup[connection.origin_node_ID]
            target_node = node_lookup[connection.target_node_ID]
            if connection.origin_node_ID != connection.target_node_ID:
                x1 = origin_node['x']
                y1 = origin_node['y']
                x2 = target_node['x']
                y2 = target_node['y']
                size = max(1, int((abs(connection.weight) / 10) * 16))
                color = (0, 255, 0) if origin_node['x'] <= target_node['x'] else (255, 0, 0)
                color = (int(130 - connection.weight / 10 * 130), int(130 + connection.weight / 10 * 125), 0) if connection.weight >= 0 else (int(130 - connection.weight / 10 * 125), int(130 + connection.weight / 10 * 130), 0)
                connection_line = pyglet.shapes.Line(x1, y1, x2, y2, width = size, color = color)
                draw_objects.append(connection_line)
            else:
                x1 = origin_node['x']
                y1 = origin_node['y'] - 5
                x2 = origin_node['x'] + 10
                y2 = origin_node['y']
                x3 = origin_node['x']
                y3 = origin_node['y'] + 5
                size = max(1, int((abs(connection.weight) / 10) * 16))
                color = (0, 0, 255)
                connection_line1 = pyglet.shapes.Line(x1, y1, x2, y2, width = size, color = color)
                connection_line2 = pyglet.shapes.Line(x2, y2, x3, y3, width = size, color = color)
                draw_objects.append(connection_line1)
                draw_objects.append(connection_line2)

        for i in range(len(draw_objects)):
            draw_objects[len(draw_objects) - i - 1].draw()
        glPopMatrix()

    def on_key_press(self, symbol, modifiers):
        if symbol == key.ESCAPE:
            self.close()

if __name__ == "__main__":
    window = NetworkWindow(windowWidth, windowHeight, "Genome", resizable=False)
    pyglet.app.run()