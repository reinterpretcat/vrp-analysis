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


def extract_column(df, config_name, problem_name, target_column, new_label):
    """
    Extracts a single column data for specific config and problem with new label
    """
    column = df.loc[(df['Config'] == config_name) & (df['Problem'] == problem_name)]
    column = column[[target_column]].rename(columns = {target_column: new_label}).reset_index(drop=True)
    return column