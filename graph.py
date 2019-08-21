# Keep a reference to all edges by keeping them in a list.
edges = []
vertexes = []


class Vertex:

    def __init__(self, index, circle, text):
        self.index = index
        self.circle = circle
        self.text = text
        self.neighbors = []
        self.associative_vertexes = []  # For graph thickness.
        self.associative_edges = []  # For graph thickness.


class Edge:

    def __init__(self, line):
        self.line = line
        self.endpoints = []
        self.associative_vertexes = []  # For graph thickness.
        self.associative_edges = []  # For graph thickness.

    def __eq__(self, other):
        return set(self.endpoints) == set(other.endpoints)

    def __hash__(self):
        return hash(id(self))

    def print(self):
        if self.endpoints:
            print((self.endpoints[0].index,
                   self.endpoints[1].index))
