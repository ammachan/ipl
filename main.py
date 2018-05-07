import copy
import operator

CURRENT_MATCH = 37


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
              Team.MI: 6,
              Team.KXIP: 10,
              Team.DD: 6,
              Team.KKR: 10,
              Team.RR: 6}

    nrr = {Team.CSK: 0.421,
           Team.SRH: 0.471,
           Team.RCB: -0.376,
           Team.MI: 0.005,
           Team.KXIP: 0.130,
           Team.DD: -0.411,
           Team.KKR: 0.240,
           Team.RR: -0.726}

    adjusted_points = {}

    for team in points.keys():
        adjusted_points[team] = points[team] + nrr[team]/10;

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

    def play(self, chain, match_id):
        # print(match_id, chain)
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

        for winner in chain:
            points_chain[winner] += 2
        # print(points_chain)
        # evaluate top 4
        qualifying_teams = sorted(points_chain.items(), key=operator.itemgetter(1), reverse=True)[:4]
        for qt in qualifying_teams:
            self.qualify_counter[qt[0]] += 1

    def print_chain(self, chain):
        for c in chain:
            print(c[0], end="  ")

    def print_result(self):
        print("\n\nTeam | Percent | Qualifying Scenarios")
        print("-----|---------|---------------------")
        for qt in sorted(self.qualify_counter.items(), key=operator.itemgetter(1), reverse=True):
            percent = round(100 * qt[1] / self.total_counter)
            if percent == 100 and qt[1] != self.total_counter:
                percent = round(100 * qt[1] / self.total_counter, 2)
            print(f"{qt[0]} | {percent}% | {qt[1]}")

        print("\nTotal Simulations : ", self.total_counter, "\n")

    def play_whatif(self):
        team1, team2 = self.c.fixture[CURRENT_MATCH]
        print(f"\n\n\nIf **{team1}** wins match {CURRENT_MATCH}")
        self.reset()
        self.play([team1], CURRENT_MATCH + 1)
        self.print_result()

        print(f"\n\n\nIf **{team2}** wins match {CURRENT_MATCH}")
        self.reset()
        self.play([team2], CURRENT_MATCH + 1)
        self.print_result()

    # def play_whatif(self):
    #     team1,team2 = self.c.fixture[CURRENT_MATCH]
    #     print(f"\n\n\nIf **{team1}** wins match {CURRENT_MATCH}")
    #     self.reset()
    #     self.c.points[team1] += 2
    #     self.play([], CURRENT_MATCH + 1)
    #     self.print_result()
    #     self.c.points[team1] -= 2
    #
    #     print(f"\n\n\nIf **{team2}** wins match {CURRENT_MATCH}")
    #     self.reset()
    #     self.c.points[team2] += 2
    #     self.play([], CURRENT_MATCH + 1)
    #     self.print_result()
    #     self.c.points[team2] -= 2


sim = Simulator()
sim.play([], CURRENT_MATCH)

print(f"\n\n\nPlay off qualifying probability after **match {CURRENT_MATCH - 1}**\n")
sim.print_result()
sim.play_whatif()
