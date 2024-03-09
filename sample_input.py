# def Factory_Block_Manager(Good_Produced):
#	A = [1, None]
#	for B in recipe_ingredients(P1):
#		A = A + 1
#	B = count_slots(STORAGE)
#	C = B / A
#	D = [1, None]

"""Sample Function"""
def sample(parameter_name):
    local_variable = [1, None]
    local_variable = parameter_name + local_variable
    if parameter_name <= local_variable:
        print("LEQ")
    else:
        print("GT")
    print("END")

