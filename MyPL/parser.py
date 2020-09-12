from error_handlers import ParseError

class Parser:

    def __init__(self, code=None):
        self.lines = None
        if code:
            self.load_script(code)

    def load_script(self, code):
        self.lines = code.split("\n")

    def get_line_count(self):
        if self.lines is not None:
            return len(self.lines)
        return 0

    def get_tokens(self, line):
        tokens = line.strip().split(' ')
        for end, token in enumerate(tokens):
            if not token or token[0] == '#':
                return tokens[:end]
        return tokens

    def get_line(self, line_n):
        return self.lines[line_n]

    def parse_line(self, line, actions):
        tokens = self.get_tokens(line)
        if tokens:
            command = tokens[0]
            if command in actions:
                args = tokens[1:]
                if len(args) in range(actions[command][1], actions[command][2] + 1):
                    return command, args, None
                else:
                    return None, None, ParseError(tokens, ParseError.wrong_arg_num)
            else:
                return None, None, ParseError(tokens, ParseError.unknown_token)
        return "", [], None