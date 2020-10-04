from flask import Flask, render_template, redirect, url_for, request, session
from team import Team
import prediction
import requests
from bs4 import BeautifulSoup
import xgboost as xgb
import pickle
import math
import json
import dryscrape

app = Flask(__name__)
app.secret_key = "secret"
series = "Indian Premier League"
status1 = "Live"
def get_soup():
    url = "https://www.espncricinfo.com/scores"
    page = requests.get(url, headers={'Cache-Control': 'no-cache'})
    if page.status_code == 200:
        html = page.content
        soup = BeautifulSoup(html, 'html')
        return soup
'''def get_soup():
    session = dryscrape.Session()
    session.visit("https://www.espncricinfo.com/scores")
    response = session.body()
    soup = BeautifulSoup(response)
    return soup'''

    
def find_inning(team1, team2):
    if team1.is_chasing() or team2.is_chasing():
        return 2
    else:
        return 1
    
def process_team(div):
    name = div.find_all("p", class_="name")[0].get_text()
    score = div.find_all("span", class_="score")[0].get_text()
    extraDiv = div.find_all("span", class_="extra-score")
    extra = ""
    if len(extraDiv) > 0:
        extra = extraDiv[0].get_text()
    battingDot = div.find_all("span", class_="batting-dot")
    is_batting = False
    if len(battingDot) > 0:
        is_batting = True
    imageSrc = div.find_all("img")[0]['src']
    return Team(name, score, extra, is_batting, imageSrc)

def build_response(team1, team2, inning, prediction):
    resp = {}
    resp['team1'] = [team1.name, team1.score, team1.extra, team1.is_batting, team1.image]
    resp['team2'] = [team2.name, team2.score, team2.extra, team2.is_batting, team2.image]
    if inning == 1:
        resp['pred'] = "The prediction score is : "+str(prediction)
    else:
        resp['pred'] = "The chasing team will win with probability : "+str(prediction)
    return resp

def run():
    soup = get_soup()
    if soup != None: 
        score_blocks = soup.find_all("div", class_= "match-score-block")
        for block in score_blocks:
            description = block.find_all("p", "small mb-0 match-description")[0].get_text()
            if series in description:
                statuses = block.find_all("span", "label match-status red")
                print(description)
                if len(statuses) > 0:
                    status = statuses[0].get_text()
                    print(status1, status)
                    if status1 in status:
                        teams = block.find_all("div", class_="d-flex justify-content-between align-items-center competitor")
                        team1 = process_team(teams[0])
                        team2 = process_team(teams[1])
                        print(team1.to_string(), team2.to_string())
                        inning = find_inning(team1, team2)
                        prediction1 = prediction.run_prediction_call(inning, team1, team2)
                        print(prediction1)
                        response = build_response(team1, team2, inning, prediction1)
                        return response

                
@app.route('/', methods = ['GET', 'POST'])
def index():
    if request.method == 'GET':
        responses = run()
        print(responses)
        if responses == None:
            return render_template("error.html")
        return render_template('results.html', responses=responses)

if __name__ == '__main__':
    app.run(host = "192.168.0.103", port = "5101")
