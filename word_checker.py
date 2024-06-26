import pandas as pd


def get_id_by_name(file_path, target_word):
    # Зчитування CSV-файлу у DataFrame
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        print(f"Помилка: файл не знайдено - {file_path}")
        return None

    # Перевірка на наявність колонок 'Name' і 'Id' у DataFrame
    if 'Name' not in df.columns or 'Id' not in df.columns:
        print("Помилка: DataFrame не містить необхідних колонок 'Name' або 'Id'")
        return None

    # Пошук точного збігу слова у колонці 'Name'
    exact_match = df[df['Name'].str.strip() == target_word.strip()]
    if not exact_match.empty:
        # Повернення першого ID, де знайдений точний збіг
        return exact_match.iloc[0]['Id']
    return None

def get_name_by_id(file_path, target_id):
    # Зчитування CSV-файлу у DataFrame
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        print(f"Помилка: файл не знайдено - {file_path}")
        return None

    # Перевірка на наявність колонок 'Id' та 'Name' у DataFrame
    if 'Id' not in df.columns or 'Name' not in df.columns:
        print("Помилка: DataFrame не містить необхідних колонок 'Id' або 'Name'")
        return None

    # Пошук рядка, де Id збігається з target_id
    match = df[df['Id'] == target_id]
    if not match.empty:
        # Повернення першого значення Name, яке збігається
        return match['Name'].iloc[0]
    return None


def get_label_by_id(file_path, node_id):
    """
    Retrieves the label of a node from a CSV file based on the node's ID.

    Args:
        file_path (str): Path to the CSV file containing the node data.
        node_id (int or str): The ID of the node for which to retrieve the label.

    Returns:
        str: The label associated with the given node ID, or None if not found.
    """
    # Load the CSV file
    try:
        df = pd.read_csv(file_path)
        print(f"CSV loaded successfully. Columns: {df.columns.tolist()}")
    except Exception as e:
        print("Failed to read the CSV file:", e)
        return None

    # Ensure IDs are stripped of leading/trailing spaces
    df['Id'] = df['Id'].astype(str).str.strip()
    node_id = str(node_id).strip()

    # Filter the DataFrame for the given node ID
    result = df[df['Id'] == node_id]
    print(f"Searching for ID: {node_id}. Result: {result}")

    # Check if the node ID was found and return the label
    if not result.empty:
        return result.iloc[0]['Label']
    else:
        print(f"No label found for ID: {node_id}")
        return None
