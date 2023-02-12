from utils.packages import *


def get_points(data):
    data['df']['home_score'] = pd.to_numeric(data['df']['result'].str.split('-', expand =  True)[0])
    data['df']['away_score'] = pd.to_numeric(data['df']['result'].str.split('-', expand =  True)[1])

    data['df'].loc[data['df']['home_score'] > data['df']['away_score'], ['home_points', 'away_points']] = [3,0]
    data['df'].loc[data['df']['home_score'] < data['df']['away_score'], ['home_points', 'away_points']] = [0,3]
    data['df'].loc[data['df']['home_score'] == data['df']['away_score'], ['home_points', 'away_points']] = [1,1]
    return(data)

def get_rank_difficulty(data):
    data['clubs_list'] = list(set(data['df']['home_team']) | set(data['df']['away_team']))
    data['points_df'] = pd.DataFrame()


    for i, club in enumerate(data['clubs_list']):
        data['temp_df'] = pd.DataFrame()
        club_home_points = data['df'].loc[data['df']['home_team' ] == club, 'home_points'].sum()
        club_away_points = data['df'].loc[data['df']['away_team' ] == club, 'away_points'].sum()

        club_home_games = data['df'].loc[data['df']['home_team' ] == club, 'home_points'].count()
        club_away_games = data['df'].loc[data['df']['away_team' ] == club, 'away_points'].count()


        data['temp_df']['club'] = [club]
        data['temp_df']['games_played'] = [club_home_games + club_away_games]
        data['temp_df']['points'] = [club_home_points + club_away_points]    

        data['points_df'] = data['points_df'].append(data['temp_df'])

        data['points_df'] = data['points_df'].sort_values(by=['points', 'games_played'], ascending = [False, True])    
        data['points_df']['curr_rank'] = data['points_df']['points'].rank(ascending = False)
        data['points_df']['difficulty'] = data['points_df']['points'].rank(ascending = True)
        data['points_df'] = data['points_df'].reset_index(drop=True)
        data['points_df'].index = data['points_df'].index + 1
        
        data['difficulty_dict'] = pd.Series(data['points_df']['difficulty'].values, data['points_df']['club'].values).to_dict()

        
    return(data)


def get_points_difficulty(data):
    data['clubs_list'] = list(set(data['df']['home_team']) | set(data['df']['away_team']))
    data['points_df'] = pd.DataFrame()


    for i, club in enumerate(data['clubs_list']):
        data['temp_df'] = pd.DataFrame()
        club_home_points = data['df'].loc[data['df']['home_team' ] == club, 'home_points'].sum()
        club_away_points = data['df'].loc[data['df']['away_team' ] == club, 'away_points'].sum()

        club_home_games = data['df'].loc[data['df']['home_team' ] == club, 'home_points'].count()
        club_away_games = data['df'].loc[data['df']['away_team' ] == club, 'away_points'].count()


        data['temp_df']['club'] = [club]
        data['temp_df']['games_played'] = [club_home_games + club_away_games]
        data['temp_df']['points'] = [club_home_points + club_away_points]    

        data['points_df'] = data['points_df'].append(data['temp_df'])

        data['points_df'] = data['points_df'].sort_values(by=['points', 'games_played'], ascending = [False, True])    
        data['points_df']['curr_rank'] = data['points_df']['points'].rank(ascending = False)
        data['points_df'] = data['points_df'].reset_index(drop=True)
        data['points_df'].index = data['points_df'].index + 1
        
    data['points_df']['difficulty'] = data['points_df']['points']
    data['difficulty_dict'] = pd.Series(data['points_df']['difficulty'].values, data['points_df']['club'].values).to_dict()
        
    return(data)


def get_remining_difficulty(data):
    for i, club in enumerate(data['clubs_list']):
        all_clubs = list(data['points_df']['club'])
        all_clubs.remove(club)
        all_opponents = all_clubs * 2
        all_opponents.sort()

        home_opponents = list(data['df'][data['df']['home_team'] == club]['away_team'])
        home_opponents.sort()

        away_opponents = list(data['df'][data['df']['away_team'] == club]['home_team'])
        away_opponents.sort()

        faced_total_opponents = home_opponents + away_opponents
        faced_total_opponents.sort()

        data['remaining_opponents'] = all_opponents
        for opponent in faced_total_opponents:
            data['remaining_opponents'].remove(opponent)    
            
        data['double_headers'] = [x for n, x in enumerate(data['remaining_opponents']) if x in data['remaining_opponents'][:n]]

        data['num_opp_rem'] = len(data['remaining_opponents'])
        data['total_rem_diff'] = sum([data['difficulty_dict'][x] for x in data['remaining_opponents']])
        data['avg_diff_rem'] = np.round(data['total_rem_diff'] / data['num_opp_rem'],2)

        data['points_df'].loc[data['points_df']['club'] == club, 'total_rem_diff'] =  data['total_rem_diff'] 
        data['points_df'].loc[data['points_df']['club'] == club, 'num_opp_rem'] =  data['num_opp_rem'] 
        data['points_df'].loc[data['points_df']['club'] == club, 'avg_rem_diff'] = data['avg_diff_rem']
        data['points_df'].loc[data['points_df']['club'] == club, 'pend_double_head'] = str(data['double_headers'])
        data['points_df'].loc[data['points_df']['club'] == club, 'yet_to_play'] = str(data['remaining_opponents'])
        data['points_df'] = data['points_df'].sort_values(by = ['avg_rem_diff'])
        
        data['points_df'] = data['points_df'].reset_index(drop=True)
        data['points_df'].index = data['points_df'].index + 1

    return(data)

def remove_and_compare(data):
    
    rem_opp_a = ast.literal_eval(data['points_df'].loc[data['points_df']['club'] == data['team_a'], 'yet_to_play'].values[0])
    rem_opp_a = [x for x in rem_opp_a if x != data['team_b']]

    data['num_opp_rem'] = len(rem_opp_a)
    data['total_rem_diff'] = sum([data['difficulty_dict'][x] for x in rem_opp_a])
    data['avg_diff_rem'] = np.round(data['total_rem_diff'] / data['num_opp_rem'],2)

    print(f'{data["team_a"]} has {data["num_opp_rem"]} games left with average difficulty of {data["avg_diff_rem"]} (excluding {data["team_b"]})')
    
    
    temp = data['team_a']
    data['team_a'] = data['team_b']
    data['team_b'] = temp
    
    rem_opp_a = ast.literal_eval(data['points_df'].loc[data['points_df']['club'] == data['team_a'], 'yet_to_play'].values[0])
    rem_opp_a = [x for x in rem_opp_a if x != data['team_b']]

    data['num_opp_rem'] = len(rem_opp_a)
    data['total_rem_diff'] = sum([data['difficulty_dict'][x] for x in rem_opp_a])
    data['avg_diff_rem'] = np.round(data['total_rem_diff'] / data['num_opp_rem'],2)

    print(f'{data["team_a"]} has {data["num_opp_rem"]} games left with average difficulty of {data["avg_diff_rem"]} (excluding {data["team_b"]})')
    
    return(data)
