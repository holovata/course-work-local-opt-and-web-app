import json
import pandas as pd
from word_checker import get_label_by_id

def update_label(label, value):
    """
    Добавляет " | мітка = " и значение к метке.

    Args:
        label (str): Исходная метка.
        value (float): Значение для добавления к метке.

    Returns:
        str: Обновленная метка.
    """
    return f"{label} | мітка = {value}"

def update_edge_label(label, weight):
    """
    Добавляет " | вага = " и значение веса к метке ребра.

    Args:
        label (str): Исходная метка ребра.
        weight (float): Значение веса для добавления к метке.

    Returns:
        str: Обновленная метка ребра.
    """
    return f"{label} | вага = {weight}"

def get_edge_properties(file_path, source_id, target_id):
    """
    Получает свойства weight и label для ребра из CSV файла на основе source_id и target_id.

    Args:
        file_path (str): Путь к CSV файлу с данными о ребрах.
        source_id (str): ID начального узла ребра.
        target_id (str): ID конечного узла ребра.

    Returns:
        dict: Словарь со свойствами weight и label для ребра.
    """
    try:
        df = pd.read_csv(file_path, encoding='utf-8')
    except Exception as e:
        print("Ошибка при чтении CSV файла:", e)
        return None

    edge = df[(df['Source'] == int(source_id)) & (df['Target'] == int(target_id))]

    if not edge.empty:
        weight = edge.iloc[0]['Weight']
        label = edge.iloc[0]['Label']
        updated_label = update_edge_label(label, weight)
        return {"weight": weight, "label": updated_label}
    else:
        print(f"Свойства для ребра от {source_id} к {target_id} не найдены.")
        return {"weight": None, "label": None}

def opt_path_to_json(path, csv_file_path='csvs/nodes12_list.csv', edge_file_path='csvs/cue1_response2_str_filtered_ROOT.csv', json_file_path='jsons/optimized_path.json'):
    """
    Сохраняет данный путь, разделенный на узлы и ребра, в JSON файл с метками узлов из CSV файла.

    Args:
        path (list): Путь для сохранения, обычно список строк узлов с ассоциированными значениями.
        csv_file_path (str): Путь к CSV файлу, содержащему ID и метки узлов.
        edge_file_path (str): Путь к CSV файлу, содержащему данные о ребрах.
        json_file_path (str): Путь к JSON файлу, куда должны быть сохранены данные.
    """
    nodes = []
    edges = []

    # Извлекаем узлы и их значения, и получаем метки из CSV
    for node in path:
        node_id, value = node.split(" (Value: ")
        value = value[:-1]  # Убираем закрывающую скобку
        value_float = float(value)
        label = get_label_by_id(csv_file_path, node_id)
        updated_label = update_label(label, value_float)
        nodes.append({"key": node_id, "value": value_float, "label": updated_label})

    # Извлекаем ребра на основе последовательных узлов и получаем их свойства из CSV
    for i in range(len(path) - 1):
        from_node = path[i].split(" (")[0]
        to_node = path[i + 1].split(" (")[0]
        edge_props = get_edge_properties(edge_file_path, from_node, to_node)
        edges.append({"from": from_node, "to": to_node, "weight": edge_props["weight"], "label": edge_props["label"]})

    # Подготавливаем данные для сохранения
    data = {
        "nodes": nodes,
        "edges": edges
    }

    # Записываем данные в JSON файл
    try:
        with open(json_file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        print("Путь успешно сохранен в", json_file_path)
    except IOError as e:
        print("Ошибка при записи в файл:", e)


# Пример использования
'''path_example = ['406 (Value: 0)', '760 (Value: 18.545454545454547)', '697 (Value: 29.177033492822964)', '233 (Value: 36.177033492822964)', '124 (Value: 58.51036682615629)', '405 (Value: 76.09370015948963)']
opt_path_to_json(path_example)'''
