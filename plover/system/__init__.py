import collections
from itertools import count
import os
import re

from plover.oslayer.config import CONFIG_DIR, ASSETS_DIR
from plover.registry import registry


def _load_wordlist(filename):
    if filename is None:
        return {}
    for dir in (CONFIG_DIR, ASSETS_DIR):
        path = os.path.realpath(os.path.join(dir, filename))
        if os.path.exists(path):
            break
    # Split the file on all whitespace, leaving a list of alternating
    # fields: [word, rank, word, rank,...]. Then make an iterator and
    # include it twice in a zip so that it gets polled twice each iteration.
    # This will shift out pairs of (word: rank) to the dict, and since the
    # rank is a single ASCII digit, getting the ordinal is the cheapest way
    # to convert to a small numeric type that preserves ordering.
    with open(path, encoding='utf-8') as f:
        fields = f.read().split()
    i = iter(fields)
    return dict(zip(i, map(ord, i)))

def _key_order(keys, numbers):
    """ Make an ordinal mapping of steno keys starting from 0.
        The order is the same whether or not a key is used as a number. """
    key_order = dict(zip(keys, count()))
    for (key, number) in numbers.items():
        key_order[number] = key_order[key]
    return collections.defaultdict(lambda: -1, key_order)

# System attributes that can be directly copied from the plugin.
_DIRECT_EXPORTS = ('KEYS', 'NUMBER_KEY', 'NUMBERS', 'UNDO_STROKE_STENO',
                   'ORTHOGRAPHY_RULES_ALIASES', 'KEYMAPS',
                   'DICTIONARIES_ROOT', 'DEFAULT_DICTIONARIES')

# System attributes that must be calculated from the plugin.
_CALCULATED_EXPORTS = {
    'KEY_ORDER'                : lambda mod: _key_order(mod.KEYS, mod.NUMBERS),
    'PREFIX_KEYS'              : lambda mod: tuple(getattr(mod, 'PREFIX_KEYS', ())),
    'SUFFIX_KEYS'              : lambda mod: tuple(getattr(mod, 'SUFFIX_KEYS', ())),
    'IMPLICIT_HYPHEN_KEYS'     : lambda mod: set(mod.IMPLICIT_HYPHEN_KEYS),
    'IMPLICIT_HYPHENS'         : lambda mod: {l.replace('-', '')
                                              for l in mod.IMPLICIT_HYPHEN_KEYS},
    'ORTHOGRAPHY_WORDS'        : lambda mod: _load_wordlist(mod.ORTHOGRAPHY_WORDLIST),
    'ORTHOGRAPHY_RULES'        : lambda mod: [(re.compile(pattern, re.I).match, replacement)
                                              for pattern, replacement in mod.ORTHOGRAPHY_RULES],
}

def setup(system_name):
    system_symbols = {}
    mod = registry.get_plugin('system', system_name).obj
    for symbol in _DIRECT_EXPORTS:
        system_symbols[symbol] = getattr(mod, symbol)
    for symbol, init in _CALCULATED_EXPORTS.items():
        system_symbols[symbol] = init(mod)
    system_symbols['NAME'] = system_name
    globals().update(system_symbols)

NAME = None
