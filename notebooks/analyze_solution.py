import pandas as pd
import geopandas as gpd
import json
from pathlib import Path
from dateutil.parser import parse

def get_data(problem_path, solution_path):
    with open(problem_path) as problem_file:
        problem = json.load(problem_file)

    with open(solution_path) as solution_file:
        solution = json.load(solution_file)

    solution_geo_path = Path(solution_path).with_suffix('.geojson')
    if Path(solution_geo_path).is_file():
        solution_geo = gpd.read_file(solution_geo_path)
    else:
        solution_geo = gpd.GeoDataFrame.from_features([])

    return (normalize_problem(problem), normalize_solution(solution), solution_geo)

def normalize_problem(problem):
    if 'objectives' not in problem:
        problem['objectives'] = {
            'primary': [{'type': 'minimize-unassigned'}, {'type': 'minimize-tours'}],
            'secondary': [{'type': 'minimize-cost'}],
        }

    return problem

def normalize_solution(solution):
    if 'extras' not in solution:
        solution['extras'] = {}

    if not 'metrics' in solution['extras']:
        if 'performance' in solution['extras']:
            generations = len(solution['extras']['performance'])
            duration = solution['extras']['performance'][-1]['timestamp'] - solution['extras']['performance'][0]['timestamp']
            evolution = []
            for iteration in solution['extras']['performance']:
                evolution.append({
                    'number': iteration['number'],
                    'timestamp': iteration['timestamp'],
                    'population': [
                        {
                            "tours": iteration['tours'],
                            "unassigned": iteration['unassigned'],
                            "cost": iteration['cost'],
                            "iAllRatio": iteration['iAllRatio'],
                            "i1000Ratio": iteration['i1000Ratio'],
                            "isImprovement": iteration['isImprovement']
                        }
                    ]
                })
            solution['extras']['metrics'] = {
                'duration': duration,
                'generations': generations,
                'speed': generations / duration,
                'evolution': evolution
            }
        else:
            solution['extras'] = {
                'metrics': {
                    'duration': 0,
                    'generations': 0,
                    'speed': 0,
                    'evolution': []
                }
            }

    if 'unassigned' not in solution:
        solution['unassigned'] = []

    return solution

def extract_problem_statistics(problem):
    df = pd.json_normalize(problem)

    df['total vehicles'] = df.apply(lambda row: sum([len(vehicle['vehicleIds']) for vehicle in row['fleet.vehicles']]), axis=1)

    columns = {'plan.jobs': 'jobs', 'fleet.vehicles': 'vehicle types', 'fleet.profiles': 'vehicle profiles', 'plan.relations': 'relations'}
    for key, value in columns.items():
        if key in df.columns:
            df[key] = df.apply(lambda row: len(row[key]), axis=1)
        else:
            df[key] = 0

    df = df.rename(columns, axis=1)
    df = df.drop(['objectives.primary', 'objectives.secondary'], axis=1)

    return df


def extract_problem_objectives(problem):
    df_1 = pd.json_normalize(problem, record_path=['objectives', 'primary']).assign(priority='primary')
    df_2 = pd.json_normalize(problem, record_path=['objectives', 'secondary']).assign(priority='secondary')

    df = df_1.append(df_2, sort=False)
    df = df.reset_index()

    return df

def extract_jobs_statistics(problem):
    def get_tasks_statistic(tasks):
        max_duration = 0
        max_tw_duration = 0
        max_demand = []
        for task in tasks:
            for place in task['places']:
                max_duration = place['duration']
                max_tw_duration = max(max_tw_duration, max([(parse(end) - parse(start)).seconds for start, end in place.get('times', [])], default = 0))
            max_demand = task['demand']

        return max_demand, max_duration, max_tw_duration

    def get_job_statistics(job):
        max_demand1, max_duration1, max_tw_duration1 = get_tasks_statistic(job.get('pickups', {}))
        max_demand2, max_duration2, max_tw_duration2 = get_tasks_statistic(job.get('deliveries', {}))
        
        return max(max_demand1, max_demand2), max(max_duration1, max_duration2), max(max_tw_duration1, max_tw_duration2)

    jobs=[]
    for job in problem['plan']['jobs']:
        max_demand, max_duration, max_tw_duration = get_job_statistics(job)
        jobs.append({
            'id': job['id'], 
            'deliveries': len(job.get('deliveries', [])), 
            'pickups': len(job.get('pickups', [])),
            'replacements': len(job.get('replacements', [])),
            'services': len(job.get('services', [])),
            'demand': max_demand,
            'service time duration': max_duration,
            'time window duration': max_tw_duration,
        })
        

    return pd.json_normalize(jobs)

def extract_vehicle_statistics(problem):
    df_1 = pd.json_normalize(problem['fleet']['vehicles'], record_path=['shifts'])

    for key in ['breaks', 'reloads']:
        if key in df_1.columns:
            df_1[key] = df_1.apply(lambda row: len(row[key]), axis=1)
        else:
            df_1[key] = df_1.apply(lambda row: 0, axis=1)
            

    df_1['start location'] = df_1.apply(lambda row: '{},{}'.format(row['start.location.lat'], row['start.location.lng']), axis=1)
    df_1['start time'] = df_1.apply(lambda row: row['start.earliest'], axis=1)
    if 'end.location.lat' in df_1.columns:
        df_1['end location'] = df_1.apply(lambda row: '{},{}'.format(row['end.location.lat'], row['end.location.lng']), axis=1)
        df_1['end time'] = df_1.apply(lambda row: row['end.latest'], axis=1)
        
    df_1.drop(list(df_1.filter(regex = 'start\.|end\.')), axis = 1, inplace = True)


    df_2 = pd.json_normalize(problem['fleet']['vehicles'])[['typeId', 'vehicleIds', 'capacity']]
    df_2['vehicleIds'] = df_2.apply(lambda row: len(row['vehicleIds']), axis=1)


    df = pd.concat([df_2, df_1], axis=1)
    df = df.rename({'vehicleIds': 'available', 'typeId': 'type'}, axis=1)

    return df


def extract_solution_statistics(solution):
    df = pd.json_normalize(solution)
    df.columns = df.columns.str.replace('statistic.', '')
    df.columns = df.columns.str.replace('times.', '')

    df.drop(list(df.filter(regex = 'extras')), axis = 1, inplace = True)
    df['tours'] = df.apply(lambda row: len(row.tours), axis=1)
    df['unassigned'] = df.apply(lambda row: len(row.unassigned), axis=1)

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

    df['start'] = df.apply(lambda row: row.stops[0]['time']['departure'], axis=1)
    df['finish'] = df.apply(lambda row: row.stops[-1]['time']['departure'], axis=1)

    df['stops'] = df.apply(lambda row: len(row.stops), axis=1)

    return df

def extract_evolution_metrics(objectives, solution):
    """
    Extracts metrics data for solution
    """
    evolution = solution['extras']['metrics']['evolution']

    if len(evolution) != 0:
        df = pd.json_normalize(evolution, record_path=['population'], meta=['number', 'timestamp'])
        df = df.drop_duplicates(subset='number', keep="first")
        df = df.reset_index()

        df_fit = pd.DataFrame([pd.Series(x) for x in df.fitness])
        df_fit.columns = [objectives.type[x] for x in df_fit.columns]

        df = pd.concat([df, df_fit], axis=1, sort=False)

        return df.drop(['improvement', 'fitness'], axis=1)
    else:
        return pd.DataFrame(columns = ['timestamp', 'number'])
