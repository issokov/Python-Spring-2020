class ParseError:
    unknown_token, wrong_arg_num = range(2)

    def __init__(self, tokens, error_type):
        self.type = error_type
        self.tokens = tokens


class ExecError:
    web_issue, extract_issue, unknown_var, wrong_type, loop_nf, wrong_set, mkdir_err, doc_issue = range(8)

    def __init__(self, error_type, what=None):
        self.type = error_type
        self.what = what


def parse_error(line_n, error):
    print(f'Error in line {line_n}:')
    print(" ".join(error.tokens) + '\n^')
    if error.type == ParseError.unknown_token:
        print("Unknown command!")
    elif error.type == ParseError.wrong_arg_num:
        print(f"Wrong argument number for {error.tokens[0]} command.")
    exit(1)


def execution_error(error):
    if error.type == ExecError.web_issue:
        print(f"Connections error:\n{error.what}")
    if error.type == ExecError.extract_issue:
        print(f"Extractions error:\n{error.what}")
    if error.type == ExecError.unknown_var:
        print(f"Unknown variable {error.what}")
    if error.type == ExecError.wrong_type:
        print(f"Wrong type: {error.what}")
    if error.type == ExecError.loop_nf:
        print("Ooooops loop not found")
    if error.type == ExecError.wrong_set:
        print(f"Expression {error.what} is not valid! Try something like 2 + 2")
    if error.type == ExecError.mkdir_err:
        print(f"System can't create directory in this path: {error.what}")
    if error.type == ExecError.doc_issue:
        print(f"DocX issue error:\n{error.what}")
    exit(1)