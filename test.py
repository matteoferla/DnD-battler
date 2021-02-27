import unittest
import numpy as np
from DnD import Dice, AbilityDie, AttackRoll
from DnD import Creature

class DiceTester(unittest.TestCase):

    def dice_variance(self, d):
        a = np.array(list(map(d.roll, range(100_000))))
        return a.mean()

    def test_notation(self):
        notation = '2d6+3'
        dice = Dice.from_notation(notation)
        self.assertEqual(notation, str(dice))
        self.assertEqual(3, dice.bonus)
        self.assertEqual(6, dice.num_faces[0])
        self.assertIsInstance(dice.roll(), int)

    def test_averaged(self):
        d = Dice(num_faces=[100])
        self.assertAlmostEqual(self.dice_variance(d), d.mean(), 0)

    def test_crit(self):
        able = AbilityDie()
        self.assertEqual(float('inf'), max([able.roll(success_on_crit=True) for i in range(100)]))
        self.assertNotEqual(float('inf'), max([able.roll(success_on_crit=False) for i in range(100)]))

    def test_advantage(self):
        able = AbilityDie()
        damage = Dice(num_faces=[8])
        attack = AttackRoll('rolling pin', able, damage)
        self.assertAlmostEqual(1/20, sum([attack.roll(advantage=0) == 10 for i in range(10000)]) / 10000, 1)
        self.assertLess(1/20, sum([attack.roll(advantage=-1) == 5 for i in range(10000)]) / 10000)
        self.assertGreater(1 / 20, sum([attack.roll(advantage=1) == 5 for i in range(10000)]) / 10000)


class CreatureTester(unittest.TestCase):

    def test_commoner(self):
        commoner = Creature.load('commoner')
        self.assertEqual(0, commoner.str.bonus, 'wrong str bonus')
        self.assertEqual(10, commoner.str.score, 'wrong str score')

    def test_jacked_commoner(self):
        beefcake = Creature.load(creature_name="commoner", name='beefcake', alignment='chaotic', str=20)
        self.assertEqual(20, beefcake.str.score, 'wrong str score')
        self.assertEqual(5, beefcake.str.bonus, 'wrong str bonus')
        self.assertEqual(1, beefcake.level)
        beefcake.set_level(10)
        self.assertEqual(4, beefcake.proficiency.bonus)

    def test_dragon(self):
        dragon = Creature.load('adult red dragon')
        self.assertEqual(27, dragon.str.score)


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