from ..victory import Victory
from ._adv_base import CreatureAdvBase

class CreatureAction(CreatureAdvBase):

    def ready(self):
        self.dodge = 0
        # there should be a few more.
        # conditions.

    def isalive(self):
        if self.hp > 0:
            return True

    def take_damage(self, points, verbose=0):
        self.hp -= points
        if verbose:
            print(self.name + ' took ' + str(points) + ' of damage. Now on ' + str(self.hp) + ' hp.')
        if self.concentrating:
            dc = points / 2
            if dc < 10: dc = 10
            if self[self.spellcasting_ability_name].roll() < dc:
                self.conc_fx()
                if verbose:
                    print(self.name + ' has lost their concentration')

    def reset(self, hard=False):
        """
        Resets the creature back to health (a long rest). a hard reset resets its scores
        :param hard: bool, false keeps tallies
        :return: None
        """
        self.hp = self.starting_hp
        if self.concentrating:
            self.conc_fx()  # TODO this looks fishy
        self.healing_spells = self.starting_healing_spells
        if hard:
            self.tally = {'damage': 0, 'hp': 0, 'hits': 0, 'misses': 0, 'rounds': 0, 'healing_spells': 0, 'battles': 0,
                          'dead': 0}

    def check_advantage(self, opponent):
        adv = 0
        if opponent.dodge:
            adv += -1
        if (opponent.condition == 'netted') or (opponent.condition == 'restrained'):
            adv += 1
        # Per coding it is impossible that a netted creature attempts an attack.
        if (self.condition == 'netted') or (self.condition == 'restrained'):
            adv += -1
        return adv

    def net(self, opponent, verbose=0):
        self.alt_attack['attack'].advantage = self.check_advantage(opponent)
        if self.alt_attack['attack'].roll(verbose) >= opponent.armor.ac:
            opponent.condition = 'netted'
            self.tally['hits'] += 1
            if verbose:
                print(self.name + " netted " + opponent.name)
        else:
            self.tally['misses'] += 1

    def cast_barkskin(self):
        if self.concentrating == 0:
            self.temp = self.armor.ac
            self.armor.ac = 16
            self.concentrating = 1
        elif self.concentrating == 1:
            self.armor.ac = self.temp
            self.concentrating = 0

    def cast_nothing(self, state='activate'):  # Something isn't quite right if this is invoked.
        pass

    def heal(self, points, verbose=0):
        self.hp += points
        if verbose:
            print(self.name + ' was healed by ' + str(points) + '. Now on ' + str(self.hp) + ' hp.')

    def assess_wounded(self, verbose=0):
        targets = self.arena.find('bloodiest allies')
        if len(targets) > 0:
            weakling = targets[0]
            if weakling.starting_hp > (self.healing.num_faces[0] + self.healing.bonus + weakling.hp):
                if verbose:
                    print(self.name + " wants to heal " + weakling.name)
                return weakling
            else:
                return 0
        else:
            raise ValueError('A dead man wants to heal folk')

    def cast_healing(self, weakling, verbose=0):
        if self.healing_spells > 0:
            weakling.heal(self.healing.roll(), verbose)
            self.healing_spells -= 1

    def multiattack(self, verbose=0, assess=0):
        if assess:
            return 0  # the default
        for i in range(len(self.attacks)):
            try:
                opponent = self.arena.find(self.arena.target, self)[0]
            except IndexError:
                raise Victory()
            self.log.debug(f"{self.name} attacks {opponent.name} with {self.attacks[i].name}")
            # This was the hit method. put here for now.
            damage = self.attacks[i].attack(opponent.armor.ac, advantage=self.check_advantage(opponent))
            if damage > 0:
                opponent.take_damage(damage, verbose)
                self.tally['damage'] += damage
                self.tally['hits'] += 1
            else:
                self.tally['misses'] += 1

    # TODO
    def check_action(self, action, verbose):
        return getattr(self, action)(assess=1)

    # TODO
    def do_action(self, action, verbose):
        # do it.
        pass

    # TODO
    def TBA_act(self, verbose=0):
        if not self.arena.find('alive enemy'):
            raise Victory()
        x = {'nothing': 'cast_nothing'}
        choice = [self.check_action(x) for x in self.actions]
        best = sorted(choice.keys(), key=choice.get)[0]
        self.do_action(best)

    def act(self, verbose=0):
        if not self.arena.find('alive enemy'):
            raise Victory()
        # BONUS ACTION
        # heal  -healing word, a bonus action.
        if self.healing_spells > 0:
            weakling = self.assess_wounded(verbose)
            if weakling != 0:
                self.cast_healing(weakling, verbose)
        # Main action!
        economy = len(self.arena.find('allies')) > len(self.arena.find('opponents')) > 0
        # Buff?
        if self.condition == 'netted':
            # NOT-RAW: DC10 strength check or something equally easy for monsters
            if verbose:
                print(self.name + " freed himself from a net")
            self.condition = 'normal'
        elif self.buff_spells > 0 and self.concentrating == 0:
            self.conc_fx()
            if verbose:
                print(self.name + ' buffs up!')
            # greater action economy: waste opponent's turn.
        elif economy and self is self.arena.find('weakest allies')[0]:
            if verbose:
                print(self.name + " is dodging")
            self.dodge = 1
        elif economy and self.alt_attack['name'] == 'net':
            opponent = self.arena.find('fiersomest enemy alive', self)[0]
            if opponent.condition != 'netted':
                self.net(opponent, verbose)
            else:
                self.multiattack(verbose)
        else:
            self.multiattack(verbose)
