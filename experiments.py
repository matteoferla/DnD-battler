__author__ = 'Matteo'
__doc__ = """
The reason why I wrote the script was to run some tests.
"""

N = "\n"
T = "\t"
# N="<br/>"

import DnD, csv

def cr_appraisal(party):
    """
    Assess the victory probability of each monster in the manual against Creatures in the `party` Encounter
    :param party: a list of creatures
    :return:
    """
    #set to same team
    for pc in party:
        pc.alignment = "players"
    out = csv.DictWriter(open("CR stats.csv",'w',newline=''),fieldnames=['beast','victory']) #DnD.Encounter().json() is overkill and messy
    out.writeheader()
    #challenge each monster
    for beastname in DnD.Creature.beastiary:
        beast=DnD.Creature(beastname)
        beast.alignment = "opponent"
        party.append(beast)  #seems a bit wrong, but everything gets hard reset
        party.go_to_war(100)
        print(beastname+": "+str(party.tally['victories']['players'])+"%")
        out.writerow({'beast': beast, 'victory': party.tally['victories']['players']})
        party.remove(beast)  # will perform a hard reset by default








if __name__ == "__main__":
    cr_appraisal(DnD.Encounter('my druid','my barbarian','mega_tank', "netsharpshooter"))