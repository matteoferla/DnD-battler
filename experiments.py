__author__ = 'Matteo'
__doc__ = """
The reason why I wrote the script was to run some tests.
"""

N = "\n"
T = "\t"
# N="<br/>"

import DnD_battler, csv


def cr_appraisal(party):
    """
    Assess the victory probability of each monster in the manual against Creatures in the `party` Encounter
    :param party: a list of creatures
    :return:
    """
    # set to same team
    for pc in party:
        pc.alignment = "players"
    out = csv.DictWriter(open("CR stats.csv", 'w', newline=''),
                         fieldnames=['beast', 'victory'])  # DnD_battler.Encounter().json() is overkill and messy
    out.writeheader()
    # challenge each monster
    for beastname in DnD_battler.Creature.beastiary:
        beast = DnD_battler.Creature.load(beastname)
        beast.alignment = "opponent"
        party.append(beast)  # seems a bit wrong, but everything gets hard reset
        party.go_to_war(100)
        print(beastname + ": " + str(party.tally['victories']['players']) + "%")
        out.writerow({'beast': beastname, 'victory': party.tally['victories']['players']})
        party.remove(beast)  # will perform a hard reset by default



def dice_variance(d):
        return sum([sum([(i+1-(d2+1)/2)**2 for i in range(d2)])/d2 for d2 in d.num_faces])

if __name__ == "__main__":
    # cr_appraisal(DnD_battler.Encounter('my druid','my barbarian','mega_tank', "netsharpshooter"))
    commoner_brawl()
    #print(dice_variance(DnD_battler.Dice(0, num_faces=[100], role="damage")))
