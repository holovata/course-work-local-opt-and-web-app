import json
import pandas as pd
from word_checker import get_label_by_id


def update_label(label, value):
    """
    Додає " | мітка = " та значення до мітки.

    Args:
        label (str): Початкова мітка.
        value (float): Значення для додавання до мітки.

    Returns:
        str: Оновлена мітка.
    """
    return f"{label} | мітка = {value:.1f}"


def update_edge_label(label, weight):
    """
    Додає " | вага = " та значення ваги до мітки ребра.

    Args:
        label (str): Початкова мітка ребра.
        weight (float): Значення ваги для додавання до мітки.

    Returns:
        str: Оновлена мітка ребра.
    """
    return f"{label} | вага = {weight:.1f}"


def get_edge_properties(file_path, source_id, target_id):
    """
    Отримує властивості weight та label для ребра з CSV файлу на основі source_id та target_id.

    Args:
        file_path (str): Шлях до CSV файлу з даними про ребра.
        source_id (str): ID початкового вузла ребра.
        target_id (str): ID кінцевого вузла ребра.

    Returns:
        dict: Словник з властивостями weight та label для ребра.
    """
    try:
        df = pd.read_csv(file_path, encoding='utf-8')
    except Exception as e:
        print("Помилка при читанні CSV файлу:", e)
        return None

    edge = df[(df['Source'] == int(source_id)) & (df['Target'] == int(target_id))]

    if not edge.empty:
        weight = edge.iloc[0]['Weight']
        label = edge.iloc[0]['Label']
        updated_label = update_edge_label(label, weight)
        return {"weight": weight, "label": updated_label}
    else:
        print(f"Властивості для ребра від {source_id} до {target_id} не знайдені.")
        return {"weight": None, "label": None}


def opt_path_to_json(path, csv_file_path='csvs/nodes12_list.csv', edge_file_path='csvs/cue1_response2_str_filtered_ROOT.csv', json_file_path='jsons/optimized_path.json'):
    """
    Зберігає даний шлях, розділений на вузли та ребра, у JSON файл з мітками вузлів з CSV файлу.

    Args:
        path (list): Шлях для збереження, зазвичай список рядків вузлів з асоційованими значеннями.
        csv_file_path (str): Шлях до CSV файлу, що містить ID та мітки вузлів.
        edge_file_path (str): Шлях до CSV файлу, що містить дані про ребра.
        json_file_path (str): Шлях до JSON файлу, куди мають бути збережені дані.
    """
    nodes = []
    edges = []

    # Витягуємо вузли та їх значення, і отримуємо мітки з CSV
    for i, node in enumerate(path):
        node_id, value = node.split(" (Value: ")
        value = value[:-1]  # Забираємо закриваючу дужку
        value_float = float(value)
        label = get_label_by_id(csv_file_path, node_id)
        updated_label = update_label(label, value_float)
        is_corner = i == 0 or i == len(path) - 1  # Першій та останній вершинам встановлюємо is_corner=True
        nodes.append({"key": node_id, "value": value_float, "label": updated_label, "is_corner": is_corner})

    # Витягуємо ребра на основі послідовних вузлів та отримуємо їх властивості з CSV
    for i in range(len(path) - 1):
        from_node = path[i].split(" (")[0]
        to_node = path[i + 1].split(" (")[0]
        edge_props = get_edge_properties(edge_file_path, from_node, to_node)
        edges.append({"from": from_node, "to": to_node, "weight": edge_props["weight"], "label": edge_props["label"]})

    # Підготовлюємо дані для збереження
    data = {
        "nodes": nodes,
        "edges": edges
    }

    # Записуємо дані в JSON файл
    try:
        with open(json_file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        print("Шлях успішно збережений в", json_file_path)
    except IOError as e:
        print("Помилка при записі до файлу:", e)


'''path_example = ['406 (Value: 0)', '760 (Value: 18.545454545454547)', '697 (Value: 29.177033492822964)', '233 (Value: 36.177033492822964)', '124 (Value: 58.51036682615629)', '405 (Value: 76.09370015948963)']
opt_path_to_json(path_example)'''
