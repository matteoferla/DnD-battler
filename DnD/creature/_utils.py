from ._base import CreatureBase
from typing import *

class CreatureUtils(CreatureBase):

    def generate_character_sheet(self) -> str:
        """
        An markdown character sheet.
        
        :return: a string
        """
        rows = ['# ' + self.name.upper()]
        rows.append(self._makeline('Name', self.name))
        rows.append(self._makeline('Alignment', self.alignment))
        if self.cr:
            level = self.cr
            lname = 'CR'
        else:
            level = self.level
            lname = 'Level'
        if self.hd:
            rows.append(self._makeline(lname + ' (hit dice)', level, self.hd))
        else:
            rows.append(self._makeline(lname, level))
        if self.xp:
            rows.append(self._makeline('XP', self.xp))
        rows.append('## Abilities')
        for ab in self.ability_names:
            rows.append(self._makeline(ab, self[ab].score, self[ab].bonus))
        rows.append('## Combat')
        rows.append(self._makeline('Hit points (hp total)', self.hp, self.starting_hp))
        rows.append(self._makeline('Condition', self.condition))
        rows.append(self._makeline('Initiative', self.initiative))
        rows.append(self._makeline('Proficiency', self.proficiency))
        rows.append(self._makeline('Armour class', self.ac))
        rows.append('### Attacks')
        rows.append(self._makeline('Potential average damage per turn', self.hurtful))
        for d in self.attacks:
            rows.append("* " + self._makeline(d['name'], d['attack'], d['damage']))
        rows.append('### Raw data')
        rows.append(str(self.__dict__).replace('<br/>', '\n'))
        return '\n'.join(rows)
    
    def _makeline(self, field: str, value: Any, secvalue: Optional[Any]=None) -> str:
        """
        dependent method for generate_character_sheet only.
        returns _field_: value (secvalue)
        secvalues is if has a secondary value to be added in brachets
        """
        if secvalue is None:
            return '_' + str(field).replace("_", " ") + '_: ' + str(value)
        else: # secondary value.
            return '_' + str(field).replace("_", " ") + '_: ' + str(value) + ' (' + str(secvalue) + ')'


    def __str__(self):
        if self.tally['battles']:
            battles = self.tally['battles']
            return self.name + ": {team=" + self.alignment + "; avg hp=" + str(
                self.tally['hp'] / battles) + " (from " + str(
                self.starting_hp) + "); avg healing spells left=" + str(
                self.tally['healing_spells'] / battles) + " (from " + str(
                self.starting_healing_spells) + "); damage done (per battle average)= " + str(
                self.tally['damage'] / battles) + "; hits/misses (PBA)= " + str(
                self.tally['hits'] / battles) + "/" + str(
                self.tally['misses'] / battles) + "; rounds (PBA)=" + str(
                self.tally['rounds'] / battles) + ";}"
        else:
            return self.name + ": UNTESTED IN BATTLE"