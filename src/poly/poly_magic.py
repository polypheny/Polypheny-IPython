from IPython.core.magic import (
    Magics,
    magics_class,
    needs_local_scope,
    line_cell_magic
)
from IPython.core.magic_arguments import magic_arguments, argument, parse_argstring

from .http_interface import HttpInterface


@magics_class
class PolyMagics(Magics):

    def __init__(self, shell):
        super().__init__(shell)
        print('Initialized ipython-polypheny extension')
        self.database = HttpInterface()

    # To correctly detect where the args end and the query starts, the first occurrence of ':' is used.
    # For cell_magic, ':' can be omitted if the initial line contains precisely the args.
    # IMPORTANT: future (optional) arguments and their expected values may not contain a ':' symbol.
    @needs_local_scope
    @line_cell_magic
    @magic_arguments()
    @argument(
        "command",
        choices=('db', 'info', 'help', 'sql', 'mql'),  # Specifies all possible subcommands
        help="Specify the command to be used.",
    )
    @argument(
        "-c",
        "--no_cache",
        action='store_false',
        dest='use_cache',
        help="Do not use the cache in this query.",
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
        """Line and Cell magics for querying Polypheny.

        Examples:
            %poly sql -c: SELECT * FROM xyz

            %%poly sql: SELECT * FROM xyz

            %%poly mql my_documents
            db.collection.find({})
        """

        ns = self.shell.user_ns.copy()

        raw_args, value = separate_args(line, cell)
        if not raw_args or not value:
            print("Did you forget to terminate your arguments with ':' ?")
            self.poly.parser.print_help()
            return

        if cell is None:
            ns.update(local_ns)  # Add local namespace to global namespace (local can only differ in line magics)

        args = parse_argstring(self.poly, raw_args)
        #print('arguments:', args)

        return self.handle(args, value)

    def handle(self, args, value):
        command = args.command

        if args.help or command == 'help':
            # TODO: add command specific help
            self.poly.parser.print_help()
            return
        if command == 'db':
            self.database.set_url(value)
        elif command == 'info':
            return str(self.database)
        else:
            return self.database.request(value, command, args.namespace, args.use_cache)


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
