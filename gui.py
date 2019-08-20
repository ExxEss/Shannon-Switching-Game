import vlc
import tkinter as tk
from typing import List
from graph import *

GRAY = '#AAAAAA'
DARK_GRAY = '#666666'
JADE = '#5DE1C0'
RED = '#A21E3F'
BLUE = '#0099CC'
DARK = '#2F3640'
BLACK = '#000000'

ANIMATION_DURATION = 2000
SEPARATION_UNIT = 2

CIRCLE_RADIUS = 25
VERTEX_RADIUS = 6

VERTEX_DISTANCE_ERROR = 200
TEXT_DISTANCE_ERROR = 500

EDGE_START_POINT = 0
EDGE_END_POINT = 1
NOT_EDGE_ENDPOINT = -1

old_posX = 0
old_posY = 0

items = []
vertex_num = 0

last_edge = None
is_new_edge_created = False

gui = tk.Tk()
gui.title('Spanning Tree (ST)')
gui.geometry('800x1000+320+0')

canvas = tk.Canvas(gui, bg=DARK, width=600, height=600,
                   highlightthickness=0, relief='ridge')

canvas.grid()

button_play = canvas.create_oval(300 - CIRCLE_RADIUS,
                                 530 - CIRCLE_RADIUS,
                                 300 + CIRCLE_RADIUS,
                                 530 + CIRCLE_RADIUS,
                                 fill=RED, outline=GRAY,
                                 width=2)

button_text = canvas.create_text(300, 530, fill=GRAY,
                                 font='Times 15 italic bold',
                                 text='Play')

canvas.create_line(30, 30, 100, 30, fill=GRAY)
canvas.create_line(30, 50, 100, 50, fill=BLUE)
canvas.create_line(30, 70, 100, 70, fill=JADE)
canvas.create_line(30, 90, 100, 90, fill=RED)
canvas.create_line(30, 110, 100, 110, fill=BLACK)

canvas.create_text(195, 30, fill=GRAY, font='Times 15 bold',
                   text='Edge without being used')

canvas.create_text(193, 50, fill=BLUE, font='Times 15 bold',
                   text='Edge of an arbitrary ST')

canvas.create_text(178, 70, fill=JADE, font='Times 15 bold',
                   text='Edge of the first ST')

canvas.create_text(187, 90, fill=RED, font='Times 15 bold',
                   text='Edge of the second ST')

canvas.create_text(191, 110, fill=BLACK, font='Times 15 bold',
                   text='Edge belong to each ST')

canvas.create_rectangle(20, 15, 290, 125)

coordinates = {'x': 0, 'y': 0, 'x2': 0, 'y2': 0}


# Resize background and adjust button's position.
def resize_bg(e):
    canvas.config(width=e.width, height=e.height)
    canvas.coords(button_play,
                  e.width / 2 - CIRCLE_RADIUS,
                  int(e.height * 0.9) - 2 * CIRCLE_RADIUS,
                  e.width / 2 + CIRCLE_RADIUS,
                  int(e.height * 0.9))

    canvas.coords(button_text, e.width / 2,
                  int(e.height * 0.9) - CIRCLE_RADIUS)


# Click event for start to draw line.
def click(e):
    # Define start point for line
    coordinates['x'] = e.x
    coordinates['y'] = e.y

    # Create a edge on this point and store it in the list
    global last_edge
    last_edge = canvas.create_line(coordinates['x'],
                                   coordinates['y'],
                                   coordinates['x'],
                                   coordinates['y'],
                                   fill=GRAY,
                                   width=2)


# Drag event for drawing line.
def drag(e):
    # Update the coordinates from the event
    coordinates['x2'] = e.x
    coordinates['y2'] = e.y

    # Change the coordinates of the last created line to the new coordinates
    global last_edge
    canvas.coords(last_edge,
                  coordinates['x'], coordinates['y'],
                  coordinates['x2'], coordinates['y2'])

    global is_new_edge_created
    is_new_edge_created = True

    # Put gui_vertexes on top layer
    lift(vertexes)


# For showing name(text) of each vertex more beautifully,
# adjust name's position when it is overlapped with some line.
def adjust_text_pos(_):
    abs_coord_x = gui.winfo_pointerx() - gui.winfo_rootx()
    abs_coord_y = gui.winfo_pointery() - gui.winfo_rooty()

    for vertex in vertexes:
        text_coord = canvas.coords(vertex.text)

        if ((abs_coord_x - text_coord[0]) ** 2
                + (abs_coord_y - text_coord[1]) ** 2
                < TEXT_DISTANCE_ERROR):
            canvas.coords(vertex.text,
                          abs_coord_x,
                          abs_coord_y)


