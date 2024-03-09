from convert import get_dict_from_desynced_str, get_desynced_str_from_dict
import ast

# performance for testing:
as_dict_simple = {'0': {'0': {'id': 'metalore', 'num': -2147483648}, 'op': 'mine', 'next': False},
                  '1': {'0': 1, '1': False, 'op': 'dodrop'}, 'parameters': [False], 'id': 'b_metal_miner',
                  'desc': 'Mines Metal Ore and drops it off to the specified location in the register',
                  'pnames': ['Resource'], 'name': 'Metal Miner Behavior'}

as_dict_complex = {
    '0': {'0': False, '1': {'num': 1}, '2': 'A', 'cmt': 'Count number of Ingredients (+1 for Production result)',
          'op': 'set_number'},
    '1': {'0': 1, '1': 'B', '2': 4, 'op': 'for_recipe_ingredients'},
    '2': {'0': 'A', '1': {'num': 1}, '2': 'A', 'op': 'add', 'next': False},
    '3': {'0': 'B', '1': False, 'op': 'count_slots', 'c': 2},
    '4': {'0': 'B', '1': 'A', '2': 'C', 'cmt': 'Get Number of Slots per item', 'op': 'div'},
    '5': {'0': {'num': 1}, '1': {'num': 1}, '2': 'D', 'cmt': 'Current inv slot', 'op': 'set_number'},
    '6': {'0': 1, '1': 'E', '2': 13, 'op': 'for_recipe_ingredients'},
    '7': {'0': {'num': 1}, '1': {'num': 1}, '2': 'F', 'cmt': 'Local loop counter', 'op': 'set_number'},
    '8': {'0': 'E', '1': 'D', 'op': 'lock_slots'},
    '9': {'0': 'D', '1': {'num': 1}, '2': 'D', 'op': 'add'},
    '10': {'0': 'F', '1': {'num': 1}, '2': 'F', 'op': 'add'},
    '11': {'0': False, '1': 9, '2': 'F', '3': 'C', 'cmt': 'For i in range(ingredients_per_slot)',
           'op': 'check_number', 'next': 9},
    '12': {'0': 1, '1': 'D', 'op': 'lock_slots'},
    '13': {'0': 'D', '1': {'num': 1}, '2': 'D', 'op': 'add'},
    '14': {'1': 13, '2': 'D', '3': 'B', 'cmt': 'while current_slot <= Num_Slots', 'op': 'check_number', 'next': 13},
    '15': {'0': {'id': 'v_star', 'num': 1}, 'cmt': 'End Setup', 'op': 'jump', 'next': False},
    '16': {'0': {'id': 'v_star', 'num': 1}, 'op': 'label', 'cmt': 'Produce'},
    '17': {'0': 1, '1': 'A', '2': 24, 'ny': 1095.4998741149902, 'op': 'for_recipe_ingredients', 'nx': 0},
    '18': {'0': 'A', '1': 'B', 'op': 'get_max_stack'},
    '19': {'0': 'B', '1': 'C', '2': 'D', 'op': 'mul'},
    '20': {'0': 'D', 'op': 'request_item'},
    '21': {'0': {'num': 1}, '1': {'id': 'v_building'}, '2': False, '3': False, '4': 'E', '5': False,
           'op': 'for_entities_in_range'},
    '22': {'0': 'E', '1': 'B', 'op': 'order_transfer', 'next': False},
    '23': {'0': 1, '1': 'G', '2': False, 'cmt': 'Wait if we have at least one stack produced', 'op': 'count_item',
           'c': 1},
    '24': {'0': 1, '1': 'H', 'op': 'get_max_stack'},
    '25': {'1': 28, '2': 'G', '3': 'H', 'op': 'check_number'},
    '26': {'0': {'num': 100}, 'op': 'wait'},
    '27': {'0': {'num': 1, 'id': 'v_star'}, 'ny': 1482.658290863037, 'op': 'jump', 'nx': 1627.3013458251953},
    'pnames': ['Good Produced'],
    'desc': 'Factory Block Manager. TODO: error report if not enough inventory slots TOTO better wait logic',
    'parameters': [False], 'name': 'Factory Block Manager'}

dict_if_sample = {'0': {'0': False, '1': {'num': 1}, '2': 'A', 'op': 'set_number'},
                  '1': {'0': 4, '1': 5, '2': 'A', '3': {'num': 1}, 'op': 'check_number'},
                  '2': {'0': False, 'txt': 'EQ', 'op': 'notify', 'next': False},
                  '3': {'0': False, 'txt': 'LARGER', 'op': 'notify', 'next': False},
                  '4': {'0': False, 'txt': 'LESS', 'op': 'notify'}, 'desc': 'Sample Function',
                  'parameters': [False, False], 'pnames': ['summand', 'result'], 'name': 'test_if'}

VARIABLE_PREFIX = "VAR_"


