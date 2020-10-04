from sklearn import preprocessing
import pickle
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, roc_auc_score 
import xgboost as xgb
import joblib
import math    
import pandas as pd
import utils 
import preprocess
    
def train_score_predictor(features):
    print("****Training First Inning Score Predictor****")
    X = features[features['inning'] == 1]
    X = X[X['over'] > 5]
    X['output'] = X['total_runs'].astype(float) - X['current_score'].astype(float)
    train, test = train_test_split(X)
    print("Training set: "+str(len(train)))
    cols = ['ball_number', 'batting_team', 'bowling_team', 'current_score', 'current_wickets']
    print("Features: ",cols)      
    X_train = train[cols]
    y_train = train['output']
    X_test = test[cols]
    y_test = test['output']
    xg_reg = xgb.XGBRegressor(objective ='reg:linear', colsample_bytree = 0.2, learning_rate = 0.1,
                max_depth = 6, alpha = 0.1, n_estimators = 150)

    xg_reg.fit(X_train,y_train)
    utils.save_model(xg_reg, "first.model")
    preds = xg_reg.predict(X_test)
    error = mean_squared_error(y_test, preds)
    print("test set error :"+str(math.sqrt(error))+" runs")
          
def train_chase_predictor(features):
    print("****Training Second Inning chase Predictor****")
    X = features[features['inning'] == 2]
    train, test = train_test_split(X)
    cols = ['ball_number', 'batting_team', 'bowling_team', 'current_score', 'current_wickets']
    X_train = train[cols]
    y_train = train['match_result']
    X_test = test[cols]
    y_test = test['match_result']
    print("Training set: "+str(len(train)))
    print("Features: ",cols)
    xg_class = xgb.XGBClassifier(objective ='binary:logistic', colsample_bytree = 0.2, learning_rate = 0.1,
                max_depth = 6, alpha = 0.1, n_estimators = 150)

    xg_class.fit(X_train,y_train)
    utils.save_model(xg_class, "second.model")
    preds = xg_class.predict(X_test)
    print("Test set AUC: "+str(roc_auc_score(y_test, preds))) 
          
def run_training():
    df = pd.read_csv("deliveries.csv")
    features = preprocess.preprocess_data(df)
    train_score_predictor(features)
    train_chase_predictor(features)
    
if __name__=="__main__":
    run_training()