import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from concurrent.futures import ThreadPoolExecutor, as_completed


# Зчитування графу з CSV файлу
def read_graph_from_csv(file_path):
    df = pd.read_csv(file_path)
    return df


# Ініціалізація орієнтованого графа з DataFrame
def initialize_graph(df):
    G = nx.DiGraph()
    # Додавання дуг з усіма атрибутами, включно з SourceWord і TargetWord
    for index, row in df.iterrows():
        G.add_edge(row['Source'], row['Target'], weight=row['Weight'], R=row['R'], N=row['N'],
                   Label=row['Label'], SourceWord=row['SourceWord'], TargetWord=row['TargetWord'])
    return G


# Встановлення початкових значень для вершин
def set_initial_values(G, start_node):
    for n in G:
        G.nodes[n]['value'] = float('inf')
    G.nodes[start_node]['value'] = 0


# Мінімізація значення для однієї вершини
def minimize_value(G, node):
    current_value = G.nodes[node]['value']
    best_predecessor = None
    new_value = float('inf')
    for n in G.predecessors(node):
        value = G.nodes[n]['value'] + G[n][node]['weight']
        if value < new_value:
            new_value = value
            best_predecessor = n
    return new_value, best_predecessor, new_value < current_value


# Паралельна оптимізація графа
def parallel_optimization(G, start_node, max_iterations=100):
    changed = True
    iteration = 0
    path = {node: None for node in G.nodes()}
    while changed and iteration < max_iterations:
        changed = False
        with ThreadPoolExecutor(max_workers=len(G.nodes())) as executor:
            futures = {executor.submit(minimize_value, G, node): node for node in G.nodes() if node != start_node}
            results = {}
            for future in as_completed(futures):
                node = futures[future]
                new_value, best_predecessor, updated = future.result()
                results[node] = (new_value, best_predecessor, updated)
                if updated:
                    changed = True
        for node, (new_value, best_predecessor, updated) in results.items():
            if updated:
                G.nodes[node]['value'] = new_value
                path[node] = best_predecessor
        iteration += 1
    return G, path


# Реконструкція шляху
def reconstruct_path(G, all_paths, start_node, end_node):
    if end_node not in all_paths or all_paths[end_node] is None:
        # Return only the start node if no path to the end node exists
        node_value = G.nodes[start_node]['value']
        return [f"{start_node} (Value: {node_value})"]

    reversed_path = []
    current = end_node
    while current != start_node:
        node_value = G.nodes[current]['value']
        reversed_path.append(f"{current} (Value: {node_value})")
        current = all_paths[current]
        if current is None:
            break
    node_value = G.nodes[start_node]['value']
    reversed_path.append(f"{start_node} (Value: {node_value})")
    reversed_path.reverse()
    return reversed_path


# Локальна оптимізація графа
def local_optimize_graph(G, start_node):
    try:
        '''if start_node not in G.nodes() or end_node not in G.nodes():
            print(f"Одна або обидві вершини {start_node}, {end_node} відсутні в графі.")
            return None, None  # Return None if either node is missing'''

        set_initial_values(G, start_node)
        optimized_graph, all_paths = parallel_optimization(G, start_node)
        '''for node, data in sorted(optimized_graph.nodes(data=True), key=lambda x: x[0]):
            shortest_path = reconstruct_path(optimized_graph, path, start_node, node)
            print(f"Вершина {node}: {data['value']}, Шлях: {shortest_path}")'''

        '''print(f"Специфічний шлях від {start_node} до {end_node}:")
        specific_path = reconstruct_path(optimized_graph, path, start_node, end_node)
        print(specific_path)'''

        print(f"Загальна кількість вершин: {optimized_graph.number_of_nodes()}")
        print(f"Загальна кількість дуг: {optimized_graph.number_of_edges()}")

        return optimized_graph, all_paths
    except ValueError:
        print("Невалідний ввід: введіть правильні цілі числа для ID вершин.")
        return None, None


if __name__ == "__main__":
    csv_file_path = 'csvs/cue1_response2_str_filtered_ROOT.csv'
    df = read_graph_from_csv(csv_file_path)
    G = initialize_graph(df)

    # Визначення початкової та кінцевої вершини для прикладу
    start_node = 1
    end_node = 10
    # set_initial_values(G, start_node)
    optimized_graph, path = local_optimize_graph(G, start_node)
    # optimized_graph, path = parallel_optimization(G, start_node)
    if path:
        print("Оптимізований шлях:", path)
    else:
        print("Шлях не знайдено.")

