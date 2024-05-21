import json

def load_data(path:str)-> dict:
    with open('../data/small_data.json') as f:
        data = json.load(f)
    return data

if __name__ == '__main__':
    #reading JSON file
    data = load_data('../data/small_data.json')
