import pandas as pd

data = pd.read_csv('csvs/cue1_response2_str_filtered_ROOT.csv')

# Зміна Label
data['Label'] = data['SourceWord'] + ' -> ' + data['TargetWord'] + ' | [' + data['Label'] + '] | вага = ' + data['Weight'].round(1).astype(str)

data.to_csv('full_graph_for_gephi/full_gr_edges.csv', index=False)

"Файл успішно оброблено і збережено."
