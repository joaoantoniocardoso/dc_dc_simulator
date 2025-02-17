from .Element import *


class Inductor(Element):
    """
    inductor class
    """

    def __init__(self, index, node1, node2, value, initial=0):
        self._dicm = False
        self._dicm_symbol = 0
        self._symbol = sym.sympify("L" + str(index))
        Element.__init__(self, index, node1, node2, value)
        self._initial_value = initial

    def _write_matrix(self, A, number_equations, index, value):
        if not self._dicm:
            s = sym.sympify("il" + str(self._index))
            A[self._position + self._index - 1, self._position + self._index - 1] = 1
            if self._node1:
                A[self._position + self._index - 1, self._node1 - 1] = -1 / value
                A[self._node1 - 1, number_equations] -= s
            if self._node2:
                A[self._node2 - 1, number_equations] += s
                A[self._position + self._index - 1, self._node2 - 1] = 1 / value
        else:
            if self._dicm_symbol != 0:
                A[
                    self._position + self._index - 1, self._position + self._index - 1
                ] = 1
            if self._node1:
                A[self._node1 - 1, number_equations] -= self._dicm_symbol
                A[self._position + self._index - 1, self._node1 - 1] = -1 / value
            if self._node2:
                A[self._node2 - 1, number_equations] += self._dicm_symbol
                A[self._position + self._index - 1, self._node2 - 1] = 1 / value
            self._dicm = False
            self._dicm_symbol = 0

    def set_dicm(self, elements_list):
        if len(elements_list):
            for element in elements_list[1:]:
                self._dicm_symbol -= (
                    sym.sympify("il" + str(abs(element)))
                    * sign(element)
                    * sign(elements_list[0])
                )

        self._dicm = True

    def get_initial_value(self):
        return self._initial_value
