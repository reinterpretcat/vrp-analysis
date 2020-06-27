import pandas as pd

def get_configs(df):
    """
    Gets all config names
    """
    return df['Config'].unique()

def get_problems(df):
    """
    Gets all problem names
    """
    return df['Problem'].unique()


def extract_columns(df, config_name, problem_name, target_columns, new_labels):
    """
    Extracts columns data for specific config and problem with new labels
    """
    columns = {}
    for idx, target_column in enumerate(target_columns):
        columns[target_column] = new_labels[idx]

    column = df.loc[(df['Config'] == config_name) & (df['Problem'] == problem_name)]
    column = column[target_columns].rename(columns = columns).reset_index(drop=True)

    return column