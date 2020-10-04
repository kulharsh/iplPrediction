# iplPrediction

A simple end to end ML project to make predictions on the basis of historical data on the IPL. 
More info about the IPL here: https://en.wikipedia.org/wiki/Indian_Premier_League

It queries this page www.espncricinfo.com/score to try and get a current live match.

Then basis of the current score makes predictions. 
There are two types of predictions:
   - First Innings: How many runs will the team make?
   - Second Innings: What is the Probability of the Chase being successful. 
Data : 
   - The data for  previous seasons of IPL is available on Kaggle https://www.kaggle.com/nowke9/ipldata
   - The data needs to be downloaded from Kaggle seperately. Not included in this repo.
   
The model used is xgboost in both cases (Regression for 1 and Classification for the other) https://xgboost.readthedocs.io/en/latest/
All the training code is in train.py.
The models are then served using a simple Flask api in main.py.



