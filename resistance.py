import pandas as pd
import numpy as np
import copy

class Player():
    def __init__(self, allegiance, spy_ratio):
        self.allegiance = allegiance
        self.suspect = spy_ratio  # measures what the other players may think
        self.appearances = 0
    #
    def update_suspect(self, fail_votes, votes):
        self.appearances += 1
        if fail_votes == 0:
            self.suspect = self.suspect/2
        else:
            self.suspect += fail_votes/votes
    #
    def assign_id(self, id):
        self.id = id

def init_game(n):
    role_dict = {5: (3, 2),
                 6: (4, 2),
                 7: (4, 3),
                 8: (5, 3),
                 9: (6, 3),
                 10: (6, 4)}
    result = []
    role_dist = role_dict[n]
    spy_ratio = role_dist[1]/sum(role_dist)
    #
    for i in range(role_dist[0]):
        result.append(Player('R', spy_ratio))
    for j in range(role_dist[1]):
        result.append(Player('S', spy_ratio))
    for player_idx in range(len(result)):
        result[player_idx].assign_id(player_idx)
    #
    np.random.shuffle(result)
    return result

def mission_assignment(round_list, captain, group):
    team_size = round_list.pop(0)
    # sort index so that we know who the best choices are for a team
    group.sort(key=lambda x: x.suspect)
    counter = 0
    for other_player in group:
        if other_player.id == captain.id:
            captain_idx = counter
        counter += 1
    # place the captain at the end of their entry doesn't interfere
    group.append(group[captain_idx])
    group.remove(group[captain_idx])
    # handle resistance and spy captains separately
    if captain.allegiance == 'R':
        team = [group[captain_idx]]
        for i in range(team_size - 1):
            team.append(group[i])
    elif captain.allegiance == 'S':
        team = []
        for i in range(team_size):
            team.append(group[i])
        if not [player.allegiance for player in team].count('S'):
            for player_idx in range(len(group)):
                if group[player_idx].allegiance == 'S':
                    team.pop()
                    team.append(group[player_idx])
                    break
                else:
                    pass
    return (round_list, team)

def vote(team):
    identities = [player.allegiance for player in team]
    if identities.count('S') == 1:
        return 'FAIL'
    else:
        return 'SUCCESS'

def step_through_rounds(group, round_list):
    scoreboard = []
    for round in range(5):
        round_list, team = mission_assignment(round_list, group[round], group)
        scoreboard.append(vote(team))
        if scoreboard.count('FAIL') == 3:
            return('S', len(scoreboard))
        elif scoreboard.count('SUCCESS') == 3:
            return('R', len(scoreboard))


if __name__ == '__main__':
    mission_strength_dict = {5: [2, 3, 2, 3, 3],
                             6: [2, 3, 4, 3, 4],
                             7: [2, 3, 3, 4, 4],
                             8: [3, 4, 4, 5, 5],
                             9: [3, 4, 4, 5, 5],
                             10: [3, 4, 4, 5, 5]}
    winner = []
    rounds = []
    group_size = []
    #
    for test_size in range(10000):
        n = np.random.randint(5, 11)
        group = init_game(n)
        round_list = copy.deepcopy(mission_strength_dict[n])
        tmp_winner, tmp_rounds = step_through_rounds(group, round_list)
        rounds.append(tmp_rounds)
        winner.append(tmp_winner)
        group_size.append(n)
    df = pd.DataFrame({'winner': winner,
                       'rounds': rounds,
                       'group_size': group_size})

df.groupby('group_size')['winner'].value_counts(dropna=False).unstack()
