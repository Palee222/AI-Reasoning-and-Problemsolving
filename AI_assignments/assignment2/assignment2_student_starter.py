# AI ESCAPE ROOM — STUDENT STARTER
# Paste this entire file into a notebook cell, complete the TODO functions,
# and run it top to bottom with both supplied JSON files in the working directory.



# # Individual Assignment 2 — AI Escape Room: Crack the Security System
#
# **Your task:** assign one control channel to every security device so that all rules hold. Implement plain backtracking, backtracking with MRV and forward checking, and min-conflicts. Submit this completed notebook and the `results.json` it creates.
#
# Put `security_system.json` and `result_sample_submission.json` in the same working directory as this notebook. Use only the standard Python library. Keep the function names, parameters and output keys below unchanged. Do not alter the data file or hard-code the answer.


# ## 1. Read the puzzle
#
# `variables` lists the devices: `L` = laser, `C` = camera, `D` = door lock, `T` = terminal, and `S` = switch. A channel is an **integer** from 1 to 4. Each `domains[name]` is the complete list of values allowed for that particular device; a value absent from the domain is forbidden.
#
# Each entry in `constraints` involves exactly two devices, named `left` and `right`:
#
# | Type | Requirement | Examples |
# | --- | --- | --- |
# | `different` | `left != right` | 2 and 3 ✓; 2 and 2 ✗ |
# | `consecutive` | `abs(left - right) == 1` | 2 and 3 ✓; 3 and 2 ✓; 5 and 1 ✗ |
# | `less_than` | `left < right` | 2 and 3 ✓; 3 and 2 ✗ |
#
# There are **no other types of rule**. `less_than` depends on the order of the named devices; the other two types do not. A rule is evaluated only when both of its devices have assigned values. Thus zero conflicts in a **partial** assignment does not mean that the puzzle is solved.


import json
import random
from pathlib import Path

DATA_DIR = Path(".")  # Change only this path if you put the JSON files elsewhere.


def read_json(filename):
    with (DATA_DIR / filename).open("r", encoding="utf-8") as file:
        return json.load(file)


problem = read_json("security_system.json")
sample_submission = read_json("result_sample_submission.json")


def check_problem(problem):
    variables = problem["variables"]
    domains = problem["domains"]
    constraints = problem["constraints"]
    assert variables and len(variables) == len(set(variables))
    assert set(variables) == set(domains)
    assert all(domains[name] and len(domains[name]) == len(set(domains[name]))
               for name in variables)
    assert all(type(value) is int for domain in domains.values()
               for value in domain)
    for rule in constraints:
        assert set(rule) == {"type", "left", "right"}
        assert rule["type"] in {"different", "consecutive", "less_than"}
        assert rule["left"] in domains and rule["right"] in domains
        assert rule["left"] != rule["right"]


def rule_holds(rule, left_value, right_value):
    """Evaluate one rule using the values in left/right order."""
    if rule["type"] == "different":
        return left_value != right_value
    if rule["type"] == "consecutive":
        return abs(left_value - right_value) == 1
    if rule["type"] == "less_than":
        return left_value < right_value
    raise ValueError(f"Unknown constraint type: {rule['type']}")


def count_conflicts(problem, assignment):
    """Count violated rules whose two variables are currently assigned."""
    return sum(
        not rule_holds(rule, assignment[rule["left"]], assignment[rule["right"]])
        for rule in problem["constraints"]
        if rule["left"] in assignment and rule["right"] in assignment
    )


def validate_solution(problem, assignment):
    """Require all variables, permitted integer values, and zero conflicts."""
    if not isinstance(assignment, dict):
        return False
    if set(assignment) != set(problem["variables"]):
        return False
    if any(type(assignment[name]) is not int or
           assignment[name] not in problem["domains"][name]
           for name in problem["variables"]):
        return False
    return count_conflicts(problem, assignment) == 0


def describe_rule(rule):
    """A readable equivalent of one JSON rule."""
    operator = {
        "different": "!=",
        "consecutive": "consecutive with",
        "less_than": "<",
    }[rule["type"]]
    return f"{rule['left']} {operator} {rule['right']}"


check_problem(problem)
print(f"Loaded {len(problem['variables'])} devices and "
      f"{len(problem['constraints'])} rules.")
print("Domains:")
for name in problem["variables"]:
    print(f"  {name}: {problem['domains'][name]}")
print("Rules:")
for index, rule in enumerate(problem["constraints"], start=1):
    print(f"  {index:2}. {describe_rule(rule)}")


# ## 2. A small worked example
#
# This is **not** the facility puzzle. It shows how to interpret the format.
#
# - `X` may use 1 or 2; `Y` may use 1, 2 or 3; `Z` may use 2 or 3.
# - `X` and `Y` must be consecutive, `X` and `Z` must differ, and `Y` must be less than `Z`.
# - `X=1, Y=2, Z=3` is complete and valid.
# - `X=2, Y=2, Z=3` violates `consecutive(X,Y)`.
# - `X=1, Y=2` has zero conflicts so far but is **not complete**.


practice_problem = {
    "variables": ["X", "Y", "Z"],
    "domains": {"X": [1, 2], "Y": [1, 2, 3], "Z": [2, 3]},
    "constraints": [
        {"type": "consecutive", "left": "X", "right": "Y"},
        {"type": "different", "left": "X", "right": "Z"},
        {"type": "less_than", "left": "Y", "right": "Z"},
    ],
}
check_problem(practice_problem)
assert validate_solution(practice_problem, {"X": 1, "Y": 2, "Z": 3})
assert count_conflicts(practice_problem, {"X": 2, "Y": 2, "Z": 3}) == 1
assert count_conflicts(practice_problem, {"X": 1, "Y": 2}) == 0
assert not validate_solution(practice_problem, {"X": 1, "Y": 2})
print("Worked example checks passed.")


