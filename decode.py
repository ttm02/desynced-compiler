
def get_function_name(code_dict):
    pnames = code_dict['pnames']
    name = code_dict['name']
    name = name.replace(' ', '_')
    pnames = [p.replace('_', ' ') for p in pnames]

    result_str = "def " + name + "("

    for p in pnames:
        result_str = result_str + p + ","
    if len(pnames) > 0:
        result_str = result_str[:-1]  # remove trailing ,
    result_str = result_str + "):"
    return result_str


# signal part of value
def get_signal(param):
    if param == False:
        return "None"
    if isinstance(param, dict):
        if 'id' in param:
            return param['id']
        else:
            return "None"
    if isinstance(param, int):
        return "P" + str(param)
    return param


# number part of value
def get_number(param):
    if param == False:
        return "None"
    if isinstance(param, dict):
        if 'num' in param:
            return str(param['num'])
        else:
            return "None"
    if isinstance(param, int):
        # parameter
        return "P" + str(param)
    # variable
    return param


# both parts of value
def get_both(param):
    if param == False:
        return "None"
    if isinstance(param, dict):
        result_str = "["
        if 'num' in param:
            result_str += str(param['num'])
        else:
            result_str += "None"
        if 'id' in param:
            result_str += str(param['id'])
        else:
            result_str += "None"
        result_str += "]"
        return result_str
    if isinstance(param, int):
        # parameter
        return "P" + str(param)
    # variable
    return param


def decode_lock_slots(inst):
    assert inst['op'] == 'lock_slots'
    assert '0' in inst
    assert '1' in inst

    item = get_signal(inst['0'])
    slot = get_number(inst['1'])
    if slot == 'None':
        slot == "ALL"

    return "lock_slots(%s, slot=%s)" % (item, slot)


def decode_get_max_stack(inst):
    assert inst['op'] == 'get_max_stack'
    assert '0' in inst
    assert '1' in inst

    item = get_signal(inst['0'])
    stack = get_both(inst['1'])
    return stack + " = get_max_stack(" + item + ")"

def decode_order_transfer(inst):
    assert inst['op'] == 'order_transfer'
    assert '0' in inst
    assert '1' in inst

    target = get_both(inst['0'])
    item = get_both(inst['1'])
    return "order_transfer(to="+target+", item=" + item + ")"

def decode_request_item(inst):
    assert inst['op'] == 'request_item'
    assert '0' in inst

    item = get_both(inst['0'])
    return  "request_item(" + item + ")"

def decode_wait(inst):
    assert inst['op'] == 'wait'
    assert '0' in inst

    time = get_number(inst['0'])
    return  "wait(" + time + ")"


def decode_set_number(inst):
    assert inst['op'] == 'set_number'
    assert '0' in inst
    assert '1' in inst
    assert '2' in inst

    var = get_both(inst['2'])
    num = str(get_number(inst['1']))
    signal = get_signal(inst['0'])

    return var + " = [" + num + ", " + signal + "]"


def decode_arith(inst):
    assert inst['op'] == 'add' or inst['op'] == 'sub' or inst['op'] == 'mul' or inst['op'] == 'div'
    assert '0' in inst
    assert '1' in inst
    assert '2' in inst
    var = get_both(inst['2'])
    a = get_number(inst['0'])
    b = get_number(inst['1'])

    operator = "+"
    if inst['op'] == 'sub':
        operator = "-"
    if inst['op'] == 'mul':
        operator = "*"
    if inst['op'] == 'div':
        operator = "/"

    return var + " = " + a + " " + operator + " " + b


def decode_count_slots(inst):
    assert inst['op'] == 'count_slots'
    assert '0' in inst
    assert '1' in inst
    assert 'c' in inst

    var = get_both(inst['0'])
    type_id = inst['c']
    type_str = None
    if type_id == 2:
        type_str = "STORAGE"
    assert type_str is not None  # others are currently not implemented

    return var + " = count_slots(" + type_str + ")"


def decode_for_recipe(inst):
    assert inst['op'] == 'for_recipe_ingredients'
    assert '0' in inst
    assert '1' in inst
    assert '2' in inst

    var = get_both(inst['1'])
    recipe = get_signal(inst['0'])

    tgt = inst['2']
    if not tgt:
        tgt = None

    return "for " + var + " in recipe_ingredients(" + recipe + "): ", tgt



def decode_for_entities_in_range(inst):
    assert inst['op'] == 'for_entities_in_range'
    assert '0' in inst
    assert '1' in inst
    assert '2' in inst
    assert '3' in inst
    assert '4' in inst
    assert '5' in inst

    range = get_number(inst['0'])
    filter = get_signal(inst['1'])
    assert get_both(inst['2']) == "None"
    assert get_both(inst['3']) == "None"
    var = get_both(inst['4'])
    tgt = inst['5']
    if not tgt:
        tgt = None

    return "for " + var + " in entities_in_range(" + range + ", filter=" + filter + "): ", tgt


def decode_into_code_str(as_dict):
    code_str = get_function_name(as_dict) + "\n"
    nesting_lvl = 1
    next_loop_end = []

    for key, instr in as_dict.items():
        if key.isdigit():
            if len(next_loop_end) > 0 and int(key) == next_loop_end[0]:
                nesting_lvl -= 1
                assert nesting_lvl > 0
                next_loop_end = next_loop_end[1:]

            for i in range(nesting_lvl):
                code_str += '\t'
            if instr['op'] == 'set_number':
                code_str += decode_set_number(instr)
            elif instr['op'] in ('add', 'sub', 'mul', 'div'):
                code_str += decode_arith(instr)
            elif instr['op'] == 'for_recipe_ingredients':
                nesting_lvl += 1  # begin loop
                st, tgt = decode_for_recipe(instr)
                if tgt:
                    next_loop_end.insert(0, tgt - 1)
                code_str += st
            elif instr['op'] == 'for_entities_in_range':
                nesting_lvl += 1  # begin loop
                st, tgt = decode_for_entities_in_range(instr)
                if tgt:
                    # TODO some nested loops are displayed wrong
                    next_loop_end.insert(0, tgt - 1)
                code_str += st
            elif instr['op'] == 'count_slots':
                code_str += decode_count_slots(instr)
            elif instr['op'] == 'request_item':
                code_str += decode_request_item(instr)
            elif instr['op'] == 'order_transfer':
                code_str += decode_order_transfer(instr)
            elif instr['op'] == 'lock_slots':
                code_str += decode_lock_slots(instr)
            elif instr['op'] == 'get_max_stack':
                code_str += decode_get_max_stack(instr)
            elif instr['op'] == 'wait':
                code_str += decode_wait(instr)
            else:
                code_str += "UNKNOWN_OPCODE: " + instr['op']
            # print(instr)

            code_str += '\n'

    return code_str