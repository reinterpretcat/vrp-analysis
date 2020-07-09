import pandas as pd


def extract_evolution_metrics(solution):
    """
    Extracts metrics data for solution
    """
    df = pd.json_normalize(solution['extras']['metrics']['evolution'], record_path=['population'], meta=['number', 'timestamp'])
    df = df.drop_duplicates(subset='number', keep="first")
    df = df.reset_index()

    df_fit = pd.DataFrame([pd.Series(x) for x in df.fitness])
    df_fit.columns = ['fitness_{}'.format(x+1) for x in df_fit.columns]

    df = pd.concat([df, df_fit], axis=1, sort=False)

    df = df.drop(['improvement', 'fitness'], axis=1)
    
    
    return df


def extract_tours_statistic(solution):
    """
    Extracts statistic data for all tours
    """
    df = pd.json_normalize(solution['tours']).drop('stops', axis=1)  
    df.columns = df.columns.str.replace('statistic.', '')
    df.columns = df.columns.str.replace('times.', '')

    return df