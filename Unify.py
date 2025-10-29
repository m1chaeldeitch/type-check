# Overall plan:
#   1) Utilize constrain.py to obtain all the constraints
#      in the form of "l_term = r_term"
#   2) Generate a collection of nodes for each term in the
#      constraint system
#   3) Implement the interface for union-find
#   4) Follow the algorithm for unifying

import pycparser
import Constrain


class Node:
    def __init__(self, value):
        self.value = value


def nodify_constraints(filename):
    #Generate the constraint system for the file (function)
    constraints = Constrain.create_constraints(filename)

    #Prepare for storage of each term as a node
    nodes = []

    for constraint in constraints:
        term_l = constraint.l_term
        term_r = constraint.r_term

        nodes.append(Node(term_l.name))
        nodes.append(Node(term_r.name))

    return nodes

if __name__ == "__main__":
    filename = "Trivial.c"
    nodified_constraints = nodify_constraints(filename)
    x = "stop"
    print("balls")