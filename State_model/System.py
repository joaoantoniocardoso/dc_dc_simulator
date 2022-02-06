# SINGLETON: CLASS THAT CONTAINS ALL INFORMATION ABOUT ELEMENTS AND NODES
# I.E. NUMBER OF NODES, INDUCTORS, CAPACITORS, ...
# USED FOR COLLECTING THESE INFORMATION AND GETTING THEM WHEN NECCESSARY

from .Elements import *
from .Nodes import *
from .Output import *


class System:
    def __init__(self):
        self._number_voltage_sources = 0
        self._number_current_sources = 0
        self._number_switches = 0
        self._number_inductors = 0
        self._number_capacitors = 0
        self._number_resistors = 0
        self._number_independent_sources = 0

        self._state_variables = 0
        self._independent_sources = 0

        self._number_elements = 0
        self._number_nodes = 0

        self._total_number_equations = 0

        self._elements = []
        self._symbols_bank = []
        self._nodes = []
        self._switches = []

        # saves pattern for switches control
        self._controlled_switches = 0
        self._controlled_switches_on_state = 0
        self._controlled_switches_off_state = 0

        # initialization block
        self._inductors = []
        self._capacitors = []
        self._initial_values = []
        self._state_variables_symbols = []

        # sources
        self._sources_symbols = []
        self._independent_sources = []
        self._sources_values = []

    def __enter__(self):
        return self

    def __exit__(self, type, value, tb):
        pass

    #####################################################################################################################################
    # get information
    def get_number_switches(self):
        return self._number_switches

    def get_number_inductors(self):
        return self._number_inductors

    def get_number_capacitors(self):
        return self._number_capacitors

    def get_number_voltage_sources(self):
        return self._number_voltage_sources

    def get_number_current_sources(self):
        return self._number_current_sources

    def get_number_resistors(self):
        return self._number_resistors

    def get_number_equations(self):
        return self._total_number_equations

    def get_inductors(self):
        return self._inductors

    def get_capacitors(self):
        return self._capacitors

    ### switches information
    def get_on_state_switches(self):
        return self._controlled_switches_on_state

    def get_off_state_switches(self):
        return self._controlled_switches_off_state

    def get_controlled_switches(self):
        return self._controlled_switches

    def get_switches(self):
        return self._switches

    def get_switches_indexes(self):
        return [switch.get_index() for switch in self._switches]

    def get_controlled_switches_indexes(self):
        return [
            switch.get_index() for switch in self._switches if switch.control_type()
        ]

    ### information about state variables
    def get_number_state_variables(self):
        return self._state_variables

    def get_state_variables_position(self):
        return (
            self._number_nodes
            + self._number_voltage_sources
            + self._number_switches
            - 1
        )

    def get_state_variables_symbols(self):
        return self._state_variables_symbols

    def get_initial_values(self):
        return self._initial_values

    ### independent sources
    def get_number_independent_sources(self):
        return self._number_independent_sources

    def get_source_symbols(self):
        return self._sources_symbols

    def get_source_values(self):
        return self._sources_values

    def get_independent_sources(self):
        return self._independent_sources

    ### output
    def get_number_outputs(self):
        return self._output.get_number()

    def get_output_indexes(self):
        return self._output.get_indexes()

    def set_output(self, output_list):
        """
        setting the output
        """
        self._output = Output()
        self._output_list = output_list

    ### set control of the controllable switches
    def set_control(self, control_switches_state, state):
        if state == "on_state":
            self._controlled_switches_on_state = control_switches_state
        else:
            self._controlled_switches_off_state = control_switches_state

        self._controlled_switches = (
            self._controlled_switches | control_switches_state
        )  # all controlled switches

    ### adds all elements and writes them
    def create_element(self, constructor):
        element = constructor
        self.add_element(element)
        self.add_symbol(element.get_symbol())

        for node in element.get_nodes():
            self.add_node(node, element)

    def add_element(self, element):
        self._elements.append(element)
        self._number_elements += 1

        if element.__class__ == Voltage_source:
            self._number_voltage_sources += 1
        elif element.__class__ == Inductor:
            self._number_inductors += 1
        elif element.__class__ == Capacitor:
            self._number_capacitors += 1
        elif element.__class__ == Switch:
            self._number_switches += 1
        elif element.__class__ == Current_source:
            self._number_current_sources += 1
        elif element.__class__ == Resistor:
            self._number_resistors += 1

    def get_elements(self):
        return self._elements

    def get_number_elements(self):
        return self._number_elements

    def write_elements(self):
        for element in self._elements:
            print(str(element))

    ### adds all of the symbols and writes them
    def write_symbols(self):
        print(self._symbols_bank)

    def add_symbol(self, symb):
        self._symbols_bank.append(symb)

    ### adds all circuit nodes and writes them
    def write_nodes(self):
        for node in self._nodes:
            print(str(node))

    def get_nodes(self):
        return self._nodes

    def get_number_nodes(self):
        return self._number_nodes

    def add_node(self, node_index, element):
        """
        adds node if does not exist and in the other case just adds element to node
        """
        global number_nodes

        dummy = True
        for node in self._nodes:
            dummy = dummy and (node.index() != node_index)

        if dummy:
            self._nodes.append(Node(node_index))
            self._number_nodes += 1

            for i in range(len(self._nodes) - 1):
                if self._nodes[i].index() > self._nodes[i + 1].index():
                    dummy = self._nodes[i]
                    self._nodes[i] = self._nodes[i + 1]
                    self._nodes[i + 1] = dummy

        for node in self._nodes:
            if node.index() == node_index:
                node.add_element(element)
                break

    ### calculates equations and writes indexes inside elements
    def initialize(self):
        # state variables
        self._state_variables = self._number_inductors + self._number_capacitors
        self._inductors = [0 for _dummy in range(self._number_inductors)]
        self._capacitors = [0 for _dummy in range(self._number_capacitors)]
        self._initial_values = [0 for _dummy in range(self._state_variables)]
        self._state_variables_symbols = [0 for _dummy in range(self._state_variables)]

        # sources
        self._number_independent_sources = (
            self._number_voltage_sources + self._number_current_sources
        )
        self._sources_symbols = [
            0 for _dummy in range(self._number_independent_sources)
        ]
        self._independent_sources = [
            0 for _dummy in range(self._number_independent_sources)
        ]
        self._sources_values = [0 for _dummy in range(self._number_independent_sources)]

        self._total_number_equations = (
            self._number_nodes
            + self._number_inductors
            + self._number_capacitors
            + self._number_voltage_sources
            + self._number_switches
            - 1
        )

        # sets elements position and gets important symbols
        for element in self._elements:
            if isinstance(element, Voltage_source):
                element.set_position(self._number_nodes - 1)
                self._sources_symbols[element.get_index() - 1] = sym.sympify(
                    "V" + str(element.get_index())
                )
                self._sources_values[element.get_index() - 1] = element.get_value()
                self._independent_sources[element.get_index() - 1] = element.get_value()
            elif isinstance(element, Inductor):
                element.set_position(
                    self._number_nodes
                    + self._number_voltage_sources
                    + self._number_switches
                    - 1
                )
                self._inductors[element.get_index() - 1] = element
                self._state_variables_symbols[element.get_index() - 1] = sym.sympify(
                    "il" + str(element.get_index())
                )
                self._initial_values[
                    element.get_index() - 1
                ] = element.get_initial_value()
            elif isinstance(element, Capacitor):
                element.set_position(
                    self._number_nodes
                    + self._number_inductors
                    + self._number_voltage_sources
                    + self._number_switches
                    - 1
                )
                self._state_variables_symbols[
                    self._number_inductors + element.get_index() - 1
                ] = sym.sympify("vc" + str(element.get_index()))
                self._initial_values[
                    self._number_inductors + element.get_index() - 1
                ] = element.get_initial_value()
                self._capacitors[element.get_index() - 1] = element
            elif isinstance(element, Switch):
                element.set_position(
                    self._number_nodes + self._number_voltage_sources - 1
                )
                self._switches.append(element)
            elif isinstance(element, Current_source):
                self._sources_symbols[
                    self._number_voltage_sources + element.get_index() - 1
                ] = sym.sympify("I" + str(element.get_index()))
                self._sources_values[element.get_index() - 1] = element.get_value()
                self._independent_sources[
                    self._number_voltage_sources + element.get_index() - 1
                ] = element.get_value()

    def initialise_output(self):
        """
        sets output indexes
        """
        for lst in self._output_list:
            if lst[0] == "node":
                self._output.add_index(lst[1] - 1)
            elif lst[0] == "inductor":
                self._output.add_index(
                    self._number_nodes + self._number_voltage_sources + lst[1] - 2
                )
            elif lst[0] == "capacitor":
                self._output.add_index(
                    self._number_nodes
                    + self._number_voltage_sources
                    + self._number_inductors
                    + lst[1]
                    - 2
                )

    ### adds indicator about dicm inside inductor
    def set_dicm(self, index, list_elements):
        self._inductors[index - 1].set_dicm(list_elements)

    ### adds indicator about dcvm inside capacitor
    def set_dcvm(self, index, list_elements):
        self._capacitors[index - 1].set_dcvm(list_elements)
