# Overall plan:
#   1) Utilize constrain.py to obtain all the constraints
#      in the form of "l_term = r_term"
#   2) Generate a collection of nodes for each term in the
#      constraint system
#   3) Implement the interface for union-find
#   4) Follow the algorithm for unifying

import pycparser
import Constrain
from Constrain import IDTerm, TypeTerm


def _make_set(term):
    term.parent = term

def find(term):
    if term.parent != term:
        term.parent = find(term.parent)

    return term.parent

def union(term_x, term_y):
    x_representative = find(term_x)
    y_representative = find(term_y)

    if x_representative != y_representative:
        x_representative.parent = y_representative

def unify(term_1, term_2):
    term_1_representative = find(term_1)
    term_2_representative = find(term_2)

    if term_1_representative != term_2_representative:
        if isinstance(term_1_representative, IDTerm) and isinstance(term_2_representative, IDTerm):
            union(term_1_representative, term_2_representative)
        elif isinstance(term_1_representative, IDTerm) and isinstance(term_2_representative, TypeTerm):
            union(term_1_representative, term_2_representative)
        elif isinstance(term_1_representative, TypeTerm) and isinstance(term_2_representative, IDTerm):
            union(term_2_representative, term_1_representative)
        elif isinstance(term_1_representative, TypeTerm) and isinstance(term_2_representative, TypeTerm) and term_1_representative.name == term_2_representative.name:
            union(term_1_representative, term_2_representative)
        else:
            return False
    return True

def perform_unification(filename):
    #collect constraint system
    constraints = Constrain.create_constraints(filename)

    #base for unification
    for constraint in constraints:
        term_a = constraint.l_term
        term_b = constraint.r_term

        _make_set(term_a)
        _make_set(term_b)

    #attempt to unify each constraint
    for constraint in constraints:
        term_a = constraint.l_term
        term_b = constraint.r_term

        unified = unify(term_a, term_b)

        if not unified:
            return False

    return True

if __name__ == "__main__":
    filename = "Trivial.c"
    print(f"\n\n{perform_unification(filename)}")