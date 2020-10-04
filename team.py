def mapOfName(name):
    testMap = {"RCB": "Royal Challengers Bangalore", "RR": "Rajasthan Royals", "DC": "Delhi Daredevils", "KKR":"Kolkata Knight Riders",}
    return testMap.get(name, name)

class Team:
    def __init__(self,name, score, extra, is_batting, image):
        self.name = mapOfName(name)
        self.score = score
        self.extra = extra
        self.balls_left = self.process_overs(extra)
        self.is_batting = is_batting
        self.runs, self.wickets = self.process_score(score)
        self.image = image
        
    def process_score(self,score):
        if len(score) > 0: 
            if len(score.split("/")) == 1:
                run = score.split("/")[0]
                wicket = 10
            else:
                run = score.split("/")[0]
                wicket = score.split("/")[1]
            return int(run),int(wicket)
        else:
            return 0,0
        
    def process_overs(self,extra):
        if len(extra) > 0: 
            overs = extra.split(",")[0][1:].split("/")[0]
            if len(overs.split(".")) == 1:
                complete = overs.split(".")[0]
                balls = 0
            else:
                complete = overs.split(".")[0]
                balls = overs.split(".")[1].split(" ")[0]
            total_balls = 120 - (int(complete) * 6 + int(balls))
            return int(total_balls)
        else:
            return 0
        
    def is_chasing(self):
        if "target" in self.extra and self.is_batting:
            return True
    def to_string(self):
        return self.name + ": " + self.score + "("+self.extra + " , "+ str(self.is_batting)+")" + str(self.runs)+"  "+str(self.wickets)