from multiprocessing import Pool
from datetime import *
from enum import *
import operator
import copy
import pprint
import re
from secrets import randbelow

MAX_FIXTURE = 56
CURRENT_MATCH = 25
ENABLE_CONSOLE_LOG = False

matches_left = MAX_FIXTURE - CURRENT_MATCH + 1
current_match_index = CURRENT_MATCH
total_simulations = pow(2, matches_left)
total_batches = pow(10, 6)
progress_percent = total_batches / 100
batch_size = max(total_simulations, round(total_simulations / total_batches))

monte_carlo_simulations = pow(10, 4)
monte_carlo_batch = 100
total_monte_carlo_simulations = monte_carlo_simulations * monte_carlo_batch
pp = pprint.PrettyPrinter(indent=4)


class Key:
    GUARANTEED_TOP2 = "guaranteed2"
    GUARANTEED_TOP4 = "guaranteed4"
    NRR_TOP2 = "nrr2"
    NRR_TOP4 = "nrr4"


class Team:
    CSK = "CSK"
    SRH = "SRH"
    RCB = "RCB"
    MI = "MI"
    KXIP = "KXIP"
    DC = "DC"
    KKR = "KKR"
    RR = "RR"

    list = [CSK, SRH, RCB, MI, KXIP, DC, KKR, RR]


class Constants:
    # MAX_FIXTURE = 56

    points = {Team.CSK: 10,
              Team.SRH: 6,
              Team.RCB: 0,
              Team.MI: 8,
              Team.KXIP: 8,
              Team.DC: 6,
              Team.KKR: 8,
              Team.RR: 2}

    nrr = {Team.CSK: 0.220,
           Team.SRH: 0.28,
           Team.RCB: 0.129,
           Team.MI: 0.32,
           Team.KXIP: -0.490,
           Team.DC: -0.22,
           Team.KKR: -0.07,
           Team.RR: -0.246}

    adjusted_points = {}

    def __init__(self):
        self.reset_adjusted_points()

    def reset_adjusted_points(self):
        for team in self.points.keys():
            self.adjusted_points[team] = self.points[team] + self.nrr[team] / 100

    fixture = {
        23: (Team.CSK, Team.KKR),
        24: (Team.MI, Team.KXIP),
        25: (Team.RR, Team.CSK),
        26: (Team.KKR, Team.DC),
        27: (Team.MI, Team.RR),
        28: (Team.KXIP, Team.RCB),
        29: (Team.KKR, Team.CSK),
        30: (Team.SRH, Team.DC),
        31: (Team.MI, Team.RCB),
        32: (Team.KXIP, Team.RR),
        33: (Team.SRH, Team.CSK),
        34: (Team.DC, Team.MI),
        35: (Team.KKR, Team.RCB),
        36: (Team.RR, Team.MI),
        37: (Team.DC, Team.KXIP),
        38: (Team.SRH, Team.KKR),
        39: (Team.RCB, Team.CSK),
        40: (Team.RR, Team.DC),
        41: (Team.CSK, Team.SRH),
        42: (Team.RCB, Team.KXIP),
        43: (Team.KKR, Team.RR),
        44: (Team.CSK, Team.MI),
        45: (Team.RR, Team.SRH),
        46: (Team.DC, Team.RCB),
        47: (Team.KKR, Team.MI),
        48: (Team.SRH, Team.KXIP),
        49: (Team.RCB, Team.RR),
        50: (Team.CSK, Team.DC),
        51: (Team.MI, Team.SRH),
        52: (Team.KXIP, Team.KKR),
        53: (Team.DC, Team.RR),
        54: (Team.RCB, Team.SRH),
        55: (Team.KXIP, Team.CSK),
        56: (Team.MI, Team.KKR)
    }


def play():
    b = list(range(total_batches))
    p = Pool(8, )
    print("Total sim = ", "{:,}".format(total_simulations))
    console_log("started")
    results = p.map(simulate, b)
    print("\n")
    console_log("reducing ...")
    f = reduce(results)
    pp.pprint(f)
    console_log("ended")


def pool_initializer():
    global current_match_index


