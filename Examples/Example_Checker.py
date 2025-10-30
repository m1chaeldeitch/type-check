import Unify
if __name__ == '__main__':
    #Check a correctly typed C program, "CorrectlyTypedA.c"
    print(f"Results for [CorrectlyTypedA.c]: [{Unify.perform_unification("CorrectlyTypedA.c")}]")

    #Check another correctly typed C program, "CorrectlyTypedB.c"
    print(f"Results for [CorrectlyTypedB.c]: [{Unify.perform_unification("CorrectlyTypedB.c")}]")

    # Check an incorrectly typed C program, "IncorrectlyTypedA.c"
    print(f"Results for [IncorrectlyTypedA.c]: [{Unify.perform_unification("IncorrectlyTypedA.c")}]")

    # Check another incorrectly typed C program, "IncorrectlyTypedB.c"
    print(f"Results for [IncorrectlyTypedB.c]: [{Unify.perform_unification("IncorrectlyTypedB.c")}]")


    #FIXME There is an issue within the constraining algorithm that throws up when it sees something like:
    # x = 2 + 2;