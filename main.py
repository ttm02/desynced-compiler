from convert import get_desynced_str_from_dict

import pandas as pd
import ast

CSV_FILE_NAME = "desynced_instructions.csv"

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

instruction_data = pd.DataFrame()


def get_value_from_ast_node(astnode):
    if isinstance(astnode, ast.List):
        assert len(astnode.elts) == 2
        assert isinstance(astnode.elts[0], ast.Constant) or isinstance(astnode.elts[0], ast.Name)
        assert isinstance(astnode.elts[1], ast.Constant) or isinstance(astnode.elts[1], ast.Name)

        if isinstance(astnode.elts[0], ast.Constant):
            num = astnode.elts[0].value
        else:
            num = astnode.elts[0].id

        if isinstance(astnode.elts[1], ast.Constant):
            signal = astnode.elts[1].value
        else:
            signal = astnode.elts[1].id

        assert not (num is None and signal is None)

        result = {}
        if num is not None:
            result['num'] = num
        if signal is not None:
            result['id'] = signal

        return result
    else:
        assert isinstance(astnode, ast.Name)
        return astnode.id


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
        result_stmt['1'] = get_value_from_ast_node(assign_node.value)
        result_stmt['2'] = tgt
        result_stmt['next'] = False
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

        left = get_value_from_ast_node(assign_node.value.left)

        right = get_value_from_ast_node(assign_node.value.right)

        result_stmt = {'op': op, '0': left, '1': right, '2': tgt, 'next': False}
        return result_stmt

    elif isinstance(assign_node.value, ast.Call):
        result_stmt, assign_tgt_idx = handle_call(assign_node.value)
        result_stmt[assign_tgt_idx] = tgt
        return result_stmt


    else:
        assert False


"returns the dict for the instruction, and the output arg to est if used in assignment"


def handle_call(call_node):
    assert isinstance(call_node, ast.Call)
    assert isinstance(call_node.func, ast.Name)
    called_func = call_node.func.id[len(VARIABLE_PREFIX):]
    if called_func == "print":
        assert len(call_node.args) == 1
        arg = call_node.args[0]
        if isinstance(arg, ast.List):
            arg = get_value_from_ast_node(arg)
            assert len(arg) == 2
        else:
            assert isinstance(arg, ast.Constant)
            arg = {'num': False, "id": arg.value}
        # num = signal to show
        # id = text to display
        return {'op': 'notify', '0': arg['num'], 'txt': arg['id'], 'next': False}, None

    if called_func in instruction_data.index:
        this_instruction_data = instruction_data.loc[called_func]
        assert len(call_node.args) == this_instruction_data['num_args']
        result_stmt = {'op': called_func, 'next': False}
        if this_instruction_data['is_iterator']:
            result_stmt['op'] = "for_" + called_func
        for i in range(1, this_instruction_data['num_args'] + 1):
            result_stmt[str(i)] = False
        for i, arg in zip(this_instruction_data['arg_idxs'], call_node.args):
            result_stmt[str(i)] = get_value_from_ast_node(arg)
        return result_stmt, str(int(this_instruction_data['output_arg_num']))

    else:
        assert False and "not Implemented yet"


def get_paths_from_predicate(predicate):
    """return triple: Larger? smaller? equal? True: if path will be taken, false: else path"""
    if isinstance(predicate, ast.LtE):
        return [False, True, True]
    if isinstance(predicate, ast.Lt):
        return [False, True, False]
    if isinstance(predicate, ast.Eq):
        return [False, False, True]
    if isinstance(predicate, ast.NotEq):
        return [True, True, False]
    if isinstance(predicate, ast.GtE):
        return [True, False, True]
    if isinstance(predicate, ast.Gt):
        return [True, False, False]
    else:
        assert False and "Not implemented yet"


def handle_for(for_node, incoming_instrs, result_list):
    assert isinstance(for_node, ast.For)
    # print(ast.dump(for_node))
    assert len(incoming_instrs) > 0
    assert isinstance(for_node.target, ast.Name)
    loop_var = get_value_from_ast_node(for_node.target)
    assert isinstance(for_node.iter, ast.Call)
    # TODO also support for i in range(variable or number literal)?

    result_stmt, arg_to_use_as_iterator = handle_call(for_node.iter)
    assert arg_to_use_as_iterator is not None
    result_stmt[arg_to_use_as_iterator] = loop_var
    add_to_result_list(incoming_instrs, result_list, result_stmt)

    # body
    body_endings = code_gen(for_node.body, [(result_stmt, 'next')], result_list)

    # TODO check if '2' is valid for all for loop intsructions
    return [(result_stmt, '2')]


def handle_while(while_node, incoming_instrs, result_list):
    assert isinstance(while_node, ast.While)
    # print(ast.dump(for_node))
    assert len(incoming_instrs) > 0

    if isinstance(while_node.test, ast.Compare):
        result_stmt, if_end, else_end = generate_compare_number(while_node.test, while_node.body, None,
                                                                incoming_instrs, result_list)
        for instr, idx_to_set in if_end:
            to_return_to = result_list.index(result_stmt) + 1
            instr[idx_to_set] = to_return_to

        return else_end
    # endless loop
    elif isinstance(while_node.test, ast.Constant) and while_node.test.value == True:
        to_return_to = len(result_list) + 1  # the nest instruction inserted by codegen
        loop_ends = code_gen(while_node.body, incoming_instrs, result_list)
        for instr, idx_to_set in loop_ends:
            instr[idx_to_set] = to_return_to
        return []


