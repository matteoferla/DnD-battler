import unittest
import numpy as np
from DnD_battler import Dice, AbilityDie, AttackRoll, Creature, log, Encounter

log.handlers[0].setLevel(20)


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
        self.assertAlmostEqual(1 / 20, sum([attack.roll(advantage=0) == 10 for i in range(10000)]) / 10000, 1)
        self.assertLess(1 / 20, sum([attack.roll(advantage=-1) == 5 for i in range(10000)]) / 10000)
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
        beefcake.ac = 20
        self.assertEqual(20, beefcake.ac)
        self.assertEqual(4, beefcake.proficiency.bonus)

    def test_dragon(self):
        dragon = Creature.load('adult red dragon')
        self.assertEqual(27, dragon.str.score)


class EncounterTester(unittest.TestCase):
    def test_rat_vs_commoner(self):
        log.handlers[0].setLevel(20)
        commoner = Creature.load(creature_name='commoner', alignment='Red team')
        rat = Creature.load(creature_name='giant rat', alignment='Blue team')
        arena = Encounter(commoner, rat)
        arena.go_to_war(10)
        self.assertLess(8, arena.tally['victories']['Blue team'])

    def test_weapon_equivalence(self):
        log.handlers[0].setLevel(20)
        tester = Creature.load(creature_name='bandit', alignment='tester team')
        target = Creature.load(creature_name='bandit', alignment='target team')
        arena = Encounter(tester, target)
        log.info(tester.attacks[0].damage_dice.mean())
        for damage_die in [Dice(num_faces=[2], bonus=3),
                           Dice(num_faces=[4], bonus=2),
                           Dice(num_faces=[6], bonus=1),
                           Dice(num_faces=[8], bonus=0),
                           Dice(num_faces=[10], bonus=-1),
                           Dice(num_faces=[2, 2, 2], bonus=0),
                           Dice(num_faces=[3, 2], bonus=1),
                           Dice(num_faces=[4, 3], bonus=0),
                           Dice(num_faces=[5, 4], bonus=-1),]:
            tester.attacks[0].damage_die = damage_die
            arena.go_to_war(5000)
            a = arena.tally["victories"]["tester team"]
            b = arena.tally["victories"]["target team"]
            log.info(f'{damage_die.num_faces} {damage_die.mean()} {a/b*100}%')
            self.assertAlmostEqual(a/5000, b/5000, 1)
            arena.reset(hard=True)

    def test_brawl(self):
        # commoners brawling...
        n = 100
        achilles = Creature.load(creature_name='commoner', name="Achilles", alignment='Achaeans')
        patrocles = Creature.load(creature_name='commoner', name="Patrocles", alignment='Achaeans')
        hector = Creature.load(creature_name='commoner', name="Hector", alignment='Trojans')
        priam = Creature.load(creature_name='commoner', name="Priam", alignment='Trojans')
        self.assertEqual([4], achilles.attacks[0].damage_dice.num_faces)  # club.
        log.info(achilles.attacks[0].damage_dice.mean())
        #log.info(f'{damage_die.num_faces} {damage_die.mean()}')
            # print(d, T, T.join(
            #     [str(Encounter(*party).go_to_war(n).tally['victories']['Achaeans']) for party in
            #      [(achilles, hector), (achilles, ratty), (achilles, patrocles, ratty),
            #       (achilles, patrocles, ratty, rattie)]]))


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
