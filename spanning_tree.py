import os
import queue
from gui import *
import gui as g


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


# Using simplified Prim algorithm to generate an arbitrary spanning tree
# which is represented by tree_vertexes and tree_edges
def get_spanning_tree():
    global last_redrawn_edge

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


# For replaying the game.
def clear_canvas():
    global is_new_edge_created, \
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

    g.vertex_num = 0
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
        count_i, count_k

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