def decode_list_literal(list_literal):
    assert isinstance(list_literal, ast.List)
    assert len(list_literal.elts) == 2
    assert isinstance(list_literal.elts[0], ast.Constant) or isinstance(list_literal.elts[0], ast.Name)
    assert isinstance(list_literal.elts[1], ast.Constant) or isinstance(list_literal.elts[1], ast.Name)

    if isinstance(list_literal.elts[0], ast.Constant):
        num = list_literal.elts[0].value
    else:
        num = list_literal.elts[0].id

    if isinstance(list_literal.elts[1], ast.Constant):
        signal = list_literal.elts[1].value
    else:
        signal = list_literal.elts[1].id

    assert not (num is None and signal is None)

    result = {}
    if num is not None:
        result['num'] = num
    if signal is not None:
        result['id'] = signal

    return result


def handle_assign(assign_node):
    # print(ast.dump(assign_node))
    assert isinstance(assign_node, ast.Assign)
    assert len(assign_node.targets) == 1
    assert isinstance(assign_node.targets[0], ast.Name)
    tgt = assign_node.targets[0].id

    # check kind of operation
    if isinstance(assign_node.value, ast.List):
        # assign constant (set_number statement)
        result_stmt = {}
        result_stmt['op'] = 'set_number'
        result_stmt['0'] = False
        result_stmt['1'] = decode_list_literal(assign_node.value)
        result_stmt['2'] = tgt
        return result_stmt

        pass
    elif isinstance(assign_node.value, ast.BinOp):
        # Math
        op = assign_node.value.op
        if isinstance(op, ast.Add):
            op = "add"
        elif isinstance(op, ast.Sub):
            op = "sub"
        elif isinstance(op, ast.Mult):
            op = "mul"
        elif isinstance(op, ast.Div):
            op = "div"
        else:
            assert False  # unknown math op

        left = assign_node.value.left
        if isinstance(left, ast.List):
            left = decode_list_literal(left)
        else:
            assert isinstance(left, ast.Name)
            left = left.id

        right = assign_node.value.right
        if isinstance(right, ast.List):
            right = decode_list_literal(right)
        else:
            assert isinstance(right, ast.Name)
            right = right.id
            result_stmt = {}
            result_stmt['op'] = op
            result_stmt['0'] = left
            result_stmt['1'] = right
            result_stmt['2'] = tgt
            return result_stmt

    else:
        assert False

    return {}


def main():
    src_file_name = "sample_input.py"

    with open(src_file_name, 'r') as src_file:
        tree = ast.parse(src_file.read(), filename=src_file_name)

    assert isinstance(tree, ast.Module)
    funcs = [f for f in tree.body]

    # only one function allowed
    assert len(funcs) <= 2

    func = funcs[0]
    docstr = ""

    if len(funcs) == 2:
        func = funcs[1]
        docstr = funcs[0]

    assert isinstance(func, ast.FunctionDef)

    if docstr != "":
        assert isinstance(docstr, ast.Expr)
        assert isinstance(docstr.value, ast.Constant)
        docstr = docstr.value.value

    # check args
    assert func.args.vararg == None
    assert func.args.kwonlyargs == []
    assert func.args.kw_defaults == []
    assert func.args.kwarg == None
    assert func.args.defaults == []

    # TODO find the correct value
    MAX_ARG_NUM = 4
    assert len(func.args.args) <= MAX_ARG_NUM

    param_names = [a.arg for a in func.args.args]

    # the compilation result
    as_dict = {}
    as_dict['desc'] = docstr
    as_dict['name'] = func.name
    as_dict['id'] = "b_" + func.name
    as_dict['pnames'] = param_names
    as_dict['parameters'] = [False for _ in param_names]

    # rename all variables to avoid conflicts with the variable names used ingame
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            node.id = VARIABLE_PREFIX + node.id

    i = 0
    for node in func.body:
        if isinstance(node, ast.Assign):
            result_stmt = handle_assign(node)
            as_dict[str(i)] = result_stmt
        else:
            assert False and "Not yet Implemented"
        i += 1

    re_name_params(as_dict, param_names)

    print(as_dict)
    print(get_desynced_str_from_dict(as_dict))


def re_name_params(as_dict, param_names):
    param_names_with_prefix = [VARIABLE_PREFIX + p for p in param_names]
    MAX_NUM_PARAMS = 11
    # Rename Variables and parameters
    variables_used = {}
    next_available_variable = 'A'
    for key_instr_num, stmt in as_dict.items():
        if isinstance(stmt, dict):
            keys_to_check = [k for k in stmt if k.isdigit()]
            for key_arg_num in keys_to_check:
                val = stmt[key_arg_num]
                if isinstance(val, str):
                    if val.startswith(VARIABLE_PREFIX):
                        if val in param_names_with_prefix:
                            stmt[key_arg_num] = param_names_with_prefix.index(val) + 1
                        elif val in variables_used:
                            stmt[key_arg_num] = variables_used[val]
                        else:
                            # new variable
                            variables_used[val] = next_available_variable
                            next_available_variable = chr(ord(next_available_variable) + 1)  # next char
                            stmt[key_arg_num] = variables_used[val]
                            assert next_available_variable != 'Z'  # too much variables


if __name__ == "__main__":
    main()
