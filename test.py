import unittest
import numpy as np
from DnD import Dice
from DnD import Creature

class DiceTester(unittest.TestCase):

    def dice_variance(self, d):
        a = np.array(list(map(d.roll, range(100_000))))
        return a.mean()

    def test_notation(self):
        notation = '2d6+3'
        dice = Dice.from_notation(notation)
        self.assertEqual(str(dice), notation)
        self.assertEqual(3, dice.bonus)
        self.assertEqual(dice.num_faces[0], 6)
        self.assertIsInstance(dice.roll(), int)

    def test_averaged(self):
        d = Dice(num_faces=[100], role="damage")
        self.assertAlmostEqual(self.dice_variance(d), d.mean(), 0)




########### Junk methods #####

def tarrasquicide():
    print('Test module...of sorts: 128 commoners can kill a tarrasque')
    print('how many commoners are needed to kill a tarasque')
    ted = Creature("tarrasque")
    print(ted)
    wwe = Encounter(ted, "commoner", "commoner").battle(1, 1)

    print(wwe.masterlog)
    max = 1
    while not wwe.tally['victories']['good']:
        max *= 2
        x = ["commoner" for x in range(int(max))]
        wwe.extend(x).battle(1, 0)
        wwe.tally['victories']['good']
        print(str(int(max)) + " commoners: " + str(wwe.tally['victories']['good']))
        print(ted.hp)


def creature_check(who='commoner'):
    """
    Dev test area. Prints the abilities of a given creature from the beastiary to see if all is okay.
    :param who: name
    :return: None
    """
    print('Ability bonus...')
    print('Beastiary: ', {x: Creature.beastiary[who][x] for x in 'AB_Str AB_Int AB_Con AB_Cha AB_Dex AB_Wis'.split()})
    print('Instance: ', Creature(who).ability_bonuses)
    print('Mod: ', Creature(who, str=999).ability_bonuses)