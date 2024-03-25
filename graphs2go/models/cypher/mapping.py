from collections import namedtuple

"""
Adapted from Cymple (https://github.com/Accenture/Cymple), MIT license.
"""
Mapping = namedtuple("Mapping", ["ref_name", "returned_name"], defaults=(None, None))
