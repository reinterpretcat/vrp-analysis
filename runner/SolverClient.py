import subprocess
import json
from Helpers import Generic

class SolverClient:
    """
    A client to VRP CLI interface.
    For installation and documentation instructions see https://github.com/reinterpretcat/vrp
    """
    def __init__(self, cli_path):
        """
        :param cli_path: Path to the VRP CLI executable.
        """
        self.cli_path = cli_path

    def solve(self, problem_path, config_path, solution_path):
        """
        Runs VRP solver.

        :param problem_path: Path to problem in pragmatic format
        :param config_path: Path to configuration
        :param solution_path: Path where solution should be stored
        """
        p = subprocess.run([self.cli_path, 'solve', 'pragmatic', problem_path,'-o', solution_path],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if p.returncode == 0:
            with open(solution_path, 'r') as f:
                solution_str = f.read()
                return json.loads(solution_str, object_hook=Generic.from_dict)
        else:
            pass
