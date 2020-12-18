"""Simple email cleanup -- wine reviews stored in a CSV file"""

import html
import re

import pandas as pd

from data import utils


PATTERNS = {
    # always ignore case

    # '2009 Charvin Chateauneuf-du-Pape - $'
    # 'NV #55 Mystery Chardonnay - $'
    'LABEL': r'(([1-2][0-9]{3}|nv)(\s+)(.*?))((\s?)(\-)(\s?)(\$))',

    # '750ml', '1.5lt', '375ml'
    'FORMAT': r'(\d{3}ml)|(\d+(\.\d*)?)lt',

    # '85pts', '90-95pts'
    'POINTS': r'([0-9]{2,3})(\-[0-9]{2,3})?(\+*)pts',

    # '$123.45', '$321', '$10-15+', '$123.45-678.90+'
    'PRICE': r'(\$)(\d+(\.\d+)?(\-\d+(\.\d+)?)?\+?)',

    # '3x', '2 x', '4  x'
    'QUANTITY': r'(\d\s*x)',

    # 'wa100',  'ws95+', 'iwc93-95', 'wa92-94+'
    'SCORE': r'([a-z]{1,3}[0-9]{2,3})(\-[0-9]{2,3})?(\+*)',

    # 'https://www.nytimes.com/'
    'URL': r'(http)(s??)(://).*',

    #
    # for reference -- string.punctuation:
    #
    #     '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'
    #

    # anything other than '-', '.', '?', '\s', '\w'
    'SYMBOL': r"[^-.?'\s\w]",

    # anything other than '\s' or '\w' and repeats 4+ times
    'RUN_ON': r"([^\s\w])\1{4,}",

    # adhoc punctuation patterns
    'AMPERSAND': r'(?<=\w)(\s?&\s?)(?=\w)',
    'DASH': r'(?<=\d)(\s?\-\s?)(?=\d)',
    'ELLIPSIS': r'(?<!\.)(\.{2,4})(?!\.)',
    'ENDASH': r'(?<=\w)(\s\-)(?=\s\w)',
    'EXCLAIM': r'(?<=\w)!',
    'PERCENT': r'(?<=\d)%(?!%)',
    'POUND': r'(?<!#)#(?=\d)',
    'SLASH': r'(?<=\w)(\s?/\s?)(?=\w)',
}


def resub(name, s, replacement=''):
    # always ignore case and default to deleting the match
    return re.sub(PATTERNS[name], replacement, s, re.IGNORECASE)


def get_label(s):
    # Extract the wine ``label`` from the string
    result = re.search(PATTERNS['LABEL'], s, re.IGNORECASE)
    msg = result.group(1) if result else 'empty'

    msg = resub('FORMAT', msg)
    msg = resub('QUANTITY', msg)
    msg = resub('SYMBOL', msg)

    return msg


# WTH? -- someone please show me a better way to do this!
UNICODE_TO_ASCII = {
    u'\u02c8': "'",
    u'\u0301': "'",
    u'\u2013': "-",
    u'\u2014': "-",
    u'\u2018': "'",
    u'\u2019': "'",
    u'\u201c': '"',
    u'\u201d': '"',
    u'\u2022': "*",  # bullet
    u'\u2026': ' ',
    u'\xa0': ' ',
    u'\xb0': '*',  # bullet
    u'\xbe': '3',
    u'\xe0': 'a',
    u'\xe2': 'a',
    u'\xe7': 'c',
    u'\xe8': 'e',
    u'\xe9': 'e',
    u'\xed': 'i',
    u'\xf1': 'n',
    u'\xf3': 'o',
    u'\xf4': 'o',
    u'\xfc': 'u',
}
TRANSLATION = str.maketrans(
    ''.join(UNICODE_TO_ASCII.keys()),
    ''.join(UNICODE_TO_ASCII.values()),
)
#
# for key, value in UNICODE_TO_ASCII.items():
#    print(key, value)
# exit()
#


def clean_message(s):
    # process the string generating a clean message
    msg = s.lower()
    msg = html.unescape(msg)
    msg = msg.translate(TRANSLATION)
    #
    # try:
    #     msg.encode('ascii').decode()
    # except Exception as e:
    #     print(e)
    #     input('ENTER')
    #
    msg = msg.encode('ascii', 'ignore').decode()

    label = get_label(msg)

    msg = utils.trim_after(msg, 'dear friends')
    msg = utils.trim_before(msg, 'thank you')
    msg = utils.trim_before(msg, 'to order')

    unwanted_lines = [
        '/person',
        'finest and freshest original provenance available',
        'first come first served',
        'jon rimmerman',
        'parcel has arrived',
        'parcel has just arrived',
        'parcel is set to arrive',
        'shipment only',
        'wholesalers',
    ]
    msg = utils.delete_lines_with_string(msg, unwanted_lines)

    unwanted_entities = [
        'antonio galloni',
        'gary walsh',
        'james halliday',
        'neal martin',
        'nick stock',

        'jancis robinson',
        'jancis',

        'jon rimmerman',
        'rimmerman',

        'robert parker',
        'bob parker',
        'parker',

        'the wine front',
        'wine advocate',
        'wine spectator',
    ]
    msg = utils.replace(msg, unwanted_entities)

    msg = resub('POINTS', msg, 'amazing')
    msg = resub('PRICE', msg, r'\2 usd')
    msg = resub('QUANTITY', msg)
    msg = resub('SCORE', msg)
    msg = resub('URL', msg)

    msg = resub('AMPERSAND', msg, ' and ')
    msg = resub('DASH', msg, ' to ')
    msg = resub('ELLIPSIS', msg, ' ')
    msg = resub('ENDASH', msg)
    msg = resub('EXCLAIM', msg, '.')
    msg = resub('PERCENT', msg, ' percent')
    msg = resub('POUND', msg, ' number ')
    msg = resub('SLASH', msg, ' and ')

    msg = resub('SYMBOL', msg)
    msg = resub('RUN_ON', msg, '')

    note = ' '.join(msg.split())  # normalize whitespace

    return label, note


def test():
    # testing dumbed down -- take a look at the PATTERNS
    # dictionary to get a sense for what to expect from this

    s = 'quantities:  3 x 750ml and 4  x  750ml and 1.5L and 2X375ml'
    out = resub('QUANTITY', s)
    print(f'{s}\n{out}\n')

    s = 'formats:  3 x 750ml and 4  x  750ml and 1.5lt and 2X375ml'
    out = resub('FORMAT', s)
    print(f'{s}\n{out}\n')

    s = 'scores: wa100 ws95+ iwc93-95 wa92-94'
    out = resub('SCORE', s, 'recommended')
    print(f'{s}\n{out}\n')

    s = 'points: 85pts and 90-95pts'
    out = resub('POINTS', s, 'holy toledo')
    print(f'{s}\n{out}\n')

    s = 'prices: ($123.45) and ($321) and - $123.45 or - $321 perhaps $10-15+ and maybe this $123.45-678.90+'
    out = resub('PRICE', s, r'\2 dollars')
    print(f'{s}\n{out}\n')

    s = 'urls:  https://foo.com/lasjflasdjflasjdf  or  http://www.pets.com/'
    out = resub('URL', s)
    print(f'{s}\n{out}\n')

    s = '2009 Charvin Chateauneuf-du-Pape - $58.81 (IWC93-95)(WA92-94)'
    out = get_label(s.lower())
    print(f'{s}\n{out}\n')

    s = 'With the new 2017 vintage, Zorzal may finally have it right with their Eggo “Filoso” Pinot Noir and the $'
    out = get_label(s.lower())
    print(f'{s}\n{out}\n')

    s = 'NV Charvin Chateauneuf-du-Pape - $58.81'
    out = get_label(s.lower())
    print(f'{s}\n{out}\n')

    s = 'Mystery #55 Crappy Chardonnay - $58.81'
    out = get_label(s.lower())
    print(f'{s}\n{out}\n')

    s = 'Charvin Chateauneuf-du-Pape'
    out = get_label(s)
    print(f'{s}\n{out}\n')

    s = 'exclaim:  (wtf!)  or  (i really love this!) or (!!!)'
    out = resub('EXCLAIM', s, '.')
    print(f'{s}\n{out}\n')

    s = 'pound:  (#10)  or  (x#x) or (# 5) or (##123) or (### 123)'
    out = resub('POUND', s, 'number ')
    print(f'{s}\n{out}\n')

    s = 'percent:  (give you a 100% discount!) or (55 %) or (44%%) or (%)'
    out = resub('PERCENT', s, ' percent')
    print(f'{s}\n{out}\n')

    s = 'ampersand:  (buy J&J stock) or (buy J & J stock) or (&) or ( & ) or ( 1& ) or ( &x ) or (&&) or ( && )'
    out = resub('AMPERSAND', s, ' and ')
    print(f'{s}\n{out}\n')

    s = 'slash:  (buy J/J stock) or (buy J / J stock) or (/) or ( / ) or ( 1/ ) or ( /x ) or (//) or ( // )'
    out = resub('SLASH', s, ' and ')
    print(f'{s}\n{out}\n')

    s = 'ellipsis: (...) or (......) or (..) or (. . . .)'
    out = resub('ELLIPSIS', s, ' so ')
    print(f'{s}\n{out}\n')

    s = 'endash: of random mixed 6packs pulled from the list of wines below - i do not know the exact make up of each'
    out = resub('ENDASH', s, '. ')
    print(f'{s}\n{out}\n')

    s = 'RUN_ON: (!!) or (@@@) or (#) or ($$) or (%%%%%%%%%%%) or (^^) or (&) or (******) or (xxxxxxx)'
    out = resub('RUN_ON', s, '')
    print(f'{s}\n{out}\n')


def clean(infile, outfile=None, verbose=False):
    """Read CSV file, clean the data, and return a
    pandas dataframe.  Can also, write data to disk.

    Parameters
    ----------
    infile : string
        path to input CSV file
    outfile : string, default None
        path to output CSV file
    verbose : bool, default False
        if True prints processing details to stdout

    Return
    ------
    df_clean : pandas.DataFrame
        cleaned data with columns = ['labels', 'notes']

    Example
    -------
    >>> df = clean(
        infile='garagiste_wine.csv',
        outfile='garagise_wine_clean.csv',
        verbose=True,
    )
    """
    if verbose:
        test()
        input('Hit ENTER to continue...')

    df = pd.read_csv(infile)
    labels, notes = [], []

    for _, row in df.iterrows():
        label, note = clean_message(row.message)
        labels.append(label)
        notes.append(note)

        if verbose:  # helps debugging
            if label == 'empty':
                # perhaps discover why label was empty
                print(f'date:  {row.date}')
                print(row.message)
                print('-' * 45)
            else:
                # show labels and notes with chunky line breaks
                print(f'label: {label}\n')
                n_note = len(note)
                n_char = 100
                n_line = n_note // n_char
                for i in range(n_line):
                    m, n = i * n_char, (i + 1) * n_char
                    print(f'{note[m:n]}')
                print('-' * 45)

    df['labels'], df['notes'] = labels, notes

    # non-empty unique labels and notes only
    df_clean = (df
        .get(['labels', 'notes'])
        .loc[~df['labels'].str.startswith('empty')]
        .drop_duplicates()
        .reset_index(drop=True)
    )

    if verbose:
        df_clean.info()
        print(df_clean.sample(5))

    if outfile:
        df_clean.to_csv(outfile, index=False)

    return df_clean


if __name__ == '__main__':
    clean(
        infile='garagiste_wine.csv',
        outfile='garagiste_wine_clean.csv',
        verbose=True,
    )
