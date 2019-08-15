import os
import vlc
import queue
import tkinter as tk
from typing import List, Tuple

# <------------------------------ Gui part 1 ------------------------------>


gui = tk.Tk()
gui.title('Spanning Tree (ST)')
gui.geometry('800x1000+320+0')

GRAY = '#AAAAAA'
JADE = '#5DE1C0'
RED = '#A21E3F'
BLUE = '#0099CC'
DARK = '#2F3640'
BLACK = '#000000'

ANIMATION_DURATION = 2000
SEPARATION_UNIT = 2

event_msj = None

canvas = tk.Canvas(gui, bg=DARK, width=600, height=600,
                   highlightthickness=0, relief='ridge')

canvas.grid()

CIRCLE_RADIUS = 25

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

# Keep a reference to all edges by keeping them in a list.
edges = []
items = []

last_edge = None
is_new_edge_created = False

vertex_num = 0
VERTEX_RADIUS = 6

old_posX = 0
old_posY = 0

VERTEX_DISTANCE_ERROR = 200
TEXT_DISTANCE_ERROR = 500

vertexes = []

EDGE_START_POINT = 0
EDGE_END_POINT = 1
NOT_EDGE_ENDPOINT = -1


def main_workflow():
    canvas.bind('<Button-1>', click)
    canvas.bind('<Double-1>', create_vertex)
    canvas.bind('<B1-Motion>', drag)
    canvas.bind('<ButtonRelease-1>', add_edge)
    canvas.tag_bind(button_play, '<Button-1>', play)
    canvas.tag_bind(button_text, '<Button-1>', play)
    gui.bind('<Delete>', undo)
    gui.bind('<Shift_L>', adjust_text_pos)
    gui.bind('<Configure>', resize_bg)

    gui.mainloop()


# <------------------------------ Gui part 2 ------------------------------>

class Vertex:

    def __init__(self, index, circle, text):
        self.index = index
        self.circle = circle
        self.text = text
        self.neighbors = []


class Edge:

    def __init__(self, line):
        self.line = line
        self.endpoints = []

    def print(self):
        if self.endpoints:
            print((self.endpoints[0].index,
                   self.endpoints[1].index))


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
    lift()


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
def lift():
    for vertex in vertexes:
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

        text = canvas.create_text(e.x + 15, e.y - 15,
                                  fill=GRAY,
                                  font='Times 13 italic bold',
                                  text=('V%d' % vertex_num))
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
def find_neighbors(vertex: Vertex) -> List[Tuple[Vertex, Edge]]:
    neighbors = []

    for edge in edges:
        pos = check_coincidence(vertex, edge)

        if pos != NOT_EDGE_ENDPOINT:
            neighbor_vertex = find_neighbor(edge, pos)
        else:
            continue

        neighbors.append((neighbor_vertex, edge))
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


# <------------------------------ Game Logic Part ------------------------------>

first_tree_vertexes = []
first_tree_edges = []

second_tree_edges = []

# To store the rest edges after finding the first spanning tree.
remaining_edges = []

# A dict which tree_subsets[k] is the set of all possible branches
# in k-th tree which can be replaced in k-th tree by a branch in
# tree_subsets[k-1].
tree_subsets = None

# For make a little bit animation by recording the last redrawn edge.
last_redrawn_edge = None

# Variable for loop of branches' replacement.
count_i = None

# Tree index.
count_k = None

# The branch which is being made replacement.
operating_edges = []

# For indicating one game is finished or not.
is_finished = False


# Using simplified Prim algorithm to generate an arbitrary spanning tree
# which is represented by tree_vertexes and tree_edges
def get_spanning_tree():
    global last_redrawn_edge, event_msj

    first_tree_vertexes.append(vertexes[0])

    if not edges:
        return

    while len(first_tree_vertexes) < len(vertexes):
        for edge in edges:
            if edge.endpoints[0] in first_tree_vertexes:
                if not edge.endpoints[1] in first_tree_vertexes:
                    first_tree_vertexes.append(edge.endpoints[1])
                    first_tree_edges.append(edge)
            else:
                if edge.endpoints[1] in first_tree_vertexes:
                    first_tree_vertexes.append(edge.endpoints[0])
                    first_tree_edges.append(edge)

    redraw_edge(first_tree_edges, BLUE)


# Redraw a given sub-graph with animation and a specific color.
def redraw_edge(edges_list: list, color: str):
    global last_redrawn_edge

    if edges_list:
        canvas.itemconfig(edges_list[0].line,
                          fill=color,
                          width=5)

        if last_redrawn_edge:
            canvas.itemconfig(last_redrawn_edge.line,
                              fill=color,
                              width=2)

        last_redrawn_edge = edges_list[0]
        gui.after(ANIMATION_DURATION,
                  (lambda: redraw_edge(edges_list[1:],
                                       color)))

    elif last_redrawn_edge is not None:
        canvas.itemconfig(last_redrawn_edge.line,
                          fill=color,
                          width=2)
        last_redrawn_edge = None


# Start game after constructing graph.
def play(e):
    global is_finished
    add_edge(e)  # Create the ultimate edge with the last created line.
    change_button_color(True)  # Animation effect.

    if not is_finished and vertex_num > 0:
        construct_graph(vertexes)
        initialize()
        is_finished = True
    else:
        clear_canvas()  # For replaying.
        is_finished = False


