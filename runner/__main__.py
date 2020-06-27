import csv
import json
import sys
import glob
from pathlib import Path
from Helpers import Generic
from SolverClient import SolverClient

# if len(sys.argv) < 2:
#     print("Provide path to experiment config")
#     sys.exit(1)
# else:
#     config_path = sys.argv[1]

config_path = "/home/builuk/playground/vrp-analysis/data/experiments/example.json"


# read config
print ("reading config from: ", config_path)
with open(config_path, 'r') as f:
    config_str = f.read()
    config = json.loads(config_str, object_hook=Generic.from_dict)

# get list of problems
problem_files = sum([ glob.glob(it) for it in config.data.problems], [])
print("problems:", problem_files)

# get list of configs
config_files = sum([glob.glob(it) for it in config.data.configs], [])
print("configs:", config_files)

# create and run solver
solver = SolverClient(config.runner.cli)
solutions = {}
iteration = 0
total_iterations = len(problem_files) * len(config_files) * config.runner.samples
for problem_path in problem_files:
    print("run '{}' with {} config(-s)".format(problem_path, len(config_files)))
    problem_file_name = Path(problem_path).stem
    for config_path in config_files:
        config_file_name = Path(config_path).stem
        out_dir = "{}/{}_{}".format(config.data.outDir, config_file_name, problem_file_name)
        Path(out_dir).mkdir(parents = True, exist_ok=True)

        for attempt in range(config.runner.samples):
            iteration += 1
            print("iteration {} of {}, config: '{}', problem: '{}'".format(iteration, total_iterations,
                config_file_name, problem_file_name))
            solution_path = "{}/solution_{}.json".format(out_dir, attempt)
            solution = solver.solve(problem_path, config_path, solution_path)
            solutions.setdefault((config_file_name, problem_file_name), []).append(solution)


# create csv for best-known solution analysis
with open("{}/best_known_solutions.csv".format(config.data.outDir), mode='w') as best_known_file:
    best_known_writer = csv.writer(best_known_file, delimiter=',', quotechar='"',  quoting=csv.QUOTE_MINIMAL)
    best_known_writer.writerow(["Config", "Problem", "Sequence", "Duration", "Generations", "Speed", "Cost", "Waiting", "Tours", "Unassigned"])
    for ((config_file_name, problem_file_name), interation_solutions) in solutions.items():
        for idx, solution in enumerate(interation_solutions):
            best_known_writer.writerow([
                config_file_name, problem_file_name, idx, solution.extras.metrics.duration, solution.extras.metrics.generations,
                "{:.4f}".format(round(solution.extras.metrics.speed, 2)), "{:.4f}".format(round(solution.statistic.cost, 2)),
                solution.statistic.times.waiting, len(solution.tours), len(solution.unassigned)
            ])