def play_montecarlo():
    global current_match_index
    b = list(range(monte_carlo_batch))
    p = Pool(8, pool_initializer)
    console_log("Total sim = ", "{:,}".format(total_monte_carlo_simulations))
    console_log("started")
    results = p.map(simulate_monte_carlo, b)
    print("\n")
    console_log("reducing ...")
    cur_result = reduce(results)
    print(
        f"\nMonte Carlo probability **after match {CURRENT_MATCH - 1} : {Constants.fixture[CURRENT_MATCH-1][0]} vs {Constants.fixture[CURRENT_MATCH-1][1]}**\n")
    output_table(total_monte_carlo_simulations, cur_result, use_elimination=False)

    team1, team2 = Constants.fixture[CURRENT_MATCH]
    current_match_index = CURRENT_MATCH + 1
    print(f"\n\n&nbsp;\n\nIf **{team1}** wins match {CURRENT_MATCH} {team1} vs {team2} : ")
    Constants.points[team1] += 2
    p = Pool(8, pool_initializer)
    team1_result = reduce(p.map(simulate_monte_carlo, b))
    output_table(total_monte_carlo_simulations, team1_result, use_elimination=False)
    Constants.points[team1] -= 2

    print(f"\n\n&nbsp;\n\nIf **{team2}** wins match {CURRENT_MATCH} {team1} vs {team2} : ")
    Constants.points[team2] += 2
    p = Pool(8, pool_initializer)
    team2_result = reduce(p.map(simulate_monte_carlo, b))
    output_table(total_monte_carlo_simulations, team2_result, use_elimination=False)
    Constants.points[team2] -= 2
    current_match_index = CURRENT_MATCH

    print("\n\n&nbsp;\n\n^(**Notes:**)")
    print(
        "\n\n^(1.**Monte Carlo** - this is NOT accurate. This is how it works - it picks a match, flips a coin and decides the winner. Repeat till the end of all the league matches. Figure out who qualified. Repeat the whole process for a large number of times and get the %.)")
    print(
        "\n\n^(2.Why is there a range of percentage: its because of NRR situation. For eg 80-90% means 80% of the time, the team can qualify without involving NRR. 90% if the team has top NRR. Somewhere in between if the NRR is mediocre)")
    print("\n\n\n")

    # pp.pprint(cur_result)
    console_log("ended")


def output_table(total, results, match_offset=None, highlight_team=None, use_elimination=True):
    if match_offset is None:
        match_offset = current_match_index
    header = "Team | Pt | ^(Matches Left) | ^(Top 4) | ^(Top 2)"
    print("\n\n" + header)
    print(get_header_dashes(header))

    sorting_table = {}
    for team in Team.list:
        sorting_table.setdefault(team, (results[Key.GUARANTEED_TOP4][team],
                                        results[Key.NRR_TOP4][team],
                                        results[Key.GUARANTEED_TOP2][team],
                                        results[Key.NRR_TOP2][team]))

    sorted_table = sorted(sorting_table.items(), key=lambda x: (x[1][0], x[1][1], x[1][2], x[1][3]), reverse=True)
    for qt in sorted_table:
        team = qt[0]
        team_txt = team if team != highlight_team else "**" + team + "**"
        top4 = f"{get_percentage(results[Key.GUARANTEED_TOP4][team], total)}-{get_percentage(results[Key.NRR_TOP4][team], total)}%"
        top2 = f"{get_percentage(results[Key.GUARANTEED_TOP2][team], total)}-{get_percentage(results[Key.NRR_TOP2][team], total)}%"
        eliminated = "~~" if use_elimination and sum([results[Key.GUARANTEED_TOP4][team], results[Key.NRR_TOP4][team],
                                  results[Key.GUARANTEED_TOP2][team], results[Key.NRR_TOP2][team]]) == 0 else ""
        print(f"{eliminated}{team_txt}{eliminated} | "
              f"{eliminated}{Constants.points[team]}{eliminated} | "
              f"{get_remaining_match_count(team, match_offset)} | "
              f"{eliminated}{top4}{eliminated} | "
              f"{eliminated}{top2}{eliminated} | "
              )
    print("\nTotal Simulations : ", "{:,}".format(total), "\n")


def get_percentage(x, total_counter):
    percent = round(100 * x / total_counter)
    if percent == 100 and x != total_counter or percent == 0 and x != 0:
        percent = round(100 * x / total_counter, 2)
    return percent


def get_remaining_match_count(team, start_from=CURRENT_MATCH):
    count = 0
    for i in range(start_from, 57):
        match = Constants.fixture[i]
        if match[0] == team or match[1] == team:
            count += 1
    return count


def console_log(*args):
    if not ENABLE_CONSOLE_LOG:
        return
    print(datetime.now(), "\t", end="")
    for a in args:
        print(a, end=" ")
    print("\n")


