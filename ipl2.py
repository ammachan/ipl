import copy
import operator

CURRENT_MATCH = 39


class Team:
    CSK = "CSK"
    SRH = "SRH"
    RCB = "RCB"
    MI = "MI"
    KXIP = "KXIP"
    DD = "DD"
    KKR = "KKR"
    RR = "RR"


class Constants:
    MAX_FIXTURE = 56

    points = {Team.CSK: 14,
              Team.SRH: 14,
              Team.RCB: 6,
              Team.MI: 8,
              Team.KXIP: 12,
              Team.DD: 6,
              Team.KKR: 10,
              Team.RR: 6}

    nrr = {Team.CSK: 0.421,
           Team.SRH: 0.471,
           Team.RCB: -0.376,
           Team.MI: 0.070,
           Team.KXIP: 0.198,
           Team.DD: -0.411,
           Team.KKR: 0.145,
           Team.RR: -0.726}

    adjusted_points = {}

    for team in points.keys():
        adjusted_points[team] = points[team] + nrr[team] / 10

    fixture = {35: (Team.CSK, Team.RCB),
               36: (Team.SRH, Team.DD),
               37: (Team.MI, Team.KKR),
               38: (Team.KXIP, Team.RR),
               39: (Team.SRH, Team.RCB),
               40: (Team.RR, Team.KXIP),
               41: (Team.KKR, Team.MI),
               42: (Team.DD, Team.SRH),
               43: (Team.RR, Team.CSK),
               44: (Team.KXIP, Team.KKR),
               45: (Team.DD, Team.RCB),
               46: (Team.CSK, Team.SRH),
               47: (Team.MI, Team.RR),
               48: (Team.KXIP, Team.RCB),
               49: (Team.KKR, Team.RR),
               50: (Team.MI, Team.KXIP),
               51: (Team.RCB, Team.SRH),
               52: (Team.DD, Team.CSK),
               53: (Team.RR, Team.RCB),
               54: (Team.SRH, Team.KKR),
               55: (Team.DD, Team.MI),
               56: (Team.CSK, Team.KXIP)
               }


class Simulator:
    total_counter = 0

    c = Constants()
    qualify_counter = {}
    qualify_with_nrr_counter = {}
    qualify_with_current_nrr_counter = {}

    def __init__(self):
        self.reset()

    def reset(self):
        self.total_counter = 0
        self.qualify_counter = {Team.SRH: 0,
                                Team.CSK: 0,
                                Team.RCB: 0,
                                Team.MI: 0,
                                Team.KXIP: 0,
                                Team.DD: 0,
                                Team.KKR: 0,
                                Team.RR: 0}
        self.qualify_with_nrr_counter = copy.deepcopy(self.qualify_counter)
        self.qualify_with_current_nrr_counter = copy.deepcopy(self.qualify_counter)

    def play(self, chain, match_id):
        if match_id > self.c.MAX_FIXTURE:
            self.evaluate_chain(chain)
            return

        next_match_id = match_id + 1
        fix = self.c.fixture[match_id]

        chain.append(fix[0])
        self.play(chain, next_match_id)

        chain.pop()
        chain.append(fix[1])
        self.play(chain, next_match_id)
        chain.pop()

    def evaluate_chain(self, chain):
        # global c
        # global total_counter
        self.total_counter += 1
        points_chain = copy.deepcopy(self.c.points)
        adjusted_points_chain = copy.deepcopy(self.c.adjusted_points)

        for winner in chain:
            points_chain[winner] += 2
            adjusted_points_chain[winner] += 2

        # evaluate top 4
        sorted_points_chain = sorted(points_chain.items(), key=operator.itemgetter(1), reverse=True)
        # qualifying with NRR : keep adding to bucket top 4 items, then add any other matching #4's score
        # qualifying without NRR : add if points

        fourth_team_point = sorted_points_chain[3][1]
        qualifying_without_nrr = []
        qualifying_without_nrr_candidate = []
        for i in range(0, len(sorted_points_chain)):
            team = sorted_points_chain[i][0]
            point = sorted_points_chain[i][1]
            # qualifying with NRR : teams 1-4, plus any team tieing with 4
            if i < 4 or point == fourth_team_point:
                self.qualify_with_nrr_counter[team] += 1

            # qualifying without NRR:
            # if point > 4th team point, then add to qualifying bucket
            # if point = 4th team point then add to candidate bucket
            if point > fourth_team_point:
                qualifying_without_nrr.append(team)
            elif point == fourth_team_point:
                qualifying_without_nrr_candidate.append(team)

        # if qualifying + candidate = 4 then add, else discard candidate
        if len(qualifying_without_nrr) + len(qualifying_without_nrr_candidate) == 4:
            qualifying_without_nrr += qualifying_without_nrr_candidate

        for team in qualifying_without_nrr:
            self.qualify_counter[team] += 1

        # using current NRR as trend
        for t in sorted(adjusted_points_chain.items(), key=operator.itemgetter(1), reverse=True)[:4]:
            self.qualify_with_current_nrr_counter[t[0]] += 1

    def print_chain(self, chain):
        for c in chain:
            print(c[0], end="  ")

    def print_result(self):
        print("\n\nTeam | Qualifying | Qualifying Current NRR | Qualifying Higher NRR | Qualifying Scenarios | Current NRR | Higher NRR")
        print("-----|------------|-----------------------------|----------------------------|---------------|-------------|-----------")
        for qt in sorted(self.qualify_counter.items(), key=operator.itemgetter(1), reverse=True):
            team = qt[0]
            print(f"{team} | {self.get_percent(self.qualify_counter[team])}% | {self.get_percent(self.qualify_with_current_nrr_counter[team])}% | {self.get_percent(self.qualify_with_nrr_counter[team])}% | {self.qualify_counter[team]} | {self.qualify_with_current_nrr_counter[team]} | {self.qualify_with_nrr_counter[team]}")

        print("\nTotal Simulations : ", self.total_counter, "\n")
        
    def get_percent(self, x):
        percent = round(100 * x / self.total_counter)
        if percent == 100 and x != self.total_counter:
            percent = round(100 * x / self.total_counter, 2)
        return percent

    def play_whatif(self):
        team1, team2 = self.c.fixture[CURRENT_MATCH]
        print(f"\n\n&nbsp;\n\nIf **{team1}** wins match {CURRENT_MATCH} {team1} vs {team2} : ")
        self.reset()
        self.play([team1], CURRENT_MATCH + 1)
        self.print_result()

        print(f"\n\n&nbsp;\n\nIf **{team2}** wins match {CURRENT_MATCH} {team1} vs {team2} : ")
        self.reset()
        self.play([team2], CURRENT_MATCH + 1)
        self.print_result()

    def play_current(self):
        self.reset()
        self.play([], CURRENT_MATCH)
        self.print_result()


sim = Simulator()

print(f"\n\n\nPlay off qualifying probability **after match {CURRENT_MATCH - 1} : {sim.c.fixture[CURRENT_MATCH-1][0]} vs {sim.c.fixture[CURRENT_MATCH-1][1]}**\n")
sim.play_current()
sim.play_whatif()
print("\n\n&nbsp;\n\n^(**Legend:**)")
print("\n\n^(1.**Qualifying** - team qualifies without any NRR tie breaker situation)")
print("\n\n^(2.**Qualifying Current NRR** - team qualifies taking the current NRR as trend that is assumed to be the same after all the league matches)")
print("\n\n^(3.**Qualifying Higher NRR** - team qualifies owing to higher NRR)")
print("\n\n\n")

