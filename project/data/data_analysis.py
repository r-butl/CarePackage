import pandas as pd

file = '/home/lucas/Desktop/programming/Senior_project/project/data/ptbxl_database.csv'

data = pd.read_csv(file)

classifications = set(data['report'])

print(len(classifications))
