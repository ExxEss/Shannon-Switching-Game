import spanning_tree as st
from typing import List, Tuple

vertexes = []
edges = []

thickening_radius = 10
translation_distance = 200

first_circuit = []
second_circuit = []


def redraw_graph(vertexes_list: List[st.Vertex]):
    return


def create_vertexes():
    for vertex in st.vertexes:

        for neighbor in vertex.neighbors:
            create_vertex(find_position(neighbor[1], find_next_edge(vertex.neighbors, neighbor[1])))


def create_vertex(position):
    return


def find_position(edge1: st.Edge, edge2: st.Edge) -> (float, float):
    return


def find_next_edge(neighbors: List[(st.Vertex, st.Edge)], edge) -> st.Edge:
    return


def create_edges(edge: st.Edge):
    return


def graph_thickening():
    for vertex in st.vertexes:
        create_vertexes()

    for edge in st.edges:
        create_edges(edge)

    st.construct_graph(vertexes)


def generate_hamiltonian_circuits():
    return


if __name__ == '__main__':
    st.gui.title('Hamiltonian Circuits')
    st.main_workflow()
    redraw_graph(st.vertexes)
    generate_hamiltonian_circuits()
    st.redraw_edge(first_circuit, st.JADE)
    st.redraw_edge(second_circuit, st.RED)
