import csv
import glob
import json
import subprocess
import sys
from pathlib import Path

class Deserializer:
    @classmethod
    def from_dict(cls, dict):
        obj = cls()
        obj.__dict__.update(dict)
        return obj

class SolverClient:
    def __init__(self, cli_path):
        self.cli_path = cli_path

    def solve(self, problem_path, config_path, solution_path, geojson_solution_path):
        p = subprocess.run([self.cli_path, 'solve', 'pragmatic', problem_path, '-c', config_path, 
            '-o', solution_path, '-g', geojson_solution_path],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if p.returncode == 0:
            with open(solution_path, 'r') as f:
                solution_str = f.read()
                return json.loads(solution_str, object_hook=Deserializer.from_dict)
        else:
            pass

# if len(sys.argv) < 4:
#     print("Provide path to cli, experiment root path and number of samples")
#     sys.exit(1)
# else:
#     cli_path = sys.argv[1]
#     config_path = sys.argv[2]
#     samples = int(sys.argv[3])

cli_path = "/home/builuk/playground/vrp-rst/target/release/vrp-cli"
experiment_path = "/home/builuk/playground/vrp-analysis/experiments/demo"
samples = 5


print("getting data in experiment root path: '{}'".format(experiment_path))

# get list of problems
problem_files = glob.glob("{}/problems/*".format(experiment_path))
print("problems:", problem_files)

# get list of configs
config_files = glob.glob("{}/configs/*".format(experiment_path))
print("configs:", config_files)

# create and run solver
solver = SolverClient(cli_path)
solutions = {}
iteration = 0
total_iterations = len(problem_files) * len(config_files) * samples
for problem_path in problem_files:
    print("run '{}' with {} config(-s)".format(problem_path, len(config_files)))
    problem_file_name = Path(problem_path).stem
    for config_path in config_files:
        config_file_name = Path(config_path).stem
        out_dir = "{}/out/{}_{}".format(experiment_path, config_file_name, problem_file_name)
        Path(out_dir).mkdir(parents = True, exist_ok=True)

        for attempt in range(samples):
            iteration += 1
            print("iteration {} of {}, config: '{}', problem: '{}'".format(iteration, total_iterations,
                config_file_name, problem_file_name))
            solution_path = "{}/solution_{}.json".format(out_dir, attempt)
            geojson_solution_path = "{}/solution_{}.geojson".format(out_dir, attempt)
            solution = solver.solve(problem_path, config_path, solution_path, geojson_solution_path)
            solutions.setdefault((config_file_name, problem_file_name), []).append(solution)
            print("\t took {}s".format(solution.extras.metrics.duration))


# create csv for best-known solution analysis
with open("{}/out/best_known_solutions.csv".format(experiment_path), mode='w') as best_known_file:
    best_known_writer = csv.writer(best_known_file, delimiter=',', quotechar='"',  quoting=csv.QUOTE_MINIMAL)
    best_known_writer.writerow(["Config", "Problem", "Sequence", "Duration", "Generations", "Speed", "Cost", "Waiting", "Tours", "Unassigned"])
    for ((config_file_name, problem_file_name), interation_solutions) in solutions.items():
        for idx, solution in enumerate(interation_solutions):
            best_known_writer.writerow([
                config_file_name, problem_file_name, idx, solution.extras.metrics.duration, solution.extras.metrics.generations,
                "{:.4f}".format(round(solution.extras.metrics.speed, 2)), "{:.4f}".format(round(solution.statistic.cost, 2)),
                solution.statistic.times.waiting, len(solution.tours), len(solution.unassigned)
            ])
