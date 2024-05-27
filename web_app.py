import json
from flask import Flask, render_template, jsonify, request
from word_checker import get_id_by_name
from local_optimization import local_optimize_graph, read_graph_from_csv, initialize_graph, extract_edges_for_path
from json_subgraph_add_values import update_values_and_labels, update_is_in_path
from create_subgraph import create_subgraph_based_on_degree
import pandas as pd
from opt_path_to_json import opt_path_to_json

app = Flask(__name__)


# Load the JSON file safely and initialize graphs on startup
try:
    with open('jsons/subgraph_no_values.json', 'r', encoding='utf-8') as file:
        graph_data = json.load(file)
    # Load and initialize the full graph from CSV files at startup
    full_edges_path = 'csvs/cue1_response2_str_filtered_ROOT.csv'
    full_nodes_path = 'csvs/nodes12_list.csv'
    df_full = read_graph_from_csv(full_edges_path)
    full_graph = initialize_graph(df_full)

    subgraph_with_path = 'jsons/subgraph_with_values.json'
    subgraph_no_path = 'jsons/subgraph_no_values.json'
    subgraph_nodes_path = 'csvs/subgraph_1_2_nodes.csv'
    subgraph_edges_path = 'csvs/subgraph_1_2_edges.csv'
    subgraph = create_subgraph_based_on_degree(full_graph, 25)
    # Load SVG file content
    with open('static/svg/full_graph.svg', 'r', encoding='utf-8') as file:
        svg_content = file.read()
    app.logger.info("Graph and JSON data loaded successfully.")
except Exception as e:
    app.logger.error(f"Failed to initialize graph or load graph data: {e}")
    graph_data = {}  # Default to an empty graph if loading fails


@app.route('/')
def home():
    return render_template('index.html', active_page='home')


@app.route('/graph_data')
def graph_data_route():
    return jsonify(graph_data)


@app.route('/demo')
def demo():
    return render_template('demo.html', active_page='demo')


@app.route('/words')
def get_words():
    try:
        df = pd.read_csv(subgraph_nodes_path)
        words = df[['Name', 'Label']].to_dict(orient='records')
        return jsonify(words)
    except Exception as e:
        app.logger.error(f"Failed to read words from CSV: {e}")
        return jsonify({"error": "Failed to load words"}), 500


@app.route('/optimize_subgraph', methods=['POST'])
def optimize_subgraph():
    word1 = request.form.get('word1', '')
    word2 = request.form.get('word2', '')
    try:
        word1_id = get_id_by_name(subgraph_nodes_path, word1)
        word2_id = get_id_by_name(subgraph_nodes_path, word2)

        optimized_subgraph, sub_path = local_optimize_graph(subgraph, word1_id, word2_id)

        update_values_and_labels(subgraph_no_path, subgraph_with_path, optimized_subgraph)  # Обновляем значения для всех узлов
        update_is_in_path(subgraph_with_path, subgraph_with_path, sub_path)  # Обновляем is_in_path только для узлов в пути

        if sub_path is None or len(sub_path) == 1:  # Проверяем, есть ли путь или он очень короткий
            message = f"Не існує шляху між {word1} та {word2}, або введені слова є однаковими."
            return jsonify({"status": "warning", "message": message})

        return jsonify({"status": "success", "message": "Проведена оптимізація підграфу."})
    except Exception as e:
        error_message = str(e)
        app.logger.error("Помилка при оптимізації підграфу: " + error_message)
        return jsonify({"status": "error", "message": "Помилка при оптимізації підграфу: " + error_message})


@app.route('/graph_data_with_path')
def graph_data_with_path():
    try:
        with open(subgraph_with_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return jsonify(data)
    except Exception as e:
        app.logger.error(f"Failed to load or parse 'subgraph_with_values.json': {e}")
        return jsonify({"error": "Failed to load resource"}), 500


@app.route('/optimize_graph', methods=['POST'])
def optimize_graph():
    word1 = request.form['word1']
    word2 = request.form['word2']

    # Check if the two words are the same
    if word1 == word2:
        return jsonify({"status": "error", "message": "Введені слова ідентичні."})

    try:
        word1_id = get_id_by_name(full_nodes_path, word1)
        word2_id = get_id_by_name(full_nodes_path, word2)

        if not word1_id or not word2_id:
            return jsonify({"status": "error", "message": "Одне чи обидва слова не наявні в мережі."})

        optimized_graph, path = local_optimize_graph(full_graph, word1_id, word2_id)

        if path is None or not path:
            return jsonify({"status": "warning", "message": "Немає шляху між введеними словами."})

        path_display = " -> ".join(str(node) for node in path)
        opt_path_to_json(path)
        return jsonify({"status": "success", "message": "Проведена оптимізація графу.", "path": path_display})
    except Exception as e:
        error_message = str(e)
        app.logger.error("Помилка при оптимізації графу: " + error_message)
        return jsonify({"status": "error", "message": "Помилка при оптимізації графу: " + error_message})


@app.route('/optimized_path_intro_data')
def optimized_path_intro_data():
    try:
        with open('jsons/optimized_path_intro.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
        return jsonify(data)
    except Exception as e:
        app.logger.error(f"Failed to load 'optimized_path_intro.json': {e}")
        return jsonify({"error": "Failed to load optimized path introduction data"}), 500

# Assuming you already have optimized_path_data route for optimized_path.json


@app.route('/optimized_path_data')
def optimized_path_data():
    try:
        with open('jsons/optimized_path.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
        # Ensure data structure is correct
        if 'nodes' not in data:
            data['nodes'] = []
        if 'edges' not in data:
            data['edges'] = []
        app.logger.info(f"Optimized path data loaded successfully: {data}")
        return jsonify(data)
    except Exception as e:
        app.logger.error(f"Failed to load 'optimized_path.json': {e}")
        return jsonify({"error": "Failed to load optimized path data"}), 500


@app.route('/shortest_path')
def shortest_path():
    return render_template('shortest_path.html', active_page='shortest_path')


@app.route('/visualization')
def visualization():
    return render_template('visualization.html', active_page='visualization', svg_content=svg_content)



if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