# For replaying the game.
def clear_canvas():
    global vertex_num, \
        is_new_edge_created, \
        first_tree_vertexes, \
        first_tree_edges, \
        second_tree_edges

    for vertex in vertexes:
        canvas.delete(vertex.circle)
        canvas.delete(vertex.text)

    for edge in edges:
        canvas.delete(edge.line)

    vertexes.clear()
    edges.clear()
    items.clear()
    first_tree_vertexes.clear()
    first_tree_edges.clear()
    second_tree_edges.clear()

    vertex_num = 0
    is_new_edge_created = False
    os.system('clear')  # Clear the console.


# Step 1
# Find an arbitrary spanning tree.
def initialize():
    print("step 1")
    global second_tree_edges, \
        remaining_edges, \
        count_i

    get_spanning_tree()

    second_tree_edges = first_tree_edges.copy()
    remaining_edges = [elem for elem in edges if
                       (elem not in first_tree_edges)]
    count_i = 1
    time_lapse = ANIMATION_DURATION * len(first_tree_edges)
    gui.after(time_lapse, lambda: insert_edge())


# Step 2
# Decrease the intersection part between the
# first tree and the second tree
def insert_edge():
    print("step 2")

    global tree_subsets, \
        operating_edges, \
        count_i, count_k

    operating_edges = {0: remaining_edges[count_i - 1]}
    tree_subsets = {-1: [], 0: {operating_edges[0]}}
    count_k = 1

    find_replaceable_edge()


# Notation: T_k means T_m where m belongs to {1, 2} and m = k (mod) 2,
# for example, T_6 <-- T_7 means T_2 <-- T_1.
def tree_index_mapping(tree_index: int) -> List[Edge]:
    if tree_index % 2 == 0:
        return second_tree_edges
    return first_tree_edges


# Step 3
def find_replaceable_edge():
    print("step 3")

    global tree_subsets, \
        operating_edges, \
        count_k

    tree_subsets[count_k] = path_union(count_k)

    if tree_subsets[count_k] == tree_subsets[count_k - 2]:
        repeat_decrement()
    else:
        replaceable_edges = [elem for elem in tree_subsets[count_k] if
                             ((elem not in tree_subsets[count_k - 2]) and
                              (elem in tree_index_mapping(count_k + 1)))]

        if len(replaceable_edges) > 0:
            operating_edges[count_k] = replaceable_edges[0]
            make_replacements()
        else:
            count_k += 1
            find_replaceable_edge()


# Unifies all sets of paths.
def path_union(tree_index: int) -> List[Edge]:
    subset = set()

    for edge in tree_subsets[tree_index - 1]:
        subset = subset.union(find_path(edge, tree_index))

    return list(subset)


# Find out the set of path of a given edge and tree index
def find_path(selected_edge: Edge, tree_index: int) -> List[Edge]:
    start_vertex = selected_edge.endpoints[0]
    end_vertex = selected_edge.endpoints[1]

    class Node:

        def __init__(self, vertex: Vertex):
            self.vertex = vertex
            self.parent = None
            self.children_tuples = []

    class Digraph:

        def __init__(self):
            self.root = Node(start_vertex)
            self.tree_edges = tree_index_mapping(tree_index)
            self.tree_copy = self.tree_edges.copy()
            self.path_edges = []
            self.queue = queue.LifoQueue()
            self.queue.put(self.root)
            self.find_path()

        def find_path(self):
            is_end_found = False
            end_node = None

            while not is_end_found:
                node = self.queue.get()

                for neighbor in node.vertex.neighbors:
                    edge = neighbor[1]

                    if edge in self.tree_copy:
                        self.tree_copy.remove(edge)
                        child = Node(neighbor[0])
                        child.parent = node
                        node.children_tuples.append((child, edge))

                        if child.vertex != end_vertex:
                            self.queue.put(child)
                        else:
                            is_end_found = True
                            end_node = child
                            break

            while end_node != self.root:
                for child_tuple in end_node.parent.children_tuples:
                    if end_node == child_tuple[0]:
                        self.path_edges.append(child_tuple[1])
                        end_node = end_node.parent
                        break

    return Digraph().path_edges


# Step 4
def make_replacements():
    print("step 4")

    global count_k, \
        tree_subsets, \
        operating_edges, \
        first_tree_edges, \
        second_tree_edges

    for edge in tree_subsets[count_k - 1]:
        if (operating_edges[count_k]
                in find_path(edge, count_k)):
            operating_edges[count_k - 1] = edge

            if tree_index_mapping(count_k) == first_tree_edges:
                first_tree_edges = list(set(
                    first_tree_edges).symmetric_difference(
                    [edge, operating_edges[count_k]]))
            else:
                second_tree_edges = list(set(
                    second_tree_edges).symmetric_difference(
                    [edge, operating_edges[count_k]]))

    count_k -= 1

    if count_k > 0:
        make_replacements()
    else:
        repeat_decrement()


# Step 5
def repeat_decrement():
    print("step 5")

    global first_tree_edges, \
        second_tree_edges, \
        last_redrawn_edge, \
        count_i, count_k, \
        event_msj

    if count_i < len(remaining_edges) and 0 < len(
            set(first_tree_edges).intersection(
                second_tree_edges)):
        count_i += 1
        insert_edge()
    else:
        gui.after(ANIMATION_DURATION, (lambda: redraw_edge(
            first_tree_edges, JADE)))

        time_lapse = ANIMATION_DURATION \
                     * (len(first_tree_edges)
                        + SEPARATION_UNIT)

        gui.after(time_lapse, (lambda: redraw_edge(
            second_tree_edges, RED)))

        time_lapse += ANIMATION_DURATION \
                      * (len(second_tree_edges)
                         + SEPARATION_UNIT)

        gui.after(time_lapse, (lambda: redraw_edge(
            list(set(first_tree_edges).intersection(
                second_tree_edges)),
            BLACK)))


if __name__ == '__main__':
    main_workflow()
