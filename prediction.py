import pickle 
import xgboost as xgb
import joblib
import numpy as np
import pandas as pd
import math 
import utils

def run_prediction_call(inning, team1, team2):
    if(inning == 2):
        return run_winning_prediction(team1, team2)
    else:
        return run_score_prediction(team1, team2)

def run_winning_prediction(team1, team2):
    if team1.is_batting:
        batting_team = team1
        bowling_team = team2
    else:
        batting_team = team2
        bowling_team = team1
    runs = batting_team.runs
    wickets = batting_team.wickets
    balls_left = batting_team.balls_left
    batting_id = transform(batting_team.name)
    bowling_id = transform(bowling_team.name)
    xgb_class1 = utils.load_model("second.model")
    df = pd.DataFrame.from_dict({"ball_number": [balls_left], 'batting_team': [batting_id], 'bowling_team':[bowling_id], 'current_score':[runs], 'current_wickets':[wickets]})
    predicted = xgb_class1.predict_proba(df)[0][1]
    return predicted
        
def run_score_prediction(team1, team2):
    if team1.is_batting:
        batting_team = team1
        bowling_team = team2
    else:
        batting_team = team2
        bowling_team = team1
        
    runs = batting_team.runs
    wickets = batting_team.wickets
    balls_left = batting_team.balls_left
    batting_id = transform(batting_team.name)
    bowling_id = transform(bowling_team.name)
    xgb_reg1 = utils.load_model("first.model")
    df = pd.DataFrame.from_dict({"ball_number": [balls_left], 'batting_team': [batting_id], 'bowling_team':[bowling_id], 'current_score':[runs], 'current_wickets':[wickets]})
    predicted = xgb_reg1.predict(df)
    return math.floor(predicted[0])+runs

def transform(name):
    le = utils.load_encoder()
    return le.transform([name])[0]