# Make sure that texts and circles always are drawn on top layer
# compare to line.
def lift(vertexes_list):
    for vertex in vertexes_list:
        canvas.tag_raise(vertex.circle)
        canvas.tag_raise(vertex.text)


def add_edge(_):
    global is_new_edge_created

    if is_new_edge_created:
        new_edge = Edge(last_edge)
        edges.append(new_edge)
        items.append(new_edge)
        is_new_edge_created = False


def create_vertex(e):
    global vertex_num, old_posX, old_posY

    # Here we need to avoid that the last created vertex is overlapped with
    # the second last created vertex.
    if (old_posX - e.x) ** 2 + (old_posY - e.y) ** 2 > 1000:
        circle = canvas.create_oval(e.x - VERTEX_RADIUS,
                                    e.y - VERTEX_RADIUS,
                                    e.x + VERTEX_RADIUS,
                                    e.y + VERTEX_RADIUS,
                                    fill=RED,
                                    outline=GRAY,
                                    width=2)

        text = canvas.create_text(e.x, e.y,
                                  fill=GRAY,
                                  font='Times 8 italic bold',
                                  text=('%d' % vertex_num))
        play_sound()

        new_vertex = Vertex(vertex_num, circle, text)

        vertexes.append(new_vertex)
        items.append(new_vertex)

        old_posX = e.x
        old_posY = e.y

        vertex_num += 1


def play_sound():
    sound_file = vlc.MediaPlayer('/Users/EssExx/'
                                 'Documents/vertex.wav')
    sound_file.play()
    sound_file.audio_set_volume(3)


# Undo the creation of the last edge or vertex.
def undo(e):
    add_edge(e)
    global vertex_num

    if not len(items):
        return

    item = items[-1]

    if type(item) == Vertex:
        vertexes.remove(item)
        canvas.delete(item.circle)
        canvas.delete(item.text)
        vertex_num -= 1
    else:
        edges.remove(item)
        canvas.delete(item.line)

    del items[-1]


# For making some animation when we want replay the game.
def change_button_color(animation: bool):
    if animation:
        canvas.itemconfig(button_play, fill=GRAY)

    canvas.after(50, (lambda:
                      canvas.itemconfig(button_play, fill=RED)))


def change_button_text():
    canvas.itemconfig(button_text, text='Replay')


# One all vertexes and edges are created, then all the connections
# and the structure of the graph must be established by finding every
# vertex's adjacent vertexes.
def construct_graph(vertexes_list: List[Vertex]):
    for vertex in vertexes_list:
        vertex.neighbors = find_neighbors(vertex)


# Connect the adjacent vertexes
def find_neighbors(vertex: Vertex) -> List[List]:
    neighbors = []

    for edge in edges:
        pos = check_coincidence(vertex, edge)

        if pos != NOT_EDGE_ENDPOINT:
            neighbor_vertex = find_neighbor(edge, pos)
        else:
            continue

        neighbors.append([neighbor_vertex, edge])
        edge.endpoints.append(vertex)

    return neighbors


# Also we need find out two endpoints of each edge(line), thus we will
# three possible result.
def check_coincidence(vertex: Vertex, edge: Edge) -> int:
    if is_coincidental(vertex, edge, EDGE_START_POINT):
        return EDGE_START_POINT

    if is_coincidental(vertex, edge, EDGE_END_POINT):
        return EDGE_END_POINT

    return NOT_EDGE_ENDPOINT


# Verify if the given vertex is a specific endpoint of the given edge.
def is_coincidental(vertex: Vertex, edge: Edge, pos: int) -> bool:
    circle_coordinate = canvas.coords(vertex.circle)
    line_coordinate = canvas.coords(edge.line)

    x1 = circle_coordinate[0] + VERTEX_RADIUS
    y1 = circle_coordinate[1] + VERTEX_RADIUS

    x2 = line_coordinate[2 * pos]
    y2 = line_coordinate[2 * pos + 1]

    if (x1 - x2) ** 2 + (y1 - y2) ** 2 < \
            VERTEX_DISTANCE_ERROR:
        return True
    return False


# Find all endpoints of a given edge.
def find_neighbor(edge: Edge, pos: int) -> Vertex:
    for vertex in vertexes:

        # Find coincident vertex of the edge's another endpoint
        if is_coincidental(vertex, edge, 1 - pos):
            return vertex


# For easing to debug, this function print the constructed graph in simple way.
def print_graph(vertex_list: List[Vertex], edge_list: List[Edge]):
    for vertex in vertex_list:
        print(vertex.index)

        for neighbor in vertex.neighbors:
            if neighbor[1] in edge_list:
                print('|')
                print(' ---->', neighbor[0].index)

        print('')
