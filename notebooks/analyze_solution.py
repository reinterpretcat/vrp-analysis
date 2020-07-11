import pandas as pd
import geopandas as gpd
import json
from pathlib import Path

def get_data(problem_path, solution_path):
    with open(problem_path) as problem_file:
        problem = json.load(problem_file)

    with open(solution_path) as solution_file:
        solution = json.load(solution_file)

    solution_geo_path = Path(solution_path).with_suffix('.geojson')
    if Path(solution_geo_path).is_file():
        solution_geo = gpd.read_file(solution_geo_path)

    return (problem, solution, solution_geo)


def extrac_solution_statistics(solution):
    df = pd.json_normalize(solution)
    df.columns = df.columns.str.replace('statistic.', '')
    df.columns = df.columns.str.replace('times.', '')

    df.drop(list(df.filter(regex = 'extras')), axis = 1, inplace = True)
    df['tours'] = df.apply(lambda s: len(s.tours), axis=1)
    df['unassigned'] = df.apply(lambda s: len(s.unassigned), axis=1)

    return df


def extract_tours_statistic(solution):
    """
    Extracts statistic data for all tours
    """
    def count_activity_types(stops, activity_type):
        return sum([1 if a['type'] == activity_type else 0 for stop in stops for a in stop['activities']])

    df = pd.json_normalize(solution['tours'])
    df.columns = df.columns.str.replace('statistic.', '')
    df.columns = df.columns.str.replace('times.', '')

    df.rename(columns = {'shiftIndex': 'shift', 'vehicleId': 'vehicle', 'typeId': 'type'}, inplace=True)

    df['max load'] = df.apply(lambda row: max([stop['load'] for stop in row.stops]), axis=1)

    df['activities'] = df.apply(lambda row: sum(map(lambda stop: len(stop['activities']), row.stops)), axis=1)
    df['deliveries'] = df.apply(lambda row: count_activity_types(row.stops, 'delivery'), axis=1)
    df['pickups'] = df.apply(lambda row: count_activity_types(row.stops, 'pickup'), axis=1)
    df['breaks'] = df.apply(lambda row: count_activity_types(row.stops, 'break'), axis=1)
    df['reloads'] = df.apply(lambda row: count_activity_types(row.stops, 'reload'), axis=1)

    df['departure'] = df.apply(lambda row: row.stops[0]['time']['departure'], axis=1)
    df['arrival'] = df.apply(lambda row: row.stops[-1]['time']['departure'], axis=1)

    df['stops'] = df.apply(lambda row: len(row.stops), axis=1)

    return df

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