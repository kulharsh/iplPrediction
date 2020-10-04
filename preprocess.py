from sklearn import preprocessing
import pickle
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, roc_auc_score 
import xgboost as xgb
import joblib
import math    
import pandas as pd
import utils 

def preprocess_data(df):
    ballCummulativeScore, wicketCummulative ,strikerRatioCummulative, non_strikerRatioCummulative, strikerBallCummulative, non_strikerBallCummulative = get_cummulative_dictionaries()
    scoreMap = get_score_dictionary(df)
    match_result = get_match_result_dictionary()
    
    print("Preprocessing Data: ")
    df['match_inning_id'] = df['match_id'].astype(str) + "_" + df['inning'].astype(str)
    df['ball_id'] = df['match_id'].astype(str) + "_" + df['inning'].astype(str)+"_"+df['over'].astype(str) + "_" + df['ball'].astype(str)

    df['total_runs'] = df.apply(lambda x: addscore(x, scoreMap), axis =1)
    df['current_score'] = df.apply(lambda x: addFromDict(x, ballCummulativeScore), axis = 1)
    df['current_wickets'] = df.apply(lambda x: addFromDict(x, wicketCummulative), axis = 1)
    df['match_result'] = df.apply(lambda x: addMatchResult(x, match_result), axis =1)
    df['stiker_ratio'] = df.apply(lambda x: addFromDict(x, strikerRatioCummulative), axis=1)
    df['non_stiker_ratio'] = df.apply(lambda x: addFromDict(x, non_strikerRatioCummulative), axis=1)
    df['stiker_balls'] = df.apply(lambda x: addFromDict(x, strikerBallCummulative), axis=1)
    df['non_stiker_balls'] = df.apply(lambda x: addFromDict(x, non_strikerBallCummulative), axis=1)
    df['ball_number'] = 120 - ((df['over'].astype(float) -1)*6 + df['ball'].astype(float))
    features = df[['match_id','match_result','inning', 'ball_number', 'over', 'ball', 'batting_team', 'bowling_team', 'batsman', 'non_striker', 'bowler', 'current_score', 'current_wickets', 'total_runs']] 
    le = preprocessing.LabelEncoder()
    features['batting_team'] = le.fit_transform(features['batting_team'])
    features['bowling_team'] = le.transform(features['bowling_team'])
    utils.dump_encoder(le)
    return features


def update(b, striker, non_striker, st):
    if b == striker:
        return non_striker
    if b == non_striker:
        return striker
    elif st:
        return striker
    else:
        return non_striker
    
def get_score_dictionary(df):
    scoreMap = {}
    totals = df.groupby(["match_id", "inning"]).sum()['total_runs']
    try :
        for l in totals.to_csv().split("\n"):
            match_id = l.split(",")[0]
            inning = l.split(",")[1]
            total_runs = l.split(",")[2]
            scoreMap[str(match_id + "_" + inning)] = total_runs
    except:
        pass
    return scoreMap

def get_cummulative_dictionaries():
    ballCummulativeScore = {}
    wicketCummulative = {}
    strikerRatioCummulative = {}
    non_strikerRatioCummulative = {}
    strikerBallCummulative = {}
    non_strikerBallCummulative = {}
    batsman1 = None
    batsman2 = None
    batsman1_runs = 0
    batsman1_balls = 0
    batsman2_runs = 0
    batsman2_balls = 0
    with open("deliveries.csv") as file1:
        oldMatchId = 1
        oldInningId = 1
        cummulative = 0
        wicketCount = 0
        skip = True
        for l in file1:
            values = l.split(",")
            if skip:
                skip = False
                continue
            match_id = values[0]
            inning = values[1]
            over  = values[4]
            ball = values[5]
            score = int(values[17])
            striker = values[6]
            non_striker = values[7]
            if batsman1 == None:
                batsman1 = update(batsman2, striker, non_striker, True)
            if batsman2 == None:
                batsman2 = update(batsman1, striker, non_striker, False)
            ball_id = match_id+"_"+inning+"_"+over+"_"+ball
            if str(oldMatchId) != str(match_id) or str(oldInningId) != str(inning):
                cummulative = 0
                oldMatchId = match_id
                oldInningId = inning
                wicketCount = 0
                batsman1_runs = 0 
                batsman1_balls = 0 
                batsman2_runs = 0
                batsman2_balls = 0
                batsman1 = None
                batsman2 = None
            dismissal = values[19]
            dismissed_batsman = values[18]
            if dismissal != "":
                if batsman1 == dismissed_batsman:
                    batsman1 = None
                    batsman1_runs = 0 
                    batsman1_balls = 0    
                if batsman2 == dismissed_batsman:
                    batsman2 = None  
                    batsman2_runs = 0
                    batsman2_balls = 0  
                wicketCount += 1
            if batsman1 == striker:
                batsman1_runs += score
                batsman1_balls += 1 
            elif batsman2 == striker:
                batsman2_runs += score
                batsman2_balls += 1
            cummulative = cummulative + score;
            ballCummulativeScore[ball_id] = cummulative
            wicketCummulative[ball_id] = wicketCount
            strikerRatio = 0
            nonStringRatio = 0
            if striker == batsman1 : 
                if batsman1_balls:
                    strikerRatio = batsman1_runs / batsman1_balls
                if batsman2_balls > 0:
                    nonStringRatio =  batsman2_runs / batsman2_balls
                strikerBalls = batsman1_balls
                non_strikerBalls = batsman2_balls
            elif striker == batsman2 :
                if batsman2_balls > 0 :
                    strikerRatio = batsman2_runs / batsman2_balls
                if batsman1_balls > 0:
                    nonStringRatio = batsman1_runs / batsman1_balls
                strikerBalls = batsman2_balls
                non_strikerBalls = batsman1_balls
            if strikerRatio != None :
                strikerRatioCummulative[ball_id] = strikerRatio
                non_strikerRatioCummulative[ball_id] = nonStringRatio
                strikerBallCummulative[ball_id] = strikerBalls
                non_strikerBallCummulative[ball_id] = non_strikerBalls
        return  ballCummulativeScore, wicketCummulative ,strikerRatioCummulative, non_strikerRatioCummulative, strikerBallCummulative, non_strikerBallCummulative

def get_match_result_dictionary():
    matchdf = pd.read_csv("matches.csv")
    match_result = {}
    try :
        for m in matchdf.to_csv().split("\n"):
            m_id = m.split(",")[1]
            win_by_wickets = m.split(",")[13]
            win_by_runs = m.split(",")[12]
            chase_win = 0
            if win_by_wickets != '0' and win_by_runs == '0':
                chase_win = 1
            match_result[m_id] = chase_win
    except:
        pass
    return match_result

def addscore(r, scoreMap):
    return scoreMap.get(r['match_inning_id'])

def addMatchResult(r, match_result):
    return match_result.get(str(r['match_id'])) 

def addFromDict(r, dictionary):
    return dictionary.get(r['ball_id'])
