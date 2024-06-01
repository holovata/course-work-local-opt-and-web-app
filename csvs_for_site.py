import pandas as pd
import zipfile
import os

# Читання вихідного CSV файлу
input_file = 'csvs/cue1_response2_str_filtered_ROOT.csv'
output_file = 'for_site/ukrainian_assoc_data.csv'
zip_file = 'for_site/ukrainian_assoc_data.zip'

# Завантаження даних
df = pd.read_csv(input_file)

# Видалення рядків, де 'SourceWord' або 'TargetWord' містить 'ROOT'
df_filtered = df[~df['SourceWord'].str.contains('ROOT', na=False) & ~df['TargetWord'].str.contains('ROOT', na=False)]

# Створення нового DataFrame у потрібному форматі
df_new = pd.DataFrame({
    'cue': df_filtered['SourceWord'],
    'response': df_filtered['TargetWord'],
    'R': df_filtered['R'],
    'N': df_filtered['N'],
    'R.Strength': df_filtered['R'] / df_filtered['N']
})

# Сортування DataFrame спочатку по стовпцю 'cue', потім по стовпцю 'response'
df_new = df_new.sort_values(by=['cue', 'response'])

# Збереження нового DataFrame у CSV файл
df_new.to_csv(output_file, index=False)

# Створення ZIP архіву
with zipfile.ZipFile(zip_file, 'w') as zipf:
    zipf.write(output_file, os.path.basename(output_file))

print(f'Файл збережено як {zip_file}')
