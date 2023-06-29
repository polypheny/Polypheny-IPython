import re

from IPython.core.magic import (
    Magics,
    magics_class,
    needs_local_scope,
    line_cell_magic, no_var_expand
)
from IPython.core.magic_arguments import magic_arguments, argument, parse_argstring
from IPython.display import display, JSON
from .poly_result import build_result

from .http_interface import HttpInterface


@magics_class
class PolyMagics(Magics):

    def __init__(self, shell):
        super().__init__(shell)
        self.database = HttpInterface()
        self.ns = None

    # To correctly detect where the args end and the query starts, the first occurrence of ':' is used.
    # For cell_magic, ':' can be omitted if the initial line contains precisely the args.
    # IMPORTANT: future (optional) arguments and their expected values may not contain a ':' symbol.
    @needs_local_scope
    @line_cell_magic
    @no_var_expand  # we implement custom variable expansion logic
    @magic_arguments()
    @argument(
        "command",
        choices=('db', 'info', 'help', 'sql', 'mql', 'cypher', 'pig', 'cql', 'load'),
        # Specifies all possible subcommands
        help="Specify the command to be used.",
    )
    @argument(
        "-j",
        "--json",
        action='store_true',
        dest='display_json',
        help="Display a JSON representation of the query result.",
    )
    @argument(
        "-i",
        "--input",
        action='store_true',
        dest='load_from_input',
        help="When using load, request the query result via an input prompt.",
    )
    @argument(
        "-t",
        "--template",
        action='store_true',
        dest='is_template',
        help="Treat the query as a template. "
             "Parameters like ${my_param} will be expanded to their corresponding value. "
             "Warning: This can lead to arbitrary query injections, as the parameters do not get escaped.",
    )
    @argument(
        "-h",
        "--help",
        action='store_true',
        help="Print command-specific help.",
    )
    @argument(
        "namespace",
        nargs='?',
        default='public',
        help="Specify the default namespace to be used. If no argument is given, 'public' is used.",
    )
    def poly(self, line, cell=None, local_ns=None):
        """    : [value]


        Line and Cell magics for querying Polypheny.
        Instead of the ':' separator between command and value, the value can be written on a new line in cell magics.

        Examples:
            %poly db: localhost:13137

            %poly sql: SELECT * FROM xyz

            %%poly sql
            SELECT * FROM xyz

            %%poly mql my_documents
            db.collection.find({})


          value\t\t\tSpecify the query (for sql,mql,cypher,pig,cql,load) or the URL (for the db command).
        """

        self.ns = self.shell.user_ns.copy()

        raw_args, value = separate_args(line, cell)
        if not (raw_args and value):
            if not 'help' in raw_args:
                print("Did you forget to terminate your arguments with ':' ?")
            self.poly.parser.print_help()
            return

        if cell is None:
            self.ns.update(local_ns)  # Add local namespace to global namespace (local can only differ in line magics)

        args = parse_argstring(self.poly, raw_args)

        return self.handle(args, value)

    def handle(self, args, value):
        command = args.command

        if args.help or command == 'help':
            # TODO: add command specific help
            self.poly.parser.print_help()
            return
        if command == 'db':
            self.database.set_url(value)
            return
        elif command == 'info':
            return str(self.database)

        if args.is_template:
            value = self.expand_variables(value)

        if command == 'load':
            result = build_result(input(value)) if args.load_from_input else build_result(value)
        else:
            result = self.database.request(value, command, args.namespace)

        if args.display_json:
            display(JSON(result.result_set))
        return result

    def expand_variables(self, template):
        pattern = r'\$\{([^\} ]+)\}'  # '${<my_var>}', where <my_var> has at least length 1 and contains no space or '}'
        matches = re.findall(pattern, template)  # Find all matches of the pattern

        for match in matches:
            if match in self.ns:
                template = template.replace('${' + match + '}', str(self.ns[match]))

        return template


def separate_args(line, cell, split_str=":"):
    """
    Finds the first occurence of an element of termination_strings in line. The line is split after this element and
    the two parts are returned.
    """
    if cell is None:
        split_str += ' '  # if line_magic, check for space after split_str. (e.g. to ignore http://)

    idx = line.find(split_str)
    if idx == -1:
        return line, cell
    args = line[:idx]
    value = line[idx + 1:]
    if cell is not None:
        value += '\n' + cell
    return args, value.strip()
