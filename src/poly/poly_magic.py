import re

from IPython.core.magic import (
    Magics,
    magics_class,
    needs_local_scope,
    line_cell_magic, no_var_expand
)
from IPython.core.magic_arguments import magic_arguments, argument, parse_argstring
from IPython.display import display, JSON
from .poly_result import build_result, QueryPolyResult, ErrorPolyResult

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
        choices=('db', 'info', 'help', 'sql', 'mql', 'cypher', 'pig', 'cql', 'load', 'store', 'retrieve', 'append', 'schema'),
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

            %poly schema

            %poly sql: SELECT * FROM xyz

            %%poly sql
            SELECT * FROM xyz

            %%poly mql my_documents
            db.collection.find({})

            # replaces content
            %poly store [namespace.]name: <variable>
            %poly append [namespace.]name: <variable>

            %poly retrieve [namespace.]name


          value\t\t\tSpecify the query (for sql,mql,cypher,pig,cql,load) or the URL (for the db command).
        """

        self.ns = self.shell.user_ns.copy()

        raw_args, value = separate_args(line, cell)

        if raw_args == 'schema':
            return self.database.schema_tree()

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

        if command == 'store' or command == 'append':
            self.handle_store(args, value, command == 'store')
            return None

        if command == 'retrieve':
            return self.handle_retrieve(args, value)

        if command == 'load':
            result = build_result(input(value)) if args.load_from_input else build_result(value)
        else:
            result = self.database.request(value, command, args.namespace)

        if args.display_json:
            display(JSON(result.result_set))
        return result

    def check_incorrect(self, result) -> bool:
        return type(result) is not QueryPolyResult

    def expand_variables(self, template):
        pattern = r'\$\{([^\} ]+)\}'  # '${<my_var>}', where <my_var> has at least length 1 and contains no space or '}'
        matches = re.findall(pattern, template)  # Find all matches of the pattern

        for match in matches:
            if match in self.ns:
                template = template.replace('${' + match + '}', str(self.ns[match]))

        return template

    def handle_store(self, args, value, truncate=False):
        #print(f"store value: {value}")
        #print(f"store name: {args.namespace}")

        if type(value) is str and self.ns[value]:
            value = self.ns[value]


        schema_res = self.database.request(f"CREATE DOCUMENT NAMESPACE IF NOT EXISTS doc;", "sql","doc")
        if self.check_incorrect(schema_res):
            print(f"Error on create document query. {schema_res}")
            return False
        if truncate:
            drop_res = self.database.request(f"db.{args.namespace}.drop()", "mql", "doc")
            if self.check_incorrect(drop_res):
                return False

        create_res = self.database.request(f"db.createCollection({args.namespace})", "mql", "doc")
        if self.check_incorrect(create_res):
            return False

        if type(value) is list:
            dicts = []
            for item in value:
                dicts.append({'value': item})
            print(dicts)
            insert_res = self.database.request(f"db.{args.namespace}.insertMany({dicts})", "mql", "doc")
        else:
            dict = {'value': value}
            insert_res = self.database.request(f"db.{args.namespace}.insertMany([{dict}])", "mql", "doc")

        if self.check_incorrect(insert_res):
            return False

    def handle_retrieve(self, args, value):
        # print(f"retrieve {value}")
        # print(f"store name: {args}")
        results = []
        responses = self.database.request(f"db.{value[0]}.find()", "mql", "doc")

        if type(responses) is ErrorPolyResult:
            return None

        for response in responses:
            for item in response:
                results.append(item['value'])

        return results


def separate_args(line, cell, split_str=":"):
    """
    Finds the first occurrence of an element of termination_strings in line. The line is split after this element and
    the two parts are returned.
    """
    if cell is None:
        split_str += ' '  # if line_magic, check for space after split_str. (e.g. to ignore http://)

    if not split_str in line:
        splits = line.split(" ")
        if len(splits) > 1:
            return splits[0], splits[1:]

    idx = line.find(split_str)
    if idx == -1:
        return line, cell
    args = line[:idx]
    value = line[idx + 1:]
    if cell is not None:
        value += '\n' + cell
    return args, value.strip()
