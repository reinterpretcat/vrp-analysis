import pandas as pd

def get_configs(df):
    """
    Gets all config names
    """
    configs = df['Config'].unique()
    configs.sort()
    return configs

def get_problems(df):
    """
    Gets all problem names
    """
    problems = df['Problem'].unique()
    problems.sort()
    return problems


def extract_columns(df, config_name, problem_name, target_columns):
    """
    Extracts columns data for specific config and problem with new labels
    """
    column = df.loc[(df['Config'] == config_name) & (df['Problem'] == problem_name)]
    column = column[target_columns].reset_index(drop=True)

    return column