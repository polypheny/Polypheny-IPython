from .poly_magic import *


def load_ipython_extension(ipython):
    ipython.register_magics(PolyMagics)
