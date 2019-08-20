from spanning_tree import *
import hamiltonian_circuits as hc

is_finished = False


# Start game after constructing graph.
def play(e):
    global is_finished
    add_edge(e)  # Create the ultimate edge with the last created line.
    change_button_color(True)  # Animation effect.

    if not is_finished and g.vertex_num > 0:
        construct_graph(vertexes)
        initialize()
        is_finished = True
        canvas.after(3 * ANIMATION_DURATION * (len(vertexes) + 1),
                     (lambda: hc.hamiltonian_circuits()))
    else:
        clear_canvas()  # For replaying.
        is_finished = False


def bind():
    canvas.bind('<Button-1>', click)
    canvas.bind('<Double-1>', create_vertex)
    canvas.bind('<B1-Motion>', drag)
    canvas.bind('<ButtonRelease-1>', add_edge)
    canvas.tag_bind(button_play, '<Button-1>', play)
    canvas.tag_bind(button_text, '<Button-1>', play)
    gui.bind('<Delete>', undo)
    gui.bind('<Shift_L>', adjust_text_pos)
    gui.bind('<Configure>', resize_bg)


if __name__ == '__main__':
    gui.title('Hamiltonian Circuits')
    bind()
    gui.mainloop()

    # redraw_edge(first_circuit, JADE)
    # redraw_edge(second_circuit, RED)
