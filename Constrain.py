import sys

import pycparser
from numpy.f2py.auxfuncs import isintent_nothide
from pycparser.c_ast import Decl, Assignment, Constant, ID, BinaryOp

import Parse

#Distinction between different r_terms of statements
class Term:
    def __init__(self, name):
        self.name = name

    def get_name(self):
        return self.name

class TypeTerm(Term):
    def __init__(self, name):
        self.name = name

    def get_type(self):
        return self.name

class IDTerm(Term):
    def __init__(self, name):
        self.name = name

    def get_id(self):
        return self.name

class ExpressionTerm(Term):
    def __init__(self, *terms, op):
        self.terms = terms
        self.op = op

    def get_expr(self):
        return self.terms

#TODO
# Adjust so that I construct the terms before hand, then pass it into the constraint
# constructor. This allows for more detail as to what kind of terms are present

# Probably another case for visitor pattern
class Constraint:
    def __init__(self, l_val, r_val):
        self.l_term = Term(l_val)
        self.r_term = Term(r_val)

    def get_l_term(self):
        return self.l_term

    def get_r_term(self):
        return self.r_term

    def print(self):
        print(f"Constraint: Type of {self.get_l_term().name} = type of {self.get_r_term().name}")


def create_constraints(filename):
    stmts = Parse.get_all_statements(filename)
    constraints = []
    for stmt in stmts:

        #Declarations without initialization (e.g: int x)
        #Looks like "[[x]] = int" in the moller
        #Should be following visitor pattern...
        if isinstance(stmt, Decl):
            term1 = stmt.name
            term2 = stmt.type.type.names[0]
            constraint = Constraint(term1, term2)
            constraints.append(constraint)
            #print(f"[[{term1}]] = {term2}")
            constraint.print()


        #Constant assignment (e.g: x = 5)
        #Looks like "[[x]] = [[5]]" in the book, but since [[5]] is int:
        #I am going with " [[x]] = int"
        if isinstance(stmt, Assignment) and isinstance(stmt.rvalue, Constant):
            term1 = stmt.lvalue.name
            term2 = stmt.rvalue.type
            constraint = Constraint(term1, term2)
            constraints.append(constraint)
            constraint.print()

        #Typevar assignment (e.g: x = y)
        #Looks like [[x]] = [[y]]
        if isinstance(stmt, Assignment) and isinstance(stmt.rvalue, ID):
            term1 = stmt.lvalue.name
            term2 = stmt.rvalue.name
            constraint = Constraint(term1, term2)
            constraints.append(constraint)
            constraint.print()

        #Binary operation assignment (e.g: z = x + y)
        #Looks like [[z]] = [[x]] = [[y]] = [[x op y]]
        #TODO
        # "x op y" is really the simplest case whenever operations only happen on same types
        # hoewever, in C, you can do operations on different types, and sometimes its allowable (?)
        # this requires some table at the minimum to see what the right side evaluates to.
        # THis is for the case of a "double X = 5 + y" where y is either an int or double, so it would
        # be allowed to be stored in X...
        # For now -- we are only looking at the more restrictive side, that is, integer assignment requires that
        # all terms are ints (or casted to ints, although this wasn't discussed in the project description).
        if isinstance(stmt, Assignment) and isinstance(stmt.rvalue, BinaryOp):
            term1 = stmt.lvalue.name
            r_val = stmt.rvalue
            traverse(r_val)
            print("todo")



#Will be useful for later when trying to find all of the items in side of a term?
#TODO
# make this return a triple, where:
#   index 0 is the list of id's
#   index 1 is the list of operators
#   index 2 constants
def traverse(node):
    if isinstance(node, ID):
        print(node.name)
        return
    if isinstance(node, Constant):
        print(node.value)
        return
    #print the left node
    traverse(node.left)

    # print itself
    print(node.op)

    #print the right node
    traverse(node.right)

if __name__ == "__main__":
    filename = "Trivial.c"
    create_constraints(filename)