import pandas as pd

# Загрузка CSV файла
data = pd.read_csv('csvs/cue1_response2_str_filtered_ROOT.csv')

# Изменение колонки Label
data['Label'] = data['SourceWord'] + ' -> ' + data['TargetWord'] + ' | [' + data['Label'] + '] | вага = ' + data['Weight'].round(2).astype(str)

# Сохранение измененных данных в новый файл
data.to_csv('full_graph_for_gephi/full_gr_edges.csv', index=False)

# Подтверждение завершения операции
"Файл был успешно обработан и сохранен."
