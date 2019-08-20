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

first_circuit = []
second_circuit = []


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


def create_vertex(pos_x, pos_y):
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


def get_angle(vec1, vec2):
    dot = vec1[0] * vec2[0] + vec1[1] * vec2[1]
    det = vec1[0] * vec2[1] - vec1[1] * vec2[0]

    if det < 0:
        return 2 * math.pi + math.atan2(det, dot)
    else:
        return math.atan2(det, dot)


def get_another_endpoint(edge, vertex) -> Vertex:
    return edge.endpoints[0] if vertex != edge.endpoints[0] \
        else edge.endpoints[1]


def draw_vertex_edges(vertexes_list):
    for i, vertex in enumerate(vertexes_list):
        thickening_edges.append(create_edge(
            vertex, vertexes_list[(i + 1) % len(vertexes_list)]))


def draw_edge_edges(vertexes_list, edge):
    for vertex1 in vertexes_list:
        for vertex2 in vertexes_list:
            if vertex1 != vertex2:
                if is_insulated(vertex1, vertex2, edge) and \
                        not is_intersected(vertex1, vertex2, edge):
                    thickening_edges.append(create_edge(vertex1, vertex2))


def is_insulated(vertex1, vertex2, edge):
    vertexes_list1 = edge.endpoints[0].associative_vertexes
    vertexes_list2 = edge.endpoints[1].associative_vertexes

    if vertex1 in vertexes_list1 and vertex2 in vertexes_list1:
        return False

    if vertex1 in vertexes_list2 and vertex2 in vertexes_list2:
        return False

    return True


def is_intersected(vertex1, vertex2, edge):
    line1 = LineString([get_coord(vertex1), get_coord(vertex2)])
    line2 = LineString([get_coord(edge.endpoints[0]),
                        get_coord(edge.endpoints[1])])

    return line1.intersects(line2)


def create_edge(vertex1, vertex2):
    coord1 = get_coord(vertex1)
    coord2 = get_coord(vertex2)

    return canvas.create_line(coord1[0], coord1[1],
                              coord2[0], coord2[1],
                              fill=DARK_GRAY)


def get_coord(vertex):
    coord = canvas.coords(vertex.circle)

    return (coord[0] + coord[2]) / 2, (coord[1] + coord[3]) / 2


def graph_thickening():
    create_vertexes()

    for vertex in vertexes:
        draw_vertex_edges(vertex.associative_vertexes)

    for edge in edges:
        draw_edge_edges(edge.associative_vertexes, edge)

    lift(thickening_vertexes)


def generate_hamiltonian_circuits():
    graph_thickening()
