from spanning_tree import *
import spanning_tree as st
from typing import List
from shapely.geometry import LineString
import math

to_exclude = ['create_vertex']

for name in to_exclude:
    del globals()[name]

THICKENING_RADIUS = 40
TRANSLATION_DISTANCE = 200
UNIT_VECTOR = (1, 0)

thickening_vertexes = []
thickening_edges = []

first_circuit = set()
second_circuit = set()


def create_vertexes():
    reorder_neighbors()

    for vertex in vertexes:
        coord1 = canvas.coords(vertex.circle)

        x1 = (coord1[0] + coord1[2]) / 2
        y1 = (coord1[1] + coord1[3]) / 2

        for i, neighbor in enumerate(vertex.neighbors):
            if i < len(vertex.neighbors) - 1:
                next_neighbor = vertex.neighbors[i + 1]
                angle = (neighbor[2] + next_neighbor[2]) / 2
            else:
                next_neighbor = vertex.neighbors[0]
                angle = (neighbor[2] + next_neighbor[2] - 2 * math.pi) / 2

                if angle < 0:
                    angle += 2 * math.pi

            new_vertex = create_vertex(x1 + THICKENING_RADIUS * math.cos(angle),
                                       y1 - THICKENING_RADIUS * math.sin(angle))

            vertex.associative_vertexes.append(new_vertex)
            neighbor[1].associative_vertexes.append(new_vertex)
            next_neighbor[1].associative_vertexes.append(new_vertex)
            thickening_vertexes.append(new_vertex)
            st.vertex_num += 1


def create_vertex(pos_x: int, pos_y: int) -> Vertex:
    circle = canvas.create_oval(pos_x - VERTEX_RADIUS,
                                pos_y - VERTEX_RADIUS,
                                pos_x + VERTEX_RADIUS,
                                pos_y + VERTEX_RADIUS,
                                fill=BLUE,
                                outline=GRAY,
                                width=2)

    text = canvas.create_text(pos_x, pos_y,
                              fill=GRAY,
                              font='Times 8 italic bold',
                              text=('%d' % st.vertex_num))

    return Vertex(st.vertex_num, circle, text)


def reorder_neighbors():
    for vertex in vertexes:
        coord1 = canvas.coords(vertex.circle)

        x1 = (coord1[0] + coord1[2]) / 2
        y1 = (coord1[1] + coord1[3]) / 2

        for neighbor in vertex.neighbors:
            edge_endpoint = get_another_endpoint(neighbor[1], vertex)
            coord2 = canvas.coords(edge_endpoint.circle)

            x2 = (coord2[0] + coord2[2]) / 2
            y2 = (coord2[1] + coord2[3]) / 2

            neighbor.append(get_angle((x2 - x1, y2 - y1), UNIT_VECTOR))

        vertex.neighbors = sorted(vertex.neighbors, key=lambda k: k[2])


def get_angle(vec1: (int, int), vec2: (int, int)) -> float:
    dot = vec1[0] * vec2[0] + vec1[1] * vec2[1]
    det = vec1[0] * vec2[1] - vec1[1] * vec2[0]

    if det < 0:
        return 2 * math.pi + math.atan2(det, dot)
    else:
        return math.atan2(det, dot)


def get_another_endpoint(edge: Edge, vertex: Vertex) -> Vertex:
    return edge.endpoints[0] if vertex != edge.endpoints[0] \
        else edge.endpoints[1]


def create_vertex_edges(vertexes_list: List[Vertex], vertex: Vertex):
    for i, vertex1 in enumerate(vertexes_list):
        new_edge = create_edge(
            vertex1, vertexes_list[(i + 1) % len(vertexes_list)])

        thickening_edges.append(new_edge)
        vertex.associative_edges.append(new_edge)


def create_edge_edges(vertexes_list: List[Vertex], edge: Edge):
    for vertex1 in vertexes_list:
        for vertex2 in vertexes_list:
            if vertex1 != vertex2:
                created_edge = find_created_edge(vertex1, vertex2, edge)

                if type(created_edge) != Edge:
                    if not is_intersected(vertex1, vertex2, edge):
                        new_edge = create_edge(vertex1, vertex2)
                        thickening_edges.append(new_edge)
                        edge.associative_edges.append(new_edge)
                else:
                    edge.associative_edges.append(created_edge)


def find_created_edge(vertex1: Vertex, vertex2: Vertex, edge: Edge):
    def find_edge(edges_list):
        for _edge in edges_list:
            if vertex1 in _edge.endpoints \
                    and vertex2 in _edge.endpoints:
                return _edge

    endpoint1 = edge.endpoints[0]
    endpoint2 = edge.endpoints[1]

    vertexes_list1 = endpoint1.associative_vertexes
    vertexes_list2 = endpoint2.associative_vertexes

    edges_list1 = endpoint1.associative_edges
    edges_list2 = endpoint2.associative_edges

    if vertex1 in vertexes_list1 and vertex2 in vertexes_list1:
        return find_edge(edges_list1)

    if vertex1 in vertexes_list2 and vertex2 in vertexes_list2:
        return find_edge(edges_list2)


def is_intersected(vertex1: Vertex, vertex2: Vertex, edge: Edge) -> bool:
    line1 = LineString([get_coord(vertex1), get_coord(vertex2)])
    line2 = LineString([get_coord(edge.endpoints[0]),
                        get_coord(edge.endpoints[1])])

    return line1.intersects(line2)


def create_edge(vertex1: Vertex, vertex2: Vertex) -> tk.BASELINE:
    coord1 = get_coord(vertex1)
    coord2 = get_coord(vertex2)

    new_edge = Edge(canvas.create_line(coord1[0], coord1[1],
                                       coord2[0], coord2[1],
                                       fill=DARK_GRAY))
    new_edge.endpoints = [vertex1, vertex2]

    return new_edge


def get_coord(vertex: Vertex) -> (int, int):
    coord = canvas.coords(vertex.circle)

    return (coord[0] + coord[2]) / 2, (coord[1] + coord[3]) / 2


def graph_thickening():
    create_vertexes()

    for vertex in vertexes:
        create_vertex_edges(vertex.associative_vertexes, vertex)

    for edge in edges:
        create_edge_edges(edge.associative_vertexes, edge)

    lift(thickening_vertexes)


def hamiltonian_circuits():
    global first_circuit, second_circuit

    graph_thickening()

    for vertex in vertexes:
        first_circuit = first_circuit. \
            symmetric_difference(
                vertex.associative_edges)

        second_circuit = second_circuit. \
            symmetric_difference(
                vertex.associative_edges)

    for edge in st.first_tree_edges:
        first_circuit = first_circuit. \
            symmetric_difference(
                edge.associative_edges)

    for edge in st.second_tree_edges:
        second_circuit = second_circuit. \
            symmetric_difference(
                edge.associative_edges)

    _redraw_edge(first_circuit, BLUE)
    _redraw_edge(second_circuit, YELLOW)
    _redraw_edge(first_circuit.intersection(
        second_circuit), BLACK)


def _redraw_edge(_edges: set, color: str):
    for edge in _edges:
        canvas.itemconfig(edge.line, fill=color)
