# class of nodes
class Node:
    def __init__(self, node):
        self._index = node
        self._elements = []
        self._element_number = 0

    def index(self):
        return self._index

    def __eq__(self, node):
        return self._index == node._index

    def __lt__(self, node):
        return True

    def __ne__(self, node):
        return self._index != node._index

    def __str__(self):
        return "node" + str(self._index)

    def add_element(self, element):
        self._elements.append(element)
        self._element_number += 1

    def get_elements(self):
        return self._elements

    def get_element_number(self):
        return self._element_number
