import copy
import operator
import re

CURRENT_MATCH = 56


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

    points = {Team.CSK: 16,
              Team.SRH: 18,
              Team.RCB: 12,
              Team.MI: 12,
              Team.KXIP: 12,
              Team.DD: 10,
              Team.KKR: 16,
              Team.RR: 14}

    nrr = {Team.CSK: 0.220,
           Team.SRH: 0.28,
           Team.RCB: 0.129,
           Team.MI: 0.32,
           Team.KXIP: -0.490,
           Team.DD: -0.22,
           Team.KKR: -0.07,
           Team.RR: -0.246}

    adjusted_points = {}

    def __init__(self):
        self.reset_adjusted_points()

    def reset_adjusted_points(self):
        for team in self.points.keys():
            self.adjusted_points[team] = self.points[team] + self.nrr[team] / 100

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
    qualify_top2_counter = {}
    qualify_top2_with_nrr_counter = {}
    log_all_combo = False

    max_log_non_qualifying = 10

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
        self.qualify_with_nrr_counter = copy.deepcopy(self.qualify_counter)
        self.qualify_top2_counter = copy.deepcopy(self.qualify_counter)
        self.qualify_top2_with_nrr_counter = copy.deepcopy(self.qualify_counter)

    def play(self, chain, match_id, log_non_qualifying_team=None):
        if match_id > self.c.MAX_FIXTURE:
            self.evaluate_chain(chain, log_non_qualifying_team)
            return

        next_match_id = match_id + 1
        fix = self.c.fixture[match_id]

        chain.append(fix[0])
        self.play(chain, next_match_id, log_non_qualifying_team)

        chain.pop()
        chain.append(fix[1])
        self.play(chain, next_match_id, log_non_qualifying_team)
        chain.pop()

    def play_team_domination(self, chain, match_id, team):
        if match_id > self.c.MAX_FIXTURE:
            self.evaluate_chain(chain)
            return

        next_match_id = match_id + 1
        fix = self.c.fixture[match_id]

        if fix[0] == team or fix[1] == team:
            chain.append(team)
            self.play(chain, next_match_id)
        else:
            chain.append(fix[0])
            self.play(chain, next_match_id)

            chain.pop()
            chain.append(fix[1])
            self.play(chain, next_match_id)
            chain.pop()

    def evaluate_chain(self, chain, log_non_qualifying_team=None):
        # global c
        # global total_counter
        self.total_counter += 1
        points_chain = copy.deepcopy(self.c.points)
        adjusted_points_chain = copy.deepcopy(self.c.adjusted_points)

        for winner in chain:
            points_chain[winner] += 2
            adjusted_points_chain[winner] += 2

        if self.log_all_combo:
            self.log_scenario(chain, points_chain)

        # evaluate top 4
        sorted_points_chain = sorted(points_chain.items(), key=operator.itemgetter(1), reverse=True)
        # qualifying with NRR : keep adding to bucket top 4 items, then add any other matching #4's score
        # qualifying without NRR : add if points

        fourth_team_point = sorted_points_chain[3][1]
        second_team_point = sorted_points_chain[1][1]
        qualifying_without_nrr = []
        qualifying_without_nrr_candidate = []
        qualifying_top2_without_nrr = []
        qualifying_top2_without_nrr_candidate = []
        # not_qual_nrr = {}

        for i in range(0, len(sorted_points_chain)):
            team = sorted_points_chain[i][0]
            point = sorted_points_chain[i][1]
            # qualifying with NRR : teams 1-4, plus any team tieing with 4
            if i < 4 or point == fourth_team_point:
                self.qualify_with_nrr_counter[team] += 1
            if i < 2 or point == second_team_point:
                self.qualify_top2_with_nrr_counter[team] += 1
            # else:
            #     not_qual_nrr[team] = 1
            # qualifying without NRR:
            # if point > 4th team point, then add to qualifying bucket
            # if point = 4th team point then add to candidate bucket
            if point > fourth_team_point:
                qualifying_without_nrr.append(team)
            elif point == fourth_team_point:
                qualifying_without_nrr_candidate.append(team)

            if point > second_team_point:
                qualifying_top2_without_nrr.append(team)
            elif point == second_team_point:
                qualifying_top2_without_nrr_candidate.append(team)

        # if qualifying + candidate = 4 then add, else discard candidate
        if len(qualifying_without_nrr) + len(qualifying_without_nrr_candidate) == 4:
            qualifying_without_nrr += qualifying_without_nrr_candidate
        for team in qualifying_without_nrr:
            self.qualify_counter[team] += 1

        if len(qualifying_top2_without_nrr) + len(qualifying_top2_without_nrr_candidate) == 2:
            qualifying_top2_without_nrr += qualifying_top2_without_nrr_candidate
        for team in qualifying_top2_without_nrr:
            self.qualify_top2_counter[team] += 1

        if log_non_qualifying_team is not None and log_non_qualifying_team not in qualifying_without_nrr:
            self.log_non_qualifying_scenario(chain, points_chain)

        # using current NRR as trend
        sorted_adjusted_points_chain = sorted(adjusted_points_chain.items(), key=operator.itemgetter(1), reverse=True)
        for t in sorted_adjusted_points_chain[:4]:
            self.qualify_with_current_nrr_counter[t[0]] += 1
            # if t[0] in not_qual_nrr:
            #     self.log_scenario(chain, points_chain)


    @staticmethod
    def get_header_dashes(txt):
        return re.sub("[^|]", "-", txt)

    def print_log_scenario_header(self):
        header = "|".join(self.c.points.keys())
        for match in range(CURRENT_MATCH, 57):
            header += "|" + str(match)
        print(header)
        print(self.get_header_dashes(header))

    def log_non_qualifying_scenario(self, chain, points_chain):
        self.max_log_non_qualifying -= 1
        if self.max_log_non_qualifying < 0:
            return
        self.log_scenario(chain, points_chain)

    def log_scenario(self, chain, points_chain):
        for team in self.c.points.keys():
            print(points_chain[team], end="|")
        print("|".join(chain))

    def print_chain(self, chain):
        for c in chain:
            print(c[0], end="  ")

    def print_result(self, highlight_team=None, match_offset=CURRENT_MATCH):
        header = "Team | Pt | ^(Matches Left) | ^(Qualifying) | ^(Qualifying Current NRR) | ^(Qualifying Higher NRR) | ^(Top 2) | ^(Qualifying Scenarios) | ^(Current NRR) | ^(Higher NRR) | ^(Top2 no tie) | ^(Top2 NRR)"
        print("\n\n" + header)
        print(self.get_header_dashes(header))
        sorting_table = {}
        for team in self.c.points.keys():
            sorting_table.setdefault(team, (self.qualify_counter[team],
                                            self.qualify_with_current_nrr_counter[team],
                                            self.qualify_with_nrr_counter[team],
                                            self.qualify_top2_counter[team],
                                            self.qualify_top2_with_nrr_counter[team]))

        sorted_table = sorted(sorting_table.items(), key=lambda x: (x[1][0], x[1][1], x[1][2], x[1][3], x[1][4]), reverse=True)
        for qt in sorted_table:
            team = qt[0]
            team_txt = team if team != highlight_team else "**" + team + "**"
            top2 = self.get_percent(self.qualify_top2_counter[team]) if self.get_percent(self.qualify_top2_counter[team]) == 100 or self.get_percent(self.qualify_top2_with_nrr_counter[team]) == 0 else f"{self.get_percent(self.qualify_top2_counter[team])}-{self.get_percent(self.qualify_top2_with_nrr_counter[team])}"
            eliminated = "~~" if self.qualify_counter[team] == self.qualify_with_current_nrr_counter[team] == self.qualify_with_nrr_counter[team] == 0 else ""
            print(f"{eliminated}{team_txt}{eliminated} | "
                  f"{eliminated}{self.c.points[team]}{eliminated} | "
                  f"{self.get_remaining_match_count(team, match_offset)} | "
                  f"{eliminated}{self.get_percent(self.qualify_counter[team])}%{eliminated} | "
                  f"{eliminated}{self.get_percent(self.qualify_with_current_nrr_counter[team])}%{eliminated} | "
                  f"{eliminated}{self.get_percent(self.qualify_with_nrr_counter[team])}%{eliminated} | "
                  f"{eliminated}{top2}%{eliminated} | "
                  f"{eliminated}^{self.qualify_counter[team]}{eliminated} | "
                  f"{eliminated}^{self.qualify_with_current_nrr_counter[team]}{eliminated} | "
                  f"{eliminated}^{self.qualify_with_nrr_counter[team]}{eliminated} | "
                  f"{eliminated}^{self.qualify_top2_counter[team]}{eliminated} | "
                  f"{eliminated}^{self.qualify_top2_with_nrr_counter[team]}{eliminated}")

        print("\nTotal Simulations : ", self.total_counter, "\n")

    def get_percent(self, x):
        percent = round(100 * x / self.total_counter)
        if percent == 100 and x != self.total_counter or percent == 0 and x != 0:
            percent = round(100 * x / self.total_counter, 2)
        return percent

    def play_whatif(self):
        team1, team2 = self.c.fixture[CURRENT_MATCH]
        print(f"\n\n&nbsp;\n\nIf **{team1}** wins match {CURRENT_MATCH} {team1} vs {team2} : ")
        self.reset()
        self.c.points[team1] += 2
        self.c.reset_adjusted_points()
        self.play([], CURRENT_MATCH + 1)
        self.print_result(team1, CURRENT_MATCH + 1)
        self.c.points[team1] -= 2

        print(f"\n\n&nbsp;\n\nIf **{team2}** wins match {CURRENT_MATCH} {team1} vs {team2} : ")
        self.reset()
        self.c.points[team2] += 2
        self.c.reset_adjusted_points()
        self.play([], CURRENT_MATCH + 1)
        self.print_result(team2, CURRENT_MATCH + 1)
        self.c.points[team2] -= 2
        self.c.reset_adjusted_points()

    def play_current(self, log_non_qualifying_team=None):
        if log_non_qualifying_team is not None:
            self.max_log_non_qualifying = 10
            self.print_log_scenario_header()
        if self.log_all_combo:
            self.print_log_scenario_header()
        self.reset()
        self.play([], CURRENT_MATCH, log_non_qualifying_team)
        self.print_result()

    def play_team_winning_all_future(self, team):
        self.reset()
        self.play_team_domination([], CURRENT_MATCH, team)
        self.print_result()

    def get_remaining_match_count(self, team, start_from=CURRENT_MATCH):
        count = 0
        for i in range(start_from, 57):
            match = self.c.fixture[i]
            if match[0] == team or match[1] == team:
                count += 1
        return count


sim = Simulator()
# sim.log_all_combo = True
print(f"\nPlay off qualifying probability **after match {CURRENT_MATCH - 1} : {sim.c.fixture[CURRENT_MATCH-1][0]} vs {sim.c.fixture[CURRENT_MATCH-1][1]}**\n")
# sim.play_current(log_non_qualifying_team=Team.SRH)
#
sim.play_current()

sim.log_all_combo = False
sim.play_whatif()
print("\n\n&nbsp;\n\n^(**Legend:**)")
print("\n\n^(1.**Qualifying** - team qualifies without any NRR tie breaker situation)")
print(
    "\n\n^(2.**Qualifying Current NRR** - team qualifies taking the current NRR as trend that is assumed to be the same after all the league matches)")
print("\n\n^(3.**Qualifying Higher NRR** - team qualifies owing to higher NRR)")
print("\n\n^(4.**Top 2** - team finishes in top 2. The lower number represents no tie situation. The higher number represents higher NRR situation)")
print("\n\n\n")

sim.reset()
# sim.play_team_winning_all_future(Team.RR)

# sim.print_log_non_qualifying_header()
