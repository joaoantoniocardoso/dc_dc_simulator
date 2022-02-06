from . import check_state
from .State import *

import sympy as sym
import numpy as np

# GETS SYSTEM INFORMATION AND FORMS ALL STATES ACCORDING TO ALGORITHM BY THE USE OF THE FUNCTIONS INSIDE check_state
# FOR POSSIBLE STATE (STATE IS A CLASS OBJECT) FORMS MATRICES A, B, C AND D
# AFTER FORMING STATES PERFORMS TRANSITION CHECK AND INSERTS INFORMATION INSIDE STATES
# USED FOR FURTHER SIMULATION


class State_space_model:
    def __init__(self, system):
        """
        initialization of the complete system
        """
        elements = system.get_elements()
        nodes = system.get_nodes()

        self._system = system

        self._loop_nodes = []
        self._all_loops = check_state.form_loops(nodes, self._loop_nodes)
        self._cutset_nodes = check_state.form_cutset_nodes(
            nodes[1:]
        )  # important for current direction
        self._all_cutsets = check_state.form_cutsets(self._cutset_nodes)

        self._dicm_nodes = []
        self._dcvm_nodes = []
        self._dicm_cutsets = check_state.find_dicm_cutsets(
            self._all_cutsets, self._cutset_nodes, self._dicm_nodes
        )
        self._dcvm_loops = check_state.find_dcvm_loops(
            self._all_loops, self._loop_nodes, self._dcvm_nodes
        )

        self._current_cutsets = check_state.find_current_cutsets(self._all_cutsets)
        self._voltage_loops = check_state.find_voltage_loops(self._all_loops)

        self._dicm_inductors = check_state.get_dicm_inductors(self._dicm_cutsets)
        self._dcvm_capacitors = check_state.get_dcvm_capacitors(self._dcvm_loops)

        self._beginning_state = None

    def form_states(self):
        """
        forms list of possible states of switches and performs all checks for the possibility of state
        """
        self._state_indexes = []

        for i in range(2 ** self._system.get_number_switches()):
            if (
                check_state.check_control_scheme(
                    self._system.get_controlled_switches(),
                    self._system.get_on_state_switches(),
                    self._system.get_off_state_switches(),
                    i,
                )
                and not (
                    check_state.check_voltage_loops(i, self._voltage_loops)
                    or check_state.check_current_cutsets(i, self._current_cutsets)
                )
                and check_state.check_dicm_cutset(self._dicm_cutsets, i)
            ):
                self._state_indexes.append(i)

    def form_state_lists(self):
        """
        for possible states forms objects and puts matrices and transition information inside
        """
        self._states = []
        independent_sources = np.array(self._system.get_source_values())
        for state in self._state_indexes:
            self.form_state(state)
        self.form_transitions()

        for state in self._states:
            state.define_control_value(independent_sources)

    def form_state(self, state_index):
        state = State(state_index)

        # adding control type
        dicm = check_state.is_dicm(state_index, self._dicm_nodes, self._dicm_cutsets)
        dcvm = check_state.is_dcvm(state_index, self._dcvm_nodes, self._dcvm_loops)

        # adding matrices
        state_variables = (
            self._system.get_number_state_variables()
        )  # number of state variables
        state_variables_position = self._system.get_state_variables_position()
        independent_sources = self._system.get_number_independent_sources()
        number_outputs = self._system.get_number_outputs()
        output_indexes = self._system.get_output_indexes()
        number_equations = self._system.get_number_equations()

        state_variables_symbols = self._system.get_state_variables_symbols()
        independent_sources_symbols = self._system.get_source_symbols()

        matrix_A = [
            [0 for dummy_i in range(state_variables)]
            for dummy_j in range(state_variables)
        ]
        matrix_B = [
            [0 for dummy_i in range(independent_sources)]
            for dummy_j in range(state_variables)
        ]
        matrix_C = [
            [0 for dummy_i in range(state_variables)]
            for dummy_j in range(number_outputs)
        ]
        matrix_D = [
            [0 for dummy_i in range(independent_sources)]
            for dummy_j in range(number_outputs)
        ]

        matrix = sym.Matrix(
            [
                [0 for dummy_i in range(number_equations + 1)]
                for dummy_j in range(number_equations)
            ]
        )

        # if DICM occurs, add an extra equation and set change of symbol inside one inductor
        if dicm[0] or dicm[1]:
            if dicm[0]:
                voltage_sources = self._system.get_number_voltage_sources()
                for element in dicm[3]:
                    for index in range(len(element)):
                        element[index] = sign(element[index]) * (
                            abs(element[index]) + voltage_sources
                        )
                    state.add_control(["dicm", dicm[2], dicm[3]])

            for line in dicm[2]:
                self._system.set_dicm(abs(line[0]), line)
                if len(line) > 1:
                    new_row = Matrix([[0 for dummy in range(number_equations + 1)]])
                    for element in line:
                        new_row[
                            0,
                            self._system.get_inductors()[
                                abs(element) - 1
                            ].get_position(),
                        ] = sign(element)
                    matrix = matrix.col_join(new_row)

        # if DCVM occurs, set the change of symbol inside one capacitor
        if dcvm[0] or dcvm[1]:
            for line in dcvm[2]:
                self._system.set_dcvm(abs(line[0]), line)
            if dcvm[0]:
                inductors = self._system.get_number_inductors()

                for element in dcvm[
                    2
                ]:  # modify index of capacitor to have proper index inside state variables
                    for index in range(len(element)):
                        element[index] = sign(element[index]) * (
                            abs(element[index]) + inductors
                        )
                state.add_control(["dcvm", dcvm[2], dcvm[3]])

        for element in self._system.get_elements():
            #            element.write_matrix_symbolic(matrix, number_equations, state_index)
            element.write_matrix_valued(matrix, number_equations, state_index)

        matrix = sym.simplify(matrix.rref())
        for i in matrix[1]:
            if (i >= state_variables_position) and (
                i < (state_variables_position + state_variables)
            ):
                index = i - state_variables_position

                for dummy_i in range(state_variables):
                    matrix_A[index][dummy_i] = matrix[0][
                        matrix[1].index(i), number_equations
                    ].subs(state_variables_symbols[dummy_i], 1)

                    for dummy_j in range(state_variables):
                        matrix_A[index][dummy_i] = matrix_A[index][dummy_i].subs(
                            state_variables_symbols[dummy_j], 0
                        )
                    for dummy_j in range(independent_sources):
                        matrix_A[index][dummy_i] = matrix_A[index][dummy_i].subs(
                            independent_sources_symbols[dummy_j], 0
                        )

                for dummy_i in range(independent_sources):
                    matrix_B[index][dummy_i] = matrix[0][
                        matrix[1].index(i), number_equations
                    ].subs(independent_sources_symbols[dummy_i], 1)
                    for dummy_j in range(independent_sources):
                        matrix_B[index][dummy_i] = matrix_B[index][dummy_i].subs(
                            independent_sources_symbols[dummy_j], 0
                        )
                    for dummy_j in range(state_variables):
                        matrix_B[index][dummy_i] = matrix_B[index][dummy_i].subs(
                            state_variables_symbols[dummy_j], 0
                        )

            if i in output_indexes:
                index = output_indexes.index(i)

                for dummy_i in range(state_variables):
                    matrix_C[index][dummy_i] = matrix[0][
                        matrix[1].index(i), number_equations
                    ].subs(state_variables_symbols[dummy_i], 1)

                    for dummy_j in range(state_variables):
                        matrix_C[index][dummy_i] = matrix_C[index][dummy_i].subs(
                            state_variables_symbols[dummy_j], 0
                        )
                    for dummy_j in range(independent_sources):
                        matrix_C[index][dummy_i] = matrix_C[index][dummy_i].subs(
                            independent_sources_symbols[dummy_j], 0
                        )

                for dummy_i in range(independent_sources):
                    matrix_D[index][dummy_i] = matrix[0][
                        matrix[1].index(i), number_equations
                    ].subs(independent_sources_symbols[dummy_i], 1)
                    for dummy_j in range(independent_sources):
                        matrix_D[index][dummy_i] = matrix_D[index][dummy_i].subs(
                            independent_sources_symbols[dummy_j], 0
                        )
                    for dummy_j in range(state_variables):
                        matrix_D[index][dummy_i] = matrix_D[index][dummy_i].subs(
                            state_variables_symbols[dummy_j], 0
                        )

        state.add_matrices(
            matrix_A,
            matrix_B,
            matrix_C,
            matrix_D,
        )

        state.add_independent_sources(self._system.get_independent_sources())

        self._states.append(state)

    def find_state(self, code):
        """
        finds state with given state of the switches
        """
        for state in self._states:
            if state.get_index() == code:
                return state
        return None

    def print_states(self):
        """
        print states
        """
        for state in self._states:
            print(str(state))

    def get_states(self):
        """
        get states
        """
        return self._states

    def get_beginning_state(self):
        return self._beginning_state

    def get_state_number(self):
        return len(self._states)

    def form_transitions(self):
        """
        form transitions
        """
        if check_state.is_Qn_PWM(
            self._all_loops,
            self._all_cutsets,
            self._dcvm_capacitors,
            self._dicm_inductors,
            self._system.get_controlled_switches(),
        ):
            for state in self._states:
                if state.get_index() == 0:
                    state.add_next_state(self.find_01_state())
                elif state.get_index() == 1:
                    state.add_control(["control", None])
                    state.add_control(["dcvmoff", None])
                    state.add_next_state(self.find_state(2))
                    state.add_next_state(self.find_state(3))
                    self._beginning_state = state
                elif state.get_index() == 2:
                    state.add_control(["control", None])
                    state.add_next_state(self.find_state(3))
                    state.add_next_state(self.find_state(1))
                    state.add_next_state(self.find_state(0))
                elif state.get_index() == 3:
                    state.add_control(["control", None])
                    state.add_next_state(self.find_state(2))
                    state.add_next_state(self.find_state(1))
                print(
                    "This is quasi-resonant converter of type Qn-PWM and possible transitions are:"
                )
                print("01 -> 10")
                print("01 -> 10 -> 00")
                print("01 -> 11")
                print("01 -> 11 -> 10")
                print("01 -> 11 -> 10 -> 00")

        elif check_state.is_Qf_PWM(
            self._all_loops,
            self._all_cutsets,
            self._dcvm_capacitors,
            self._dicm_inductors,
            self._system.get_controlled_switches(),
        ):
            pass

        elif check_state.is_ZV_QSW(
            self._all_loops,
            self._dcvm_capacitors,
            self._system.get_on_state_switches(),
        ):
            controlled = bin(
                self._system.get_on_state_switches()
                | self._system.get_off_state_switches()
            ).count("1")
            print(
                "This is quasi-resonant converter of type ZV-QSW and possible transitions are:"
            )
            print("01 -> 00")
            print("01 -> 00 -> 10 -> 00")

            for state in self._states:
                if state.get_index() == 0:
                    state.add_control(["control", None])
                    state.add_next_state(self.find_state(1))
                    state.add_next_state(self.find_state(2))
                elif state.get_index() == 1:
                    state.add_control(["control", None])
                    state.add_next_state(self.find_state(0))
                    if controlled == 2:
                        self.find_state(2).add_control(["control", None])
                        state.add_next_state(self.find_state(2))
                        print("01 -> 10")
                    else:
                        self.find_state(0).add_off_control(
                            self.find_state(2).get_control()
                        )
                        self._beginning_state = state
                elif state.get_index() == 2:
                    state.add_next_state(self.find_state(0))
                    state.add_next_state(self.find_state(1))

        elif check_state.is_ZC_QSW(
            self._all_cutsets,
            self._dicm_inductors,
            self._system.get_controlled_switches(),
        ):
            pass

        elif check_state.is_ZV(
            self._all_loops,
            self._all_cutsets,
            self._system.get_controlled_switches(),
        ):
            controlled = bin(
                self._system.get_on_state_switches()
                | self._system.get_off_state_switches()
            ).count("1")
            print("This is quasi resonant ZV and possible transitions are:")
            if controlled == 1:
                print("11 -> 10")
                print("11 -> 01 -> 00 -> 10")
                for state in self._states:
                    if state.get_index() == 0:
                        state.add_next_state(self.find_state(2))
                        state.add_control(["control", None])
                    elif state.get_index() == 1:
                        state.add_next_state(self.find_state(0))
                    elif state.get_index() == 2:
                        state.add_next_state(self.find_state(3))
                        state.add_control(["control", None])
                    else:
                        state.add_control(["control", None])
                        state.add_next_state(self.find_state(1))
                        state.add_next_state(self.find_state(2))
                        self._beginning_state = state

        elif check_state.is_ZC(
            self._all_loops,
            self._all_cutsets,
            self._system.get_controlled_switches(),
        ):
            pass

        else:
            print("This is PWM converter with possible transitions:")
            print("01 -> 10")
            for state in self._states:
                if state.get_index() == 0:
                    state.add_next_state(self.find_state(1))
                    self.find_state(2).add_next_state(state)
                    print("01 -> 10 -> 00")
                elif state.get_index() == 1:
                    state.add_next_state(self.find_state(2))
                    state.add_control(["control", None])
                    self._beginning_state = state
                elif state.get_index() == 2:
                    state.add_next_state(self.find_state(1))
                    state.add_control(["control", None])
                else:
                    self.find_state(1).add_next_state(state)
                    state.add_next_state(self.find_state(2))
                    print("01 -> 11 -> 10")

    ##############################################################################################################################################
    # CCM operation

    def steady_state(self, duty_ratio, marker="CCM"):
        """
        steady state for switching circuit
        """
        independent_sources = self._system.get_independent_sources()
        if marker == "CCM":
            (A1, B1, C1, D1) = self.find_state(1).get_matrices()
            (A2, B2, C2, D2) = self.find_state(2).get_matrices()
            A = A1 * duty_ratio[0] + A2 * (1 - duty_ratio[0])
            B = B1 * duty_ratio[0] + B2 * (1 - duty_ratio[0])
        elif marker == "DICM":
            (A1, B1, C1, D1) = self.find_state(1).get_matrices()
            (A2, B2, C2, D2) = self.find_state(2).get_matrices()
            (A3, B3, C3, D3) = self.find_state(0).get_matrices()
            A = (
                A1 * duty_ratio[0]
                + A2 * duty_ratio[-1]
                + A3 * (1 - duty_ratio[0] - duty_ratio[-1])
            )
            B = (
                B1 * duty_ratio[0]
                + B2 * duty_ratio[-1]
                + B3 * (1 - duty_ratio[0] - duty_ratio[-1])
            )
        else:
            (A1, B1, C1, D1) = self.find_state(1).get_matrices()
            (A2, B2, C2, D2) = self.find_state(2).get_matrices()
            (A3, B3, C3, D3) = self.find_state(3).get_matrices()
            A = (
                A1 * duty_ratio[0]
                + A3 * duty_ratio[1]
                + A2 * (1 - duty_ratio[0] - duty_ratio[1])
            )
            B = (
                B1 * duty_ratio[0]
                + B3 * duty_ratio[1]
                + B2 * (1 - duty_ratio[0] - duty_ratio[1])
            )

        x = -np.matmul(np.linalg.pinv(A), np.matmul(B, independent_sources))
        return x

    def delta_steady_state(self, duty_ratio, period, equilibrium, marker="CCM"):
        """
        rippler in steady state for switching circuit
        """
        independent_sources = self._system.get_independent_sources()
        if marker == "CCM":
            (A, B, C, D) = self._beginning_state.get_matrices()
            delta = (
                (np.matmul(A, equilibrium) + np.matmul(B, independent_sources))
                * duty_ratio[0]
                * period
                * 0.5
            )
        else:
            # to be written
            delta = 0
        return delta
