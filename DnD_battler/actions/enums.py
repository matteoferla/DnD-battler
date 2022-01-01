from enum import Enum

class AttackType(Enum):
    # I hate uppercase Enum convension.
    melee = 1
    ranged = 2
    target_spell = 3
    aoe_spell = 4

combinations = {}
for team, t in {'any': 0, 'enemy': -1, 'ally': +1}.items():
    for state, s in {'schrondinger': 0, 'alive': +1, 'dead': -1}.items():
        for r, rank in enumerate(('weakest', 'random', 'fiersomest')):
            combinations[f'{team}_{state}_{rank}'] = (t,s,r)
TargetChoice = Enum('TargetChoice', combinations)