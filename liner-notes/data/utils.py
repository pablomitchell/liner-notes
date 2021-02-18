"""Simple text manipulation utilities"""


def trim_after(s, pattern):
    """Trim input string starting pattern.  
    Leading and trailing whitespace is stripped.

    Parameters
    ----------
    s : Input string
    pattern : String used to locate trim location

    Returns
    -------
    t : trimmed string

    Example
    -------
    >>> trim_after('quick brown fox', 'quick')
    'brown fox'

    """
    try:
        idx = s.index(pattern) + len(pattern)
    except ValueError:
        idx = 0
    finally:
        return s[idx:].strip()


def trim_before(s, pattern):
    """Trim input string ending at pattern.
    Leading and trailing whitespace is stripped.

    Parameters
    ----------
    s : Input string
    pattern : String used to locate trim location

    Returns
    -------
    t : trimmed string

    Example
    -------
    >>> trim_after('quick brown fox', 'fox')
    'quick brown'

    """
    try:
        idx = s.index(pattern)
    except ValueError:
        idx = -1
    finally:
        return s[:idx].strip()


def delete_lines_with_string(s, patterns):
    """Given an input string representing a document with
    line-breaks (e.g. an email) return a copy with lines
    containing specified patterns removed.  The return string
    has all white-space (including line-breaks) normalized to
    single spaces.

    Parameters
    ----------
    s : string
    patterns : sequence
        sequence of strings containing patterns used to identify
        lines to be removed

    Returns
    -------
    out : string

    Example
    -------
    >>> s = '''
    Make sure to remove lines
    bloooody hoo foo
    candy bar
    containing words we dislike
    baz
    '''
    >>> patterns = ['foo', 'bar', 'baz']
    >>> delete_lines_with_string(s, patterns)
    Make sure to remove lines containing words we dislike

    """
    keepers = []

    for line in s.split('\n'):
        if not any(pattern in line for pattern in patterns):
            keepers.append(line)

    return ' '.join(keepers)


def replace(s, patterns, replacment=''):
    """Given an input string representing a document with
    line-breaks (e.g. an email) return a copy with substrings
    exactly matched by patterns replaced.

    Parameters
    ----------
    s : string
    patterns : sequence
        sequence of strings containing patterns used to identify
        substrings to be removed
    replacement : string
        string used for replacement

    Returns
    -------
    out : string

    Example
    -------
    >>> s = '''
    Make sure to remove names of people
    and George Washington places we want
    to strike Alexander Hamilton from the
    record.
    '''
    >>> patterns = ['George Washington', 'Alexander Hamilton']
    >>> delete_substrings(s, patterns, '[REDACTED]')
    Make sure to remove names of people
    and [REDACTED] places we want
    to strike [REDACTED] from the
    record.

    """
    msg = s[:]

    for name in patterns:
        msg = msg.replace(name, replacment)

    return msg
