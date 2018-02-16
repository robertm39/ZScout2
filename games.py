# -*- coding: utf-8 -*-
"""
Created on Sun Jan 21 13:38:09 2018

@author: rober
"""

class Game:
    def __init__(self, categories, numeric_categories, get_scouting_from_match, process_scouting=lambda s:s):
        self.categories = categories
        self.numeric_categories = numeric_categories
        self.get_scouting_from_match = get_scouting_from_match
        self.process_scouting = process_scouting

def put_in_histogram(contrs, upper_limit = False, verbose=False):
    result = {}
    tot = 0
    for contr in contrs:
        result[contr] = result.get(contr, 0) + 1
        tot += 1
        
    for contr in result:
        result[contr] = result[contr] / tot
    
    return result

def averages_from_contrs(contrs):
    result = {}
    for team in contrs.keys():
        result[team] = averages_from_contrs_for_team(contrs[team])
    return result

def averages_from_contrs_for_team(contrs):
    result = {}
    for cat in contrs.keys():
        tot = 0
        cc = contrs[cat]
        for num in cc.keys():
            tot += num * cc[num]
        result[cat] = int(tot*100)/100 #Two decimal places
    return result

def contrs(raw_scouting, game):
    contrs = {}
    for team in raw_scouting.keys():
        contrs[team] = team_contrs(raw_scouting[team], game)
        
    return contrs

def team_contrs(team_scouting, game, pr=False):
    """Return the contrs. Contrs is cat -> distr (num -> amount)"""
    cats = game.numeric_categories
    
    contrs = {}
    for num, results in team_scouting:
        if pr:
            print('num, results:', num, results)
            print('')
        for cat in cats:
            if cat in results:
                if not cat in contrs:
                    contrs[cat] = []
                contrs[cat].append(results[cat])
                
    for cat in contrs:
        contrs[cat] = put_in_histogram(contrs[cat])
        
    return contrs

def steamworks_process_match(match):
    if 'caught_rope' in match:
        match = match.copy()
        match['caught_rope'] |= match['hanging']
    return match

def steamworks_process_scouting(scouting):
    result = {}
    for team in scouting:
        matches = []
        for match in scouting[team]:
            matches.append((match[0], steamworks_process_match(match[1])))
        result[team] = matches
    return result

def powerup_process_match(match):
    match = match.copy()
    endgame_action = match.pop('endgame_action')
    match['climbing'] = int(endgame_action == 0) #climbing is action 0
    match['parking'] =int(endgame_action == 1) #parking is action 1
    return match

def powerup_process_scouting(scouting):
    result = {}
    for team in scouting:
        matches = []
        for match in scouting[team]:
            matches.append((match[0], powerup_process_match(match[1])))
        result[team] = matches
    return result

def get_cats(scouting_cats, game_cats, numeric=False):
    if len(game_cats) == 0:
        result = scouting_cats[:]
        if numeric and 'comments' in result:
            result.remove('comments')
        return result
    return [cat for cat in game_cats if cat in scouting_cats] #intersection

steamworks_cats = ['auton_lowgoal',
                   'auton_highgoal',
                   'auton_gears',
                   'try_lft_auton_gears',
                   'try_cen_auton_gears',
                   'try_rgt_auton_gears',
                   'lft_auton_gears',
                   'cen_auton_gears',
                   'rgt_auton_gears',
                   'crossed_baseline',
                   'pickup_gears',
                   'dropped_gears',
                   'teleop_lowgoal',
                   'teleop_highgoal',
                   'teleop_gears',
                   'hanging',
                   'caught_rope',
                   'comments']
STEAMWORKS = Game(steamworks_cats, steamworks_cats[:-1], None, steamworks_process_scouting)

powerup_cats = ['auton_ci_switch',
                'auton_ci_scale',
                'auton_cube_count',
                'cube_count',
                'cube_switch',
                'cube_scale',
                'cube_vault',
                'fouls',
                'tech_fouls',
                'climbing',
                'hanging',
                'helping_robot',
                'comments']
POWER_UP = Game(powerup_cats, powerup_cats[:-1], None, powerup_process_scouting)

GAMES_FROM_YEARS = {'2017':STEAMWORKS, '2018': POWER_UP}
