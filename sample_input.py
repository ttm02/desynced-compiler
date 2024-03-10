from desynced_functions import *

"""Sample Function Description """
def sample(parameter_name):

    local_variable = [1, None]
    local_variable = parameter_name + local_variable
    if parameter_name <= local_variable:
        print("LEQ")
    else:
        print("GT")
    for ingr in recipe_ingredients(parameter_name):
        print([ingr,"In Recipe"])
    print("END FOR")