def reduce(results):
    final = {
        Key.GUARANTEED_TOP2: get_team_init_counter(),
        Key.GUARANTEED_TOP4: get_team_init_counter(),
        Key.NRR_TOP2: get_team_init_counter(),
        Key.NRR_TOP4: get_team_init_counter()
    }
    for r in results:
        if r is None: continue
        for k in [Key.GUARANTEED_TOP2, Key.GUARANTEED_TOP4, Key.NRR_TOP2, Key.NRR_TOP4]:
            for team in Team.list:
                final[k][team] += r[k][team]
    return final


def simulate(batch_no):
    global current_match_index
    if ENABLE_CONSOLE_LOG and batch_no % progress_percent == 0:
        print("\r", round(100 * batch_no / total_batches), "%", end=' ', flush=True)

    result = {
        Key.GUARANTEED_TOP2: get_team_init_counter(),
        Key.GUARANTEED_TOP4: get_team_init_counter(),
        Key.NRR_TOP2: get_team_init_counter(),
        Key.NRR_TOP4: get_team_init_counter()
    }
    start = batch_no * batch_size
    end = min(start + batch_size, total_simulations)
    if start >= end:
        return None
    for i in range(start, end):
        points = copy.deepcopy(Constants.points)
        for j in range(matches_left):
            match_index = current_match_index + j
            winner_binary_index = randbelow(2)
            winner = Constants.fixture[match_index][winner_binary_index]
            points[winner] += 2
        evaluate_combo(result, points)

    return result


def simulate_monte_carlo(batch_no):
    if ENABLE_CONSOLE_LOG:
        print("\r", round(100 * batch_no / monte_carlo_batch), "%", end=' ', flush=True)

    result = {
        Key.GUARANTEED_TOP2: get_team_init_counter(),
        Key.GUARANTEED_TOP4: get_team_init_counter(),
        Key.NRR_TOP2: get_team_init_counter(),
        Key.NRR_TOP4: get_team_init_counter()
    }
    for i in range(monte_carlo_simulations):
        points = copy.deepcopy(Constants.points)
        for match_index in range(current_match_index, matches_left):
            winner_binary_index = randbelow(2)
            winner = Constants.fixture[match_index][winner_binary_index]
            points[winner] += 2
        evaluate_combo(result, points)

    return result


def get_team_init_counter():
    return {Team.CSK: 0,
            Team.SRH: 0,
            Team.RCB: 0,
            Team.MI: 0,
            Team.KXIP: 0,
            Team.DC: 0,
            Team.KKR: 0,
            Team.RR: 0}


#
def evaluate_combo(result, points, log_non_qualifying_team=None):
    # # global c
    # # global total_counter
    # self.total_counter += 1
    # points_chain = copy.deepcopy(self.c.points)
    # adjusted_points_chain = copy.deepcopy(self.c.adjusted_points)
    #
    # for winner in chain:
    #     points_chain[winner] += 2
    #     adjusted_points_chain[winner] += 2
    #
    # if self.log_all_combo:
    #     self.log_scenario(chain, points_chain)
    #
    # # evaluate top 4
    sorted_points_chain = sorted(points.items(), key=operator.itemgetter(1), reverse=True)
    # # qualifying with NRR : keep adding to bucket top 4 items, then add any other matching #4's score
    # # qualifying without NRR : add if points

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
            result[Key.NRR_TOP4][team] += 1
        if i < 2 or point == second_team_point:
            result[Key.NRR_TOP2][team] += 1
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
        result[Key.GUARANTEED_TOP4][team] += 1

    if len(qualifying_top2_without_nrr) + len(qualifying_top2_without_nrr_candidate) == 2:
        qualifying_top2_without_nrr += qualifying_top2_without_nrr_candidate
    for team in qualifying_top2_without_nrr:
        result[Key.GUARANTEED_TOP2][team] += 1

    # if log_non_qualifying_team is not None and log_non_qualifying_team not in qualifying_without_nrr:
    #     self.log_non_qualifying_scenario(chain, points_chain)

    # using current NRR as trend
    # sorted_adjusted_points_chain = sorted(adjusted_points_chain.items(), key=operator.itemgetter(1), reverse=True)
    # for t in sorted_adjusted_points_chain[:4]:
    #     self.qualify_with_current_nrr_counter[t[0]] += 1
    # if t[0] in not_qual_nrr:
    # self.log_scenario(chain, points_chain)


def get_header_dashes(txt):
    return re.sub("[^|]", "-", txt)


#
#
# if __name__ == '__main__':
#
# t1 = datetime.now()
# for i in range(1000000000):
#     a = 1
# t2 = datetime.now()
#
# print("Elapsed = ", t2 - t1)

# play()
play_montecarlo()
