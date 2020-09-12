from executor import Executor
from parser import Parser
from error_handlers import execution_error
from error_handlers import parse_error

class Interpreter:

    executor = Executor()
    parser = Parser()

    def run(self, code: str):
        self.parser.load_script(code)
        while self.executor.line_n < self.parser.get_line_count():
            line = self.parser.get_line(self.executor.line_n)
            action, args, p_error = self.parser.parse_line(line, self.executor.actions)
            if p_error:
                parse_error(self.executor.line_n, p_error)
            e_error = self.executor.exec_command(action, args)
            if e_error:
                execution_error(e_error)
