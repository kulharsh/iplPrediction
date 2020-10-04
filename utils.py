import pickle
import joblib

def dump_encoder(le):
    output = open('team_encoder.pkl', 'wb')
    pickle.dump(le, output)
    output.close()
    
def load_encoder():
    pkl_file = open('team_encoder.pkl', 'rb')
    le = pickle.load(pkl_file) 
    pkl_file.close()
    return le

def save_model(model, model_name):
    joblib.dump(model, model_name)

def load_model(model_name):
    return joblib.load(model_name)