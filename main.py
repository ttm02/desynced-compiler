from convert import get_dict_from_desynced_str, get_desynced_str_from_dict

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




def main():
    complex_sample_script = "DSC1Dh1Y0A1I1Bt2tR1NLvhY223I0u2Nomhi0ISJb52owTeG3JX3GP1hRRTO2gGSrG4J5Meb451rQ42vwdps1LljmK2XeBVa0jZytE4Ayl6B2C2cSK1Jz0582BbFd64SvrVO0bZMBJ2ilOVH1mSDfR2emb320CGaKz4PvDv13GnIsr3Jc6tC1FU4Px0nj01y24v1df0ral4M0dWVhV03jINe2T8hQf0aUrNC3nowiy45nVVS4d1Yqc08BeeK4WAW0d3CIfM72tn5Ym2tdv3h0zlPaJ2doZp63qa4uT2XWEmY1OJKEO28It8J2ke2AV03k3VN0gGAJY3pn4tI01gWee4Ojo5B41yXNs3JZ8Ts265QJ00Zwclq4Z0o4549ZUgN4ZcojH2IrjEk0ElTja2l3wZU02PAlW1xzkpV2mcvTu38oepn2SfHCj4crFIV27ilfc0O2Luc4Ixvyr1hIgXC1XvWbf3Jb0RK3GhNFR0NAp6j25gnAj1X1MKZ0YMGAY4XxYkU2IWvBH31izTV4AZK6f42lqXH4Ngf0N3yhzBs2wlvII3nUWcN09IFj62WWNfl4XR8RE3RKGlW0FgrBy3ei6wi0tR5aZ3yRAGE22Ff0h0y2FCQ45RP3B17HkpC2kyLFf4TsO0A4AoL2z3uQTPL4ejGqE34RNkA0ikIG73AchaR0S7zpD3qTrh41p5fLx0LGHBB2PIaxC2VVGRw0KWoJX4I9sLR22ee2R28xIX508zDwL4MPsoI0SrLnF2e38OX1KIcgj2hfrdY0DOJYy42DXVb0Y5Hpj3evNpM3dU8gT3GLJbu3eO8tV4GEDMl3sCiak0TYjVF3hOFJQ13P3qs16aAwv1k2n413Hbcq23681a43XXrU20cG0dp1X9skp2tpEgF1ISEvm1HdmZW2675aL0OH5aP4c0zeH0WpFJP3CVaxC3To1Fv0ZyCK61oR2xM09R8Gc25gh5Q4YT9co06BHrd1W2vXn2rBzuH3UsTZA396oAI23LlWd0cJzqw0J8eBi1nPrQP3LN0932hHkMg3E5F4k0b1MTJ0dM06y4WHezk2VaHOv3yWgUF0cqyIS16UOHK1Xd2mv4fjzKO0MXFSh"

    simple_sample_script = "DSC7h2aG6ae1BX2uH1D6tqS1t5pjg0NibnM2eMJHl2AbaLj15J95Y3NAyL53KNBPI1oRarX02p8cc21J6z74boEtP4g4tXY4VjBfk2LaqZB4Ty2UF0CvQHa4e2SH125IoTe1LoZau2bqzbY3iC9XK3HyTFS1XF9d72Jjhip23onu84c4cZ014ZhuQ4fwaVX2MCq5531qVz33k1MiC0k2w360srPDh1X62Ra3cKNjX1d8RzS0QnuPM3gHMIv0EnzGJ0VYins1EY11J29mH5T2uwhxQ36Iyx5143Cvj07v68s1kF3UPW"
    # as_dict = get_dict_from_desynced_str(complex_sample_script)
    as_dict = as_dict_complex




if __name__ == "__main__":
    main()
