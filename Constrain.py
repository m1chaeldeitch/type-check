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

class LiteralTerm(Term):
    def __init__(self, literal_type):
        self.type = literal_type

    def get_literal(self):
        return self.type

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
        print(f"Constraint: [[{self.get_l_term().name}]] = [[{self.get_r_term().name}]]")


def create_constraints(filename):
    stmts = Parse.get_all_statements(filename)
    constraint = None
    constraints = []
    for stmt in stmts:

        #Declarations without initialization (e.g: int x)
        #Looks like "[[x]] = int" in the moller
        #Should be following visitor pattern...
        if isinstance(stmt, Decl):
            term1 = stmt.name
            term2 = stmt.type.type.names[0]
            constraint = Constraint(term1, term2)

        #Constant assignment (e.g: x = 5)
        #Looks like "[[x]] = [[5]]" in the book, but since [[5]] is int:
        #I am going with " [[x]] = int"
        if isinstance(stmt, Assignment) and isinstance(stmt.rvalue, Constant):
            term1 = stmt.lvalue.name
            term2 = stmt.rvalue.type
            constraint = Constraint(term1, term2)

        #Typevar assignment (e.g: x = y)
        #Looks like [[x]] = [[y]]
        if isinstance(stmt, Assignment) and isinstance(stmt.rvalue, ID):
            term1 = stmt.lvalue.name
            term2 = stmt.rvalue.name
            constraint = Constraint(term1, term2)

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
            r_terms = traverse_and_collect(r_val)

            #Chain the constraints together
            # [x] = [y] = [z]

            constraint = Constraint(term1, r_terms[0].name)
            duplicate_constraint = False

            if not _constraint_exists(constraint, constraints):
                constraints.append(constraint)
                constraint.print()

            for i in range(1, len(r_terms)):
                #print(f"Got to iteration [{i}]")
                curr_r_term_class = r_terms[i].__class__
                prev_r_term_class = r_terms[i-1].__class__
                constraint = ""

                if curr_r_term_class == LiteralTerm and prev_r_term_class == LiteralTerm:
                    # e.g: Int z = 3 + 3
                    constraint = Constraint(r_terms[i - 1].type, r_terms[i].type)

                elif curr_r_term_class == LiteralTerm and prev_r_term_class is not LiteralTerm:
                    # e.g: Int z = x + 3
                    constraint = Constraint(r_terms[i-1].name, r_terms[i].type)

                elif curr_r_term_class != LiteralTerm and prev_r_term_class == LiteralTerm:
                    # e.g: Int z = 3 + x
                    #todo: For diagnosiing issues in the future, this might be a good start
                    # the constriants here would be written as [[3]] = [[x]], which might be weird to deal with
                    constraint = Constraint(r_terms[i-1].type, r_terms[i].name)

                elif curr_r_term_class != LiteralTerm and prev_r_term_class != LiteralTerm:
                    #e.g Int z = x + y
                    constraint = Constraint(r_terms[i - 1].name, r_terms[i].name)

                else:
                    print("Error in parsing a binary operation.")

                if not _constraint_exists(constraint, constraints):
                    constraints.append(constraint)
                    constraint.print()

        if not _constraint_exists(constraint, constraints):
            constraints.append(constraint)
            constraint.print()

    return constraints

#Will be useful for later when trying to find all of the items in side of a term?
#TODO
# make this return a triple, where:
#   index 0 is the list of id's
#   index 1 is the list of operators
#   index 2 constants


def _constraint_exists(new_constraint, existing_constraints):
    duplicate_constraint = False
    for existing_constraint in existing_constraints:
        if existing_constraint.get_l_term().name == new_constraint.get_l_term().name and existing_constraint.get_r_term().name == new_constraint.get_r_term().name:
            return True
        elif existing_constraint.get_l_term().name == new_constraint.get_r_term().name and existing_constraint.get_r_term().name == new_constraint.get_l_term().name:
            return True
    return False

def traverse_and_collect(node):
    ids = []
    operators = []
    constants = []
    terms = []
    traverse(node, terms)
    return terms

def traverse(node, terms):
    if isinstance(node, ID):
        #print(node.name)
        terms.append(IDTerm(node.name))
        return
    if isinstance(node, Constant):
        #print(node.value)
        terms.append(LiteralTerm(node.type))
        return
    #print the left node
    traverse(node.left, terms)

    # print itself
    #TODO: CHeck this:
    # Don't really need to add the operator in the constraint?
    #terms.append(node.op)
    #print(node.op)

    #print the right node
    traverse(node.right, terms)

if __name__ == "__main__":
    filename = "Trivial.c"
    all_constraints = create_constraints(filename)
    x = "stop"