import pandas as pd
from local_optimization import read_graph_from_csv, initialize_graph, local_optimize_graph


# Збереження інформації про ребра підграфа у CSV файл
def save_subgraph_edges_to_csv(G, subgraph, output_file_path):
    # Створення списку словників для кожного ребра з усіма необхідними атрибутами
    edge_data = [{
        'Source': u,
        'Target': v,
        'SourceWord': data['SourceWord'],
        'TargetWord': data['TargetWord'],
        'R': data['R'],
        'N': data['N'],
        'Weight': data['weight'],
        'Label': data['Label']
    } for u, v, data in subgraph.edges(data=True)]

    # Конвертація списку словників у DataFrame
    df_edges = pd.DataFrame(edge_data)

    # Збереження DataFrame у CSV
    df_edges.to_csv(output_file_path, index=False)
    print(f"Інформація про ребра підграфа збережена до {output_file_path}")


# Збереження інформації про вузли підграфа у CSV файл
def save_subgraph_nodes_to_csv(graph_nodes, subgraph_nodes, output_csv_file):
    # Гарантування, що ID вузлів підграфа правильно сформатовані у список
    subgraph_node_ids = list(subgraph_nodes)

    # Фільтрація DataFrame так, щоб включати лише вузли з підграфа
    subgraph_df = graph_nodes[graph_nodes['Id'].isin(subgraph_node_ids)]

    if subgraph_df.empty:
        print("Фільтрований DataFrame вузлів пустий. Перевірте ID вузлів та їх форматування.")
        return

    # Збереження відфільтрованого DataFrame до нового CSV файлу
    subgraph_df.to_csv(output_csv_file, index=False)
    print(f"Вузли підграфа збережено до {output_csv_file}")


# Створення підграфа на основі ступеня вузлів
def create_subgraph_based_on_degree(G, num_nodes):
    # Сортування вузлів за ступенем у порядку спадання
    sorted_nodes_by_degree = sorted(G.degree, key=lambda x: x[1], reverse=True)
    top_nodes = [node for node, degree in sorted_nodes_by_degree[:num_nodes]]
    subgraph = G.subgraph(top_nodes).copy()

    # Виведення інформації про вузли та ребра підграфа
    print("Вузли підграфа:", subgraph.nodes())
    print("Ребра підграфа:")
    for u, v, data in subgraph.edges(data=True):
        print(f"{u} -> {v} з вагою {data['weight']}")

    return subgraph


if __name__ == "__main__":
    full_nodes_csv_path = 'csvs/nodes12_list.csv'
    G_nodes = pd.read_csv(full_nodes_csv_path)
    subgraph_nodes_csv_path = 'csvs/subgraph_1_2_nodes.csv'

    csv_file_path = 'csvs/cue1_response2_str_filtered_ROOT.csv'
    output_csv_file_path = 'csvs/subgraph_1_2_edges.csv'
    df = read_graph_from_csv(csv_file_path)
    G = initialize_graph(df)

    subgraph = create_subgraph_based_on_degree(G, 25)
    save_subgraph_edges_to_csv(G, subgraph, output_csv_file_path)

    optimized_subgraph, path = local_optimize_graph(subgraph, start_node=255, end_node=630)
    # update_json_file(optimized_subgraph, path, 'jsons/subgraph_with_values.json')
