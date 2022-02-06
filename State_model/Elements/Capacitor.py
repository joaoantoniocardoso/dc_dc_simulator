from .Element import *


class Capacitor(Element):
    """
    capacitor class
    """

    def __init__(self, index, node1, node2, value, initial=0):
        self._dcvm = False
        self._dcvm_symbol = 0
        self._initial_value = initial

        self._symbol = sym.sympify("C" + str(index))
        Element.__init__(self, index, node1, node2, value)

    def _write_matrix(self, A, number_equations, index, value):
        if not self._dcvm:
            s = sym.sympify("vc" + str(self._index))
            A[self._position + self._index - 1, number_equations] = s

            if self._node1:
                A[self._node1 - 1, self._position + self._index - 1] = value
                A[self._position + self._index - 1, self._node1 - 1] = 1
            if self._node2:
                A[self._node2 - 1, self._position + self._index - 1] = -value
                A[self._position + self._index - 1, self._node2 - 1] = -1

        else:
            if self._dcvm_symbol == 0:
                A[
                    self._position + self._index - 1, self._position + self._index - 1
                ] = 1
            else:
                A[
                    self._position + self._index - 1, number_equations
                ] = self._dcvm_symbol
                if self._node1:
                    A[self._node1 - 1, self._position + self._index - 1] = value
                    A[self._position + self._index - 1, self._node1 - 1] = 1
                if self._node2:
                    A[self._node2 - 1, self._position + self._index - 1] = -value
                    A[self._position + self._index - 1, self._node2 - 1] = -1

            self._dcvm = False
            self._dcvm_symbol = 0

    def set_dcvm(self, elements_list):
        self._dcvm = True
        if len(elements_list):
            for element in elements_list[1:]:
                self._dcvm_symbol += (
                    SX.sym("vc" + str(abs(element)))
                    * sign(element)
                    * sign(elements_list[0])
                )

    def get_initial_value(self):
        return self._initial_value
