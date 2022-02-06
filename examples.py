#!/bin/env python

from State_model import System, State_space_model
from State_model.Elements import *
import sympy as sym


def create_boost(model: System):
    Vi, Li, R_Li, Co, Ro = sym.symbols(["Vi", "Li", "R_{Li}", "Co", "Ro"])

    model.create_element(Voltage_source(1, 1, 0, Vi))
    model.create_element(Resistor(2, 1, 2, R_Li))
    model.create_element(Inductor(1, 2, 3, Li))
    model.create_element(Switch(1, 3, 3, 0))
    model.create_element(Switch(2, 3, 3, 4))
    model.create_element(Capacitor(1, 4, 0, Co))
    model.create_element(Resistor(1, 4, 0, Ro))

    model.set_control(1, "on_state")
    model.set_control(2, "off_state")
    model.set_output([["node", 4]])
    model.initialize()
    model.initialise_output()

    return model


def create_buck(model: System):
    Vi, Li, Co, Ro = sym.symbols(["Vi", "Li", "Co", "Ro"])

    model.create_element(Voltage_source(1, 1, 0, Vi))
    model.create_element(Switch(1, 3, 1, 2))
    model.create_element(Switch(2, 3, 2, 0))
    model.create_element(Inductor(1, 2, 3, Li))
    model.create_element(Capacitor(1, 3, 0, Co))
    model.create_element(Resistor(1, 3, 0, Ro))

    model.set_control(1, "on_state")
    model.set_control(2, "off_state")
    model.set_output([["node", 3]])
    model.initialize()
    model.initialise_output()

    return model


def create_cuk(model: System):
    Vi, Li, Lo, Cc, Co, Ro = sym.symbols(["Vi", "Li", "Lo", "Cc", "Co", "Ro"])

    model.create_element(Voltage_source(1, 1, 0, Vi))
    model.create_element(Switch(1, 3, 2, 0))
    model.create_element(Switch(2, 3, 3, 0))
    model.create_element(Inductor(1, 1, 2, Li))
    model.create_element(Capacitor(1, 2, 3, Cc))
    model.create_element(Inductor(2, 3, 4, Lo))
    model.create_element(Capacitor(2, 4, 0, Co))
    model.create_element(Resistor(1, 4, 0, Ro))

    model.set_control(1, "on_state")
    model.set_control(2, "off_state")
    model.set_output([["node", 4]])
    model.initialize()
    model.initialise_output()

    return model


def main():
    with System() as model:
        print("#" * 80)
        print("Example - Boost Model\n")

        model = create_boost(model)

        state_space_model = State_space_model(model)
        state_space_model.form_states()
        state_space_model.form_state_lists()
        state_space_model.print_states()

        [print(state.get_matrices()) for state in state_space_model.get_states()]

        print("\n" + "#" * 80 + "\n")

    with System() as model:
        print("#" * 80)
        print("Example - Buck Model\n")

        model = create_buck(model)

        state_space_model = State_space_model(model)
        state_space_model.form_states()
        state_space_model.form_state_lists()
        state_space_model.print_states()

        [print(state.get_matrices()) for state in state_space_model.get_states()]

        print("\n" + "#" * 80 + "\n")

    with System() as model:
        print("#" * 80)
        print("Example - Cuk Model\n")

        model = create_cuk(model)

        state_space_model = State_space_model(model)
        state_space_model.form_states()
        state_space_model.form_state_lists()
        state_space_model.print_states()

        [print(state.get_matrices()) for state in state_space_model.get_states()]

        print("\n" + "#" * 80 + "\n")


if __name__ == "__main__":
    main()
