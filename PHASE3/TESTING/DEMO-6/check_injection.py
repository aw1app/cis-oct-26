import argparse
import ast
import sys
from pathlib import Path


SQL_MARKERS = ("SELECT ", "INSERT ", "UPDATE ", "DELETE ")


def contains_sql_text(node):
	return any(
		isinstance(child, ast.Constant)
		and isinstance(child.value, str)
		and any(marker in child.value.upper() for marker in SQL_MARKERS)
		for child in ast.walk(node)
	)


def uses_parameter(node, parameter_names):
	return any(
		isinstance(child, ast.Name) and child.id in parameter_names
		for child in ast.walk(node)
	)


def is_concatenated_query(node):
	return any(
		isinstance(child, (ast.BinOp, ast.JoinedStr))
		and (
			isinstance(child, ast.BinOp) and isinstance(child.op, ast.Add)
			or isinstance(child, ast.JoinedStr)
		)
		for child in ast.walk(node)
	)


def find_unsafe_execute_calls(tree):
	findings = []

	for function in ast.walk(tree):
		if not isinstance(function, (ast.FunctionDef, ast.AsyncFunctionDef)):
			continue

		parameter_names = {
			argument.arg
			for argument in function.args.posonlyargs + function.args.args + function.args.kwonlyargs
		}
		if function.args.vararg:
			parameter_names.add(function.args.vararg.arg)
		if function.args.kwarg:
			parameter_names.add(function.args.kwarg.arg)

		assignments = {}
		for node in ast.walk(function):
			if isinstance(node, ast.Assign):
				for target in node.targets:
					if isinstance(target, ast.Name):
						assignments[target.id] = node.value
			elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.value:
				assignments[node.target.id] = node.value

		for node in ast.walk(function):
			if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
				continue
			if node.func.attr != "execute" or not node.args:
				continue
			if len(node.args) > 1 or node.keywords:
				continue

			query = node.args[0]
			if isinstance(query, ast.Name):
				query = assignments.get(query.id, query)

			if (
				contains_sql_text(query)
				and is_concatenated_query(query)
				and uses_parameter(query, parameter_names)
			):
				findings.append((function.name, query.lineno, node.lineno))

	return findings


def main():
	parser = argparse.ArgumentParser(
		description="Check Python source for SQL string concatenation passed to execute()."
	)
	parser.add_argument(
		"source",
		nargs="?",
		type=Path,
		default=Path(__file__).with_name("alert_utils.py"),
		help="Python file to inspect (defaults to alert_utils.py beside this script)",
	)
	args = parser.parse_args()

	try:
		source_text = args.source.read_text(encoding="utf-8")
		tree = ast.parse(source_text, filename=str(args.source))
	except (OSError, SyntaxError) as error:
		print(f"Could not inspect {args.source}: {error}", file=sys.stderr)
		return 2

	findings = find_unsafe_execute_calls(tree)
	if findings:
		for function_name, query_line, execute_line in findings:
			print(
				"Potential SQL injection: "
				f"{function_name} builds a query from a function parameter "
				f"at line {query_line} and calls execute() without bound parameters "
				f"at line {execute_line}."
			)
		return 1

	print(f"No matching unsafe SQL construction found in {args.source}.")
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
