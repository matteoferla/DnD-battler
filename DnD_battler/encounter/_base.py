from ..creature import Creature
from typing import *
from ..log import log
import json

class EncounterBase:
    log = log
    target = 'enemy alive weakest'
    # target='enemy alive weakest', target='enemy alive random', target='enemy alive fiersomest'

    def __init__(self, *lineup):
        """
        :param lineup: Creatures in arena
        """
        self.tally = {'rounds': 0, 'battles': 0, 'perfect': None, 'close': None, 'victories': None}
        self.active = None
        self.name = 'Encounter'
        self.masterlog = []
        self.note = ''
        self.combattants : List[Creature] = []
        for chap in lineup:
            self.append(chap)

    def blank(self, hard=True):
        # this resets the teams
        self.sides = set([dude.alignment for dude in self])
        self.tally['battles'] = 0
        self.tally['rounds'] = 0
        self.tally['perfect'] = {side: 0 for side in self.sides}
        self.tally['close'] = {side: 0 for side in self.sides}
        self.tally['victories'] = {side: 0 for side in self.sides}
        self.reset(hard)

    def reset(self, hard=False):
        for schmuck in self.combattants:
            schmuck.reset(hard)
        return self

    def __iter__(self):
        return iter(self.combattants)

    def append(self, newbie: Union[Creature, str]):
        if isinstance(newbie, str):
            newbie = Creature.load(newbie)
        if isinstance(newbie, dict):
            newbie = Creature(**newbie)
        self.combattants.append(newbie)
        newbie.arena = self
        self.blank()

    def extend(self, iterable):
        for x in iterable:
            self.append(x)
        return self

    def __str__(self):
        """
        The former verbose code is in describe
        """
        return f'Encounter {self.name} featuring {[str(com) for com in self.combattants]}'

    def describe(self, html_formatting:bool=False) -> str:
        badgify = lambda i: f'<span class="badge">{i}</span>'
        if html_formatting:
            # it is bootstrap 3 in Jupyter notebook, but with jupyter themes it looks weird.
            # class="list-group" and class="list-group-item"
            _listitemiser = lambda item: f'<li>{item}</li>'
            listify = lambda items: f'<ul>{"".join(map(_listitemiser, items))}</ul>'
        else:
            listify = lambda items: ''.join([str(item) + '\n' for item in items])

        # ## Title
        if html_formatting:
            text = f'<h3>{self.name}</h3>'
        else:
            text = "=" * 50 + ' ' + self.name + " " + "=" * 50 + '\n'

        # ## Prediction
        text += self.predict(html_formatting=html_formatting)
        if html_formatting:
            text += '<hr>'
        else:
            text += "-" * 110 + '\n'

        # ## Battles
        if html_formatting:
            text += f'<span class="label label-primary">Battles {badgify(self.tally["battles"])}</span>'
            text += f'&nbsp;'
            text += f'<span class="label label-default">Sum of rounds {badgify(self.tally["rounds"])}</span>'
            text += f'<span>{self.note}</span>'
        else:
            text += "Battles: " + str(self.tally['battles']) + "; Sum of rounds: " + str(
                self.tally['rounds']) + "; " + self.note + '\n'

        # ## Team summary
        teams = []
        for side in self.sides:
            if html_formatting:
                teams.append(f'<b>Team {side}</b> ' +
                             f'<span>winning battles {badgify(self.tally["victories"][side])}</span> ' +
                             f'<span>perfect battles {badgify(self.tally["perfect"][side])}</span> ' +
                             f'<span>close-call battles {badgify(self.tally["close"][side])}</span> ')
            else:
                teams.append("> Team " + str(side) +
                             " = winning battles: " +
                             str(self.tally['victories'][side]) +
                             "; perfect battles: " +
                             str(self.tally['perfect'][side]) +
                             "; close-call battles: " +
                             str(self.tally['close'][side]) +
                             ";\n")
        if html_formatting:
            text += listify(teams)
        else:
            text += ''.join(teams)+'\n'

        # ## Combatants
        # Fighter is a D&D class. Combatant is a fighter. while combattant is a herandry term
        # this will need to be fixed TODO Combattant --> Combatant
        if html_formatting:
            text += f'<h4>Combatants</h3>'
        else:
            text += "-" * 49 + " Combatants  " + "-" * 48 + '\n'
        text += listify(map(str, self.combattants))
        # ## Done
        return text

    def _repr_html_(self):
        return self.describe(html_formatting=True)

    def json(self):
        jsdic = {"prediction": self.predict(),
                 "battles": self.tally['battles'],
                 "rounds": self.tally['rounds'],
                 "notes": self.note,
                 "team_names": list(self.sides),
                 "team_victories": [self.tally['victories'][x] for x in list(self.sides)],
                 "team_perfects": [self.tally['perfect'][x] for x in list(self.sides)],
                 "team_close": [self.tally['close'][x] for x in list(self.sides)],
                 "combattant_names": [x.name for x in self.combattants],
                 "combattant_alignments": [x.alignment for x in self.combattants],
                 "combattant_damage_avg": [x.tally['damage'] / self.tally['battles'] for x in self.combattants],
                 "combattant_hit_avg": [x.tally['hits'] / self.tally['battles'] for x in self.combattants],
                 "combattant_miss_avg": [x.tally['misses'] / self.tally['battles'] for x in self.combattants],
                 "combattant_rounds": [x.tally['rounds'] / self.tally['rounds'] for x in self.combattants],
                 "sample_encounter": '\n'.join(self.masterlog)
                 }
        return json.dumps(jsdic)

    def __len__(self):
        return len(self.combattants)

    def __add__(self, other):
        if type(other) is str:
            self.append(Creature(other))
        elif type(other) is Creature:
            self.append(other)
        elif type(other).__name__ == 'Encounter':  # not declared yet
            self.extend(other.combattants)
        else:
            raise TypeError('Unsupported type ' + str(type(other)))

    def __getitem__(self, item):
        for character in self:
            if character.name == item:
                return character
        raise Exception('Nobody by this name')

    def __delitem__(self, moriturus:Union[str, Creature]):
        self.remove(moriturus)

    def remove(self, moriturus):
        """
        Removes a creature and resets and rechecks
        :param moriturus: The creature name to be dropped
        :return: self
        """
        if type(moriturus) is str:
            for chap in self.combattants:
                if chap.name == moriturus:
                    self.combattants.remove(chap)
                    break
            else:
                raise ValueError(
                    moriturus + ' not found in Encounter among ' + "; ".join([chap.name for chap in self.combattants]))
        elif type(moriturus) is Creature:
            self.combattants.remove(moriturus)
        self.blank()