def generate_compare_number(test_node, if_body, else_body, incoming_instrs, result_list):
    assert isinstance(test_node, ast.Compare)
    assert len(test_node.ops) == 1
    assert len(test_node.comparators) == 1

    lhs = test_node.left
    rhs = test_node.comparators[0]
    predicate = test_node.ops[0]

    lhs = get_value_from_ast_node(lhs)
    rhs = get_value_from_ast_node(rhs)

    paths = get_paths_from_predicate(predicate)

    result_stmt = {'0': False,  # larger
                   '1': False,  # smaller
                   'next': False,  # equal
                   '2': lhs, '3': rhs, 'op': 'check_number'}
    add_to_result_list(incoming_instrs, result_list, result_stmt)
    prev_instrs = []
    if paths[0]:
        prev_instrs.append((result_stmt, '0'))
    if paths[1]:
        prev_instrs.append((result_stmt, '1'))
    if paths[2]:
        prev_instrs.append((result_stmt, 'next'))
    # if path
    if_end = code_gen(if_body, prev_instrs, result_list)

    assert if_body is not None
    prev_instrs = []
    if not paths[0]:
        prev_instrs.append((result_stmt, '0'))
    if not paths[1]:
        prev_instrs.append((result_stmt, '1'))
    if not paths[2]:
        prev_instrs.append((result_stmt, 'next'))

    if else_body is not None:
        # else path
        else_end = code_gen(else_body, prev_instrs, result_list)
    else:
        else_end = prev_instrs

    return result_stmt, if_end, else_end


def handle_if(if_node, incoming_instrs, result_list):
    assert isinstance(if_node, ast.If)
    assert len(incoming_instrs) > 0
    # TODO currently only compare_number is supported
    assert isinstance(if_node.test, ast.Compare)
    result_stmt, if_end, else_end = generate_compare_number(if_node.test, if_node.body, if_node.orelse, incoming_instrs,
                                                            result_list)

    return if_end + else_end


"""
incoming_instr is a list of tuples (instruction,key to replace)
result_list holds the list of all instructions generated so far

"""


def code_gen(body, incoming_instrs, result_list):
    if len(body) == 0:
        return

    # add dummy
    prev_instrs = [({'next': False}, 'next')] + incoming_instrs

    i = 0
    for node in body:
        if isinstance(node, ast.Assign):
            result_stmt = handle_assign(node)
            add_to_result_list(prev_instrs, result_list, result_stmt)
            prev_instrs = [(result_stmt, 'next')]
        elif isinstance(node, ast.Expr):
            if isinstance(node.value, ast.Call):
                result_stmt, _ = handle_call(node.value)
                add_to_result_list(prev_instrs, result_list, result_stmt)
                prev_instrs = [(result_stmt, 'next')]
            else:
                print(ast.dump(node))
                assert False and "Not yet Implemented"
        elif isinstance(node, ast.If):
            prev_instrs = handle_if(node, prev_instrs, result_list)
        elif isinstance(node, ast.For):
            prev_instrs = handle_for(node, prev_instrs, result_list)
        elif isinstance(node, ast.While):
            prev_instrs = handle_while(node, prev_instrs, result_list)
        else:
            print(ast.dump(node))
            assert False and "Not yet Implemented"

    return prev_instrs


def add_to_result_list(prev_instrs, result_list, result_stmt):
    new_elem_pos = len(result_list)
    result_list.append(result_stmt)
    for inst, key in prev_instrs:
        inst[key] = new_elem_pos + 1


def main():
    src_file_name = "sample_input.py"

    global instruction_data
    instruction_data = pd.read_csv(CSV_FILE_NAME, index_col="name", converters={"arg_idxs": ast.literal_eval})

    with open(src_file_name, 'r') as src_file:
        tree = ast.parse(src_file.read(), filename=src_file_name)

    print(ast.dump(tree))
    assert isinstance(tree, ast.Module)
    docstr = ""

    for node in tree.body:
        if isinstance(node, ast.Expr):
            assert isinstance(node.value, ast.Constant)
            docstr = node.value.value

        elif isinstance(node, ast.ImportFrom) or isinstance(node, ast.Import):
            pass  # ignore

        elif isinstance(node, ast.FunctionDef):
            print("compile function %s:" % node.name)
            result_dict = compile_function(node, docstr)
            print("as dict:")
            print(result_dict)
            print("encode to desynced string:")
            print(get_desynced_str_from_dict(result_dict))
        else:
            assert False


def compile_function(func, docstr):
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
    for node in ast.walk(func):
        if isinstance(node, ast.Name):
            node.id = VARIABLE_PREFIX + node.id
    # print(ast.dump(func))
    result_list = []
    code_gen(func.body, [], result_list)
    for i, stmt in enumerate(result_list):
        as_dict[str(i)] = stmt
    re_name_params(as_dict, param_names)
    return as_dict


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
