from itertools import chain, zip_longest

"""
Helper functions for doing stuff
"""

def grouper(it, n, fill=None):
    """Break an iterator into chunks of length n
    Positional arguments:
        it -- iterable to be chunked
        n -- integer length of chunks
    Keyword arguments:
    fill -- Value to fill the last iterator if when
    the length of the input is not divisible by n
    """
    args = [iter(it)] * n
    return zip_longest(*args, fillvalue=fill)

def dict_merge(it):
    """Merge an iterable of dictionaries into one dictionary
    Behavior for duplicate keys is undefined
    Example: dict_merage([{1:2}, {3:4}]) --> {1:2,3:4}
    Positional arguments:
        it -- iterable of dictionaries
    """
    # This is readable
    return dict(chain(*map(dict.items, it)))