# ## 3. Implement the three methods
#
# Each function receives a problem in the **same format**, must leave the input unchanged, and returns `(solution, stats)`.
#
# - `solution`: a dictionary `{device: channel}` if successful. If systematic search finds no solution, return `None`. Min-conflicts should return its **best complete assignment** if its limits are exhausted.
# - `assignments`: number of candidate variable/value assignments tried, including those rejected immediately.
# - `backtracks`: number of previously consistent choices undone because they could not lead to a solution (including a forward-checking domain wipeout). Do not count an immediately rejected candidate again as a backtrack.
# - `steps`: total **single-variable repairs** actually made by min-conflicts across all attempts.
# - `restarts`: number of new random complete configurations tried **after** the first configuration.
# - `final_conflicts`: violated rules in the returned min-conflicts assignment; it is 0 on success.
#
# For reproducibility, min-conflicts should use `rng = random.Random(seed)` and honour `max_steps` **per attempt** and `max_restarts` **additional attempts**. Break ties using `rng.choice`. Different correct implementations may report different numbers; grading does not require the instructor's exact metric values.
#
# **Plain backtracking:** assign variables in the order of `problem["variables"]`. **Improved backtracking:** choose the smallest remaining domain (MRV), breaking ties by that same variable order; after each assignment, filter all unassigned domains (forward checking). **Min-conflicts:** start with a complete assignment, select a variable in a violated rule, and change its value to minimise the number of violated rules touching that variable; restart if needed.


def plain_backtracking(problem):
    """Return (solution, {"assignments": int, "backtracks": int})."""
    # TODO: implement basic recursive backtracking in variable-list order.
    raise NotImplementedError("Implement plain_backtracking")


def improved_backtracking(problem):
    """Return (solution, {"assignments": int, "backtracks": int})."""
    # TODO: implement MRV with forward checking and reversible domain copies.
    raise NotImplementedError("Implement improved_backtracking")


def min_conflicts(problem, seed=202610, max_steps=1000, max_restarts=100):
    """Return (solution, {"steps": int, "restarts": int,
                          "final_conflicts": int})."""
    # TODO: use a local rng; start with complete assignments; repair conflicts.
    raise NotImplementedError("Implement min_conflicts")


# ## 4. Self-check, run and export
#
# Run the notebook **from top to bottom** after completing all three functions. The small example below checks that your code can solve another compatible problem, rather than depending on the facility's device names. The code below checks the supplied puzzle and writes `results.json`. Do not change its keys or write a solution by hand.
#
# You will be assessed on algorithm correctness and valid solutions, including additional **satisfiable** problems with this same three-rule format. The exact search metrics and the solution found by a solver are not prescribed.


import copy


def check_return(method, candidate, stats, source, expected_metrics):
    assert isinstance(stats, dict), f"{method}: return a statistics dictionary"
    assert set(stats) == set(expected_metrics), (
        f"{method}: expected metric keys {expected_metrics}; got {list(stats)}"
    )
    for key in expected_metrics:
        assert type(stats[key]) is int and stats[key] >= 0, (
            f"{method}: {key} must be a non-negative integer"
        )
    assert validate_solution(source, candidate), (
        f"{method}: returned assignment is incomplete, outside a domain, "
        "or violates a rule"
    )
    if method == "min_conflicts":
        assert stats["final_conflicts"] == count_conflicts(source, candidate)


practice_copy = copy.deepcopy(practice_problem)
for method, solver, metrics in (
    ("backtracking", plain_backtracking, ("assignments", "backtracks")),
    ("improved_backtracking", improved_backtracking,
     ("assignments", "backtracks")),
    ("min_conflicts", min_conflicts, ("steps", "restarts", "final_conflicts")),
):
    candidate, stats = solver(practice_problem)
    check_return(method, candidate, stats, practice_problem, metrics)
    print(f"Practice: {method} passed.")
assert practice_problem == practice_copy, "A solver modified the input problem"


original_problem = copy.deepcopy(problem)
run_specs = {
    "backtracking": (plain_backtracking, ("assignments", "backtracks")),
    "improved_backtracking": (
        improved_backtracking, ("assignments", "backtracks")
    ),
    "min_conflicts": (
        min_conflicts, ("steps", "restarts", "final_conflicts")
    ),
}
assert set(run_specs) == set(sample_submission)

results = {}
for method, (solver, metrics) in run_specs.items():
    solution, stats = solver(problem)
    check_return(method, solution, stats, problem, metrics)
    entry = {"solution": solution, "valid": validate_solution(problem, solution),
             **stats}
    assert set(entry) == set(sample_submission[method]), (
        f"{method}: result keys differ from result_sample_submission.json"
    )
    assert set(entry["solution"]) == set(sample_submission[method]["solution"])
    results[method] = entry
    print(f"{method}: valid={entry['valid']}, metrics={stats}")

assert problem == original_problem, "A solver modified the input problem"
with (DATA_DIR / "results.json").open("w", encoding="utf-8") as file:
    json.dump(results, file, ensure_ascii=False, indent=2)
    file.write("\n")
print("Saved results.json")
