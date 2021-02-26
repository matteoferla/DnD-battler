
class Encounter:
    """
    The encounter class is the arena.
    In a dimentionless model, move action and the main actions dash, disengage, hide, shove back/aside, tumble and overrun are meaningless.
    weapon attack —default
    two-weapon attack —
        Good when the opponent has low AC (<12) if 2nd attack is without proficiency.
        Stacks with bonuses such as sneak attack or poisoned weapons —neither are in the model.
        Due to the 1 action for donning/doffing a shield, switch to two handed is valid for unshielded folk only.
        Best keep two weapon fighting as a prebuild not a combat switch.
    AoE spell attack — Layout…
    targetted spell attack —produce flame is a cantrip so could be written up as a weapon. The bigger ones. Spell slots need to be re-written.
    spell buff —Barkskin is a druidic imperative. Haste? Too much complication.
    spell debuff —Bane…
    dodge —targetted and turn economy
    help —high AC target (>18), turn economy, beefcake ally
    ready —teamwork preplanning. No way.
    grapple/climb —very situational. grapple/shove combo or barring somatic.
    disarm —disarm… grey rules about whether picking it up or kicking it away is an interact/move/bonus/main action.
        netting is a better option albeit a build.
    called shot —not an official rule. Turn economy.
    """

    def __init__(self, *lineup):
        # print(lineup)
        # self.lineup={x.name:x for x in lineup}
        # self.lineup = list(lineup)  #Classic fuck-up
        self.KILL = False  # needed for code.
        self.tally = {'rounds': 0, 'battles': 0, 'perfect': None, 'close': None, 'victories': None}
        self.active = None
        self.name = 'Encounter'
        self.masterlog = []
        self.note = ''
        self.combattants = []
        for chap in lineup:
            self.append(chap)
        self.blank()

    def blank(self, hard=True):
        # this resets the teams
        self.sides = set([dude.alignment for dude in self])
        self.tally['battles'] = 0
        self.tally['rounds'] = 0
        self.tally['perfect'] = {side: 0 for side in self.sides}
        self.tally['close'] = {side: 0 for side in self.sides}
        self.tally['victories'] = {side: 0 for side in self.sides}
        self.reset(hard)

    def append(self, newbie):
        if not type(newbie) is Creature:
            newbie = Creature(newbie)  # Is this safe??
        self.combattants.append(newbie)
        newbie.arena = self
        self.blank()

    def extend(self, iterable):
        for x in iterable:
            self.append(x)
        return self

    def addmob(self, n):
        """
        Adds _n_ commoners to the battle
        :param n: number of commoners
        :return: self
        """
        for x in range(int(n)):
            self.append("commoner")
        return self

    def __str__(self):
        string = "=" * 50 + ' ' + self.name + " " + "=" * 50 + N
        string += self.predict()
        string += "-" * 110 + N
        string += "Battles: " + str(self.tally['battles']) + "; Sum of rounds: " + str(
            self.tally['rounds']) + "; " + self.note + N
        for s in self.sides:
            string += "> Team " + str(s) + " = winning battles: " + str(
                self.tally['victories'][s]) + "; perfect battles: " + str(
                self.tally['perfect'][s]) + "; close-call battles: " + str(self.tally['close'][s]) + ";\n"
        string += "-" * 49 + " Combattants  " + "-" * 48 + N
        for fighter in self.combattants: string += str(fighter) + N
        return string

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
                 "sample_encounter": N.join(self.masterlog)
                 }
        return json.dumps(jsdic)

    def __len__(self):
        return len(self.combattants)

    def __add__(self, other):
        if type(other) is str:
            self.append(Creature(other))
        elif type(other) is Creature:
            self.append(other)
        elif type(other) is Encounter:
            self.extend(other.combattants)
        else:
            raise TypeError('Unsupported type ' + str(type(other)))

    def __iter__(self):
        return iter(self.combattants)

    def __getitem__(self, item):
        for character in self:
            if character.name == item:
                return character
        raise Exception('Nobody by this name')

    def reset(self, hard=False):
        for schmuck in self.combattants:
            schmuck.reset(hard)
        return self

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

    def set_deathmatch(self):
        colours = 'red blue green orange yellow lime cyan violet ultraviolet pink brown black white octarine teal magenta blue-green fuchsia purple cream grey'.split(
            ' ')
        for schmuck in self:
            schmuck.alignment = colours.pop(0) + " team"
        return self

    def roll_for_initiative(self, verbose=0):
        self.combattants = sorted(self.combattants, key=lambda fighter: fighter.initiative.roll())
        if verbose:
            verbose.append("Turn order:")
            verbose.append(str([x.name for x in self]))

    def predict(self):
        def safediv(a, b, default=0):
            try:
                return a / b
            except:
                return default

        def not_us(side):
            (a, b) = list(self.sides)
            if a == side:
                return b
            else:
                return a

        if len(self.sides) != 2:
            # print('Calculations unavailable for more than 2 teams')
            return "Prediction unavailable for more than 2 teams"
        t_ac = {x: [] for x in self.sides}
        for character in self:
            t_ac[character.alignment].append(character.ac)
        ac = {x: sum(t_ac[x]) / len(t_ac[x]) for x in t_ac.keys()}
        damage = {x: 0 for x in self.sides}
        hp = {x: 0 for x in self.sides}
        for character in self:
            for move in character.attacks:
                move['damage'].avg = True
                damage[character.alignment] += safediv((20 + move['attack'].bonus - ac[not_us(character.alignment)]),
                                                       20 * move['damage'].roll())
                move['damage'].avg = False
                hp[character.alignment] += character.starting_hp
        (a, b) = list(self.sides)
        rate = {a: safediv(hp[a], damage[b], 0.0), b: safediv(hp[b], damage[a], 0.0)}
        return ('Rough a priori predictions:' + N +
                '> ' + str(a) + '= expected rounds to survive: ' + str(
                    round(rate[a], 2)) + '; crudely normalised: ' + str(
                    round(safediv(rate[a], (rate[a] + rate[b]) * 100))) + '%' + N +
                '> ' + str(b) + '= expected rounds to survive: ' + str(
                    round(rate[b], 2)) + '; crudely normalised: ' + str(
                    round(safediv(rate[b], (rate[a] + rate[b]) * 100))) + '%' + N)

    def battle(self, reset=1, verbose=1):
        if verbose: self.masterlog.append('==NEW BATTLE==')
        self.tally['battles'] += 1
        if reset: self.reset()
        for schmuck in self: schmuck.tally['battles'] += 1
        self.roll_for_initiative(self.masterlog)
        while True:
            try:
                if verbose: self.masterlog.append('**NEW ROUND**')
                self.tally['rounds'] += 1
                for character in self:
                    character.ready()
                    if character.isalive():
                        self.active = character
                        character.tally['rounds'] += 1
                        character.act(self.masterlog)
                    else:
                        character.tally['dead'] += 1
            except Encounter.Victory:
                break
        # closing up maths
        side = self.active.alignment
        team = self.find('allies')
        self.tally['victories'][side] += 1
        perfect = 1
        close = 0
        for x in team:
            if x.hp < x.starting_hp:
                perfect = 0
            if x.hp < 0:
                close = 1
        if not perfect:
            self.tally['perfect'][side] += perfect
        self.tally['close'][side] += close
        for character in self:
            character.tally['hp'] += character.hp
            character.tally['healing_spells'] += character.healing_spells
        if verbose: self.masterlog.append(str(self))
        # return self or side?
        return self

    def go_to_war(self, rounds=1000):
        for i in range(rounds):
            # print(i,self.KILL)
            self.battle(1, 0)
            if self.KILL == True:
                break
        x = {y: self.tally['victories'][y] for y in self.sides}
        se = {}
        for i in list(x):
            x[i] /= rounds
            try:
                se[i] = math.sqrt(x[i] * (1 - x[i]) / rounds)
            except Exception:
                se[i] = "NA"
        self.reset()
        for i in list(x):
            try:
                self.note += str(i) + ': ' + str(round(float(x[i]), 2)) + ' ± ' + str(round(float(se[i]), 2)) + '; '
            except:
                self.note += str(i) + ': ' + str(x[i]) + ' ± ' + str(se[i]) + '; '
        return self

    def find(self, what, searcher=None, team=None):

        def _enemies(folk):
            return [query for query in folk if (query.alignment != team)]

        def _allies(folk):
            return [query for query in folk if (query.alignment == team)]

        def _alive(folk):
            return [query for query in folk if (query.hp > 0)]

        def _normal(folk):
            return [joe for joe in folk if joe.condition == 'normal']

        def _random(folk):
            random.shuffle(folk)
            return folk

        def _weakest(folk):
            return sorted(folk, key=lambda query: query.hp)

        def _bloodiest(folk):
            return sorted(folk, key=lambda query: query.hp - query.starting_hp)

        def _fiersomest(folk):
            return sorted(folk, key=lambda query: query.hurtful, reverse=True)

        def _opponents(folk):
            return _alive(_enemies(folk))

        searcher = searcher or self.active
        team = team or searcher.alignment
        folk = self.combattants
        agenda = list(what.split())
        opt = {
            'enemies': _enemies,
            'enemy': _enemies,
            'opponents': _opponents,
            'allies': _allies,
            'ally': _allies,
            'normal': _normal,
            'alive': _alive,
            'fiersomest': _fiersomest,
            'weakest': _weakest,
            'random': _random,
            'bloodiest': _bloodiest
        }
        for cmd in list(agenda):  # copy it.
            if folk == None:
                folk = []
            for o in opt:
                if (cmd == o):
                    folk = opt[o](folk)
                    agenda.remove(cmd)
        if agenda:
            raise Exception(str(cmd) + ' field not found')
        return folk