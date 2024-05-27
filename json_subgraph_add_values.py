import json
from local_optimization import local_optimize_graph, read_graph_from_csv, initialize_graph
from create_subgraph import create_subgraph_based_on_degree


def modify_json_data(source_file, destination_file):
    """Reads JSON, modifies data, and saves the result."""
    try:
        with open(source_file, 'r', encoding='utf-8') as file:
            data = json.load(file)

        for node in data['nodes']:
            node['attributes']['is_in_path'] = False
            node['attributes']['value'] = "inf"

        for edge in data['edges']:
            edge['attributes']['is_in_path'] = False
            weight = edge['attributes']['weight']
            edge['attributes']['label'] += f" | вага = {weight:.1f}"

        with open(destination_file, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
        print(f"Modified data saved to {destination_file}")

    except Exception as e:
        print(f"Error processing file: {e}")


def set_initial_values(G, start_node):
    for n in G:
        G.nodes[n]['value'] = "inf"
    G.nodes[start_node]['value'] = 0


def update_is_in_path(input_file, output_file, path):
    """Updates JSON data for the path and saves the final results."""
    try:
        with open(input_file, 'r', encoding='utf-8') as file:
            data = json.load(file)

        # Отримання ідентифікаторів вузлів зі шляху
        node_ids = [int(node.split(" ")[0]) for node in path]

        # Встановлення значень атрибутів для вузлів
        for node in data['nodes']:
            if int(node['key']) in node_ids:
                node['attributes']['is_in_path'] = True
                node['attributes']['value'] = None  # or another calculated value, depending on context

        # Встановлення атрибутів тільки для ребер, які з'єднують сусідні вузли у шляху
        for i in range(len(node_ids) - 1):
            from_node = node_ids[i]
            to_node = node_ids[i + 1]
            for edge in data['edges']:
                if int(edge['source']) == from_node and int(edge['target']) == to_node:
                    edge['attributes']['is_in_path'] = True

        # Збереження кінцевого JSON файла
        with open(output_file, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
        print(f"Final data saved to {output_file}")

    except Exception as e:
        print(f"Error updating and saving JSON: {e}")


def update_values_and_labels(input_file, output_file, graph):
    try:
        with open(input_file, 'r', encoding='utf-8') as file:
            data = json.load(file)

        # Обновление значений для всех вершин
        for node in data['nodes']:
            node_key = int(node['key'])
            # Получение значения узла из графа, с предварительной проверкой на бесконечность
            node_value = graph.nodes[node_key].get('value')
            if node_value is None or node_value == float('inf'):
                node_value_str = 'inf'
            else:
                node_value_str = f"{node_value:.1f}"  # Округление до 1 знака после запятой

            # Установка значения 'value' и обновление 'label'
            node['attributes']['value'] = node_value_str
            node['attributes']['label'] += f" | мітка = {node_value_str}"

        with open(output_file, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
        print("Updated values and labels in JSON successfully.")

    except Exception as e:
        print(f"Error while updating values and labels in JSON: {e}")


def update_json_with_path_and_save(input_file, output_file, path):
    """Updates JSON data for the path and saves the final results."""
    try:
        with open(input_file, 'r', encoding='utf-8') as file:
            data = json.load(file)

        # Отримання ідентифікаторів вузлів зі шляху
        node_ids = [int(node.split(" ")[0]) for node in path]

        # Встановлення значень атрибутів для вузлів
        for node in data['nodes']:
            if int(node['key']) in node_ids:
                node['attributes']['is_in_path'] = True
                node['attributes']['value'] = None  # or another calculated value, depending on context

        # Встановлення атрибутів тільки для ребер, які з'єднують сусідні вузли у шляху
        for i in range(len(node_ids) - 1):
            from_node = node_ids[i]
            to_node = node_ids[i + 1]
            for edge in data['edges']:
                if int(edge['source']) == from_node and int(edge['target']) == to_node:
                    edge['attributes']['is_in_path'] = True

        # Збереження кінцевого JSON файла
        with open(output_file, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
        print(f"Final data saved to {output_file}")

    except Exception as e:
        print(f"Error updating and saving JSON: {e}")


if __name__ == "__main__":
    source_path = 'jsons/subgraph_gephi.json'
    no_values_path = 'jsons/subgraph_no_values.json'
    with_values_path = 'jsons/subgraph_with_values.json'
    modify_json_data(source_path, no_values_path)

    # full_edges_path = 'csvs/cue1_response2_str_filtered_ROOT.csv'
    # df_full = read_graph_from_csv(full_edges_path)
    # full_graph = initialize_graph(df_full)
    # subgraph = create_subgraph_based_on_degree(full_graph, 25)

    # opt_graph, path = local_optimize_graph(subgraph, 406, 222)
    # path = ['406 (Value: 0)', '257 (Value: 34.0)', '832 (Value: 87.0)', '222 (Value: 129.4)']

    # update_values_and_labels(no_values_path, with_values_path, opt_graph)
    # update_json_with_path_and_save(no_values_path, with_values_path, path)
    # update_is_in_path(no_values_path, with_values_path, path)
