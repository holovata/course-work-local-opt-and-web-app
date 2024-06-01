import json
import os
from flask import Flask, render_template, jsonify, request, send_from_directory
from word_checker import get_id_by_name
from local_optimization import local_optimize_graph, read_graph_from_csv, initialize_graph, reconstruct_path
from json_subgraph_add_values import update_values_and_labels, update_is_in_path
from create_subgraph import create_subgraph_based_on_degree
import pandas as pd
from opt_path_to_json import opt_path_to_json

app = Flask(__name__)

global optimized_graph, all_paths, first_word_id
full_nodes_count = 3892

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


@app.route('/words_full')
def get_words_full():
    try:
        df = pd.read_csv(full_nodes_path)
        words = df[['Name', 'Label']].to_dict(orient='records')
        return jsonify(words)
    except Exception as e:
        app.logger.error(f"Failed to read words from CSV: {e}")
        return jsonify({"error": "Failed to load words"}), 500


@app.route('/words_sub')
def get_words_sub():
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

        optimized_subgraph, all_paths = local_optimize_graph(subgraph, word1_id)
        sub_path = reconstruct_path(subgraph, all_paths, word1_id, word2_id)

        update_values_and_labels(subgraph_no_path, subgraph_with_path, optimized_subgraph)
        update_is_in_path(subgraph_with_path, subgraph_with_path, sub_path)

        if sub_path is None or len(sub_path) == 1:
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
    global optimized_graph, all_paths, first_word_id

    word1 = request.form['word1']
    word2 = request.form['word2']

    # Check if the two words are the same
    if (word1 == word2):
        return jsonify({"status": "error", "message": "Введені слова ідентичні."})

    try:
        word1_id = get_id_by_name(full_nodes_path, word1)
        word2_id = get_id_by_name(full_nodes_path, word2)

        if word1_id is None or word2_id is None:
            return jsonify({"status": "error", "message": "Одне чи обидва слова не наявні в мережі."})

        optimized_graph, all_paths = local_optimize_graph(full_graph, word1_id)
        path = reconstruct_path(full_graph, all_paths, word1_id, word2_id)
        first_word_id = word1_id

        if path is None or not path:
            return jsonify({"status": "warning", "message": "Немає шляху між введеними словами."})

        path_display = " -> ".join(str(node) for node in path)
        opt_path_to_json(path)
        return jsonify({"status": "success", "message": "Проведена оптимізація графу.", "path": path_display})
    except Exception as e:
        error_message = str(e)
        app.logger.error("Помилка при оптимізації графу: " + error_message)
        return jsonify({"status": "error", "message": "Помилка при оптимізації графу: " + error_message})


@app.route('/optimize_new_second_word', methods=['POST'])
def optimize_new_second_word():
    global optimized_graph, all_paths, first_word_id

    new_second_word = request.form['newSecondWord']

    try:
        new_second_word_id = get_id_by_name(full_nodes_path, new_second_word)

        if new_second_word_id is None:
            return jsonify({"status": "error", "message": "Слово не наявне в мережі."})

        path = reconstruct_path(optimized_graph, all_paths, first_word_id, new_second_word_id)

        if path is None or not path:
            return jsonify({"status": "warning", "message": "Немає шляху між введеними словами."})

        path_display = " -> ".join(str(node) for node in path)
        opt_path_to_json(path)
        return jsonify({"status": "success", "message": "Шлях реконструйовано.", "path": path_display})
    except Exception as e:
        error_message = str(e)
        app.logger.error("Помилка при реконструкції шляху: " + error_message)
        return jsonify({"status": "error", "message": "Помилка при реконструкції шляху: " + error_message})


@app.route('/optimized_path_intro_data')
def optimized_path_intro_data():
    try:
        with open('jsons/optimized_path_intro.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
        return jsonify(data)
    except Exception as e:
        app.logger.error(f"Failed to load 'optimized_path_intro.json': {e}")
        return jsonify({"error": "Failed to load optimized path introduction data"}), 500


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


@app.route('/download_assoc_data')
def download_assoc_data():
    zip_path = 'for_site/ukrainian_assoc_data.zip'
    try:
        return send_from_directory(directory='for_site', path=os.path.basename(zip_path), as_attachment=True)
    except Exception as e:
        app.logger.error(f"Failed to send file: {e}")
        return jsonify({"error": "Failed to send file"}), 500


def save_all_paths_to_file():
    global all_paths, full_nodes_count
    try:
        with open('for_site/all_paths.txt', 'w', encoding='utf-8') as file:
            for i in range(full_nodes_count):
                path = reconstruct_path(full_graph, all_paths, first_word_id, i)
                if path:
                    path_display = " -> ".join(str(node) for node in path)
                    file.write(f"Path from {first_word_id} to {i}: {path_display}\n")
        app.logger.info("All paths have been successfully saved to 'for_site/all_paths.txt'.")
    except Exception as e:
        app.logger.error(f"Failed to save all paths to file: {e}")


@app.route('/download_all_paths', methods=['POST'])
def download_all_paths():
    try:
        save_all_paths_to_file()
        return jsonify({"status": "success", "message": "Всі шляхи успішно збережені."})
    except Exception as e:
        app.logger.error(f"Failed to save all paths: {e}")
        return jsonify({"status": "error", "message": f"Не вдалося зберегти всі шляхи: {e}"})


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)