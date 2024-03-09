from convert import get_dict_from_desynced_str


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

def main():
    if_sample = "DSC8Y3kBDfk1BF4N725IhKC2ydfgH1i1R9b1StvGG4LPqFi3srfJa455kS50b3NV50CYwAz2TgVX31sn7qq3sFWFy0zyhPU1lQUy324A44T3IxtNR4Rx6364bZRne3XjWwl1A27Jw0uOykK0eSnUo3SEMYl2Nrifp0hnpgs2b1bUR4EokmO1XGTSg0xg9zb3Usf9S06WhVo0WCG5B1U2if11HeHRS0TKnH32n28v626bzAl2xVC9l2xpCPz1YdYDI0BjmRV2QO7mt3qtwte0MVDPI1fkjnwl"
    complex_sample_script = "DSC1Dh1Y0A1I1Bt2tR1NLvhY223I0u2Nomhi0ISJb52owTeG3JX3GP1hRRTO2gGSrG4J5Meb451rQ42vwdps1LljmK2XeBVa0jZytE4Ayl6B2C2cSK1Jz0582BbFd64SvrVO0bZMBJ2ilOVH1mSDfR2emb320CGaKz4PvDv13GnIsr3Jc6tC1FU4Px0nj01y24v1df0ral4M0dWVhV03jINe2T8hQf0aUrNC3nowiy45nVVS4d1Yqc08BeeK4WAW0d3CIfM72tn5Ym2tdv3h0zlPaJ2doZp63qa4uT2XWEmY1OJKEO28It8J2ke2AV03k3VN0gGAJY3pn4tI01gWee4Ojo5B41yXNs3JZ8Ts265QJ00Zwclq4Z0o4549ZUgN4ZcojH2IrjEk0ElTja2l3wZU02PAlW1xzkpV2mcvTu38oepn2SfHCj4crFIV27ilfc0O2Luc4Ixvyr1hIgXC1XvWbf3Jb0RK3GhNFR0NAp6j25gnAj1X1MKZ0YMGAY4XxYkU2IWvBH31izTV4AZK6f42lqXH4Ngf0N3yhzBs2wlvII3nUWcN09IFj62WWNfl4XR8RE3RKGlW0FgrBy3ei6wi0tR5aZ3yRAGE22Ff0h0y2FCQ45RP3B17HkpC2kyLFf4TsO0A4AoL2z3uQTPL4ejGqE34RNkA0ikIG73AchaR0S7zpD3qTrh41p5fLx0LGHBB2PIaxC2VVGRw0KWoJX4I9sLR22ee2R28xIX508zDwL4MPsoI0SrLnF2e38OX1KIcgj2hfrdY0DOJYy42DXVb0Y5Hpj3evNpM3dU8gT3GLJbu3eO8tV4GEDMl3sCiak0TYjVF3hOFJQ13P3qs16aAwv1k2n413Hbcq23681a43XXrU20cG0dp1X9skp2tpEgF1ISEvm1HdmZW2675aL0OH5aP4c0zeH0WpFJP3CVaxC3To1Fv0ZyCK61oR2xM09R8Gc25gh5Q4YT9co06BHrd1W2vXn2rBzuH3UsTZA396oAI23LlWd0cJzqw0J8eBi1nPrQP3LN0932hHkMg3E5F4k0b1MTJ0dM06y4WHezk2VaHOv3yWgUF0cqyIS16UOHK1Xd2mv4fjzKO0MXFSh"
    simple_sample_script = "DSC7h2aG6ae1BX2uH1D6tqS1t5pjg0NibnM2eMJHl2AbaLj15J95Y3NAyL53KNBPI1oRarX02p8cc21J6z74boEtP4g4tXY4VjBfk2LaqZB4Ty2UF0CvQHa4e2SH125IoTe1LoZau2bqzbY3iC9XK3HyTFS1XF9d72Jjhip23onu84c4cZ014ZhuQ4fwaVX2MCq5531qVz33k1MiC0k2w360srPDh1X62Ra3cKNjX1d8RzS0QnuPM3gHMIv0EnzGJ0VYins1EY11J29mH5T2uwhxQ36Iyx5143Cvj07v68s1kF3UPW"

    as_dict = get_dict_from_desynced_str(if_sample)

    print(as_dict)

if __name__ == "__main__":
    main()


