# Copyright (c) 2010-2011 Joshua Harlan Lifton.
# See LICENSE.txt for details.

"""Functions that implement some English orthographic rules."""

from plover import system


def _add_candidates_from_rules(candidates, word, suffix):
    """ Use regular expressions to match orthography rules. """
    input = word + " ^ " + suffix
    for (rx_match, replacement) in system.ORTHOGRAPHY_RULES:
        m = rx_match(input)
        if m:
            candidates.append(m.expand(replacement))


def _add_suffix(word, suffix):
    """ Try to find a valid way to join a suffix to a root word using
        simple concatenation or regular expressions. A dictionary of
        the most common English words is used for validation. """

    in_dict_f = system.ORTHOGRAPHY_WORDS.__contains__
    candidates = []

    # Try a simple join if it is in the dictionary.
    simple = word + suffix
    if in_dict_f(simple):
        candidates.append(simple)

    # Add matches from the regular expression orthography rules.
    _add_candidates_from_rules(candidates, word, suffix)

    # If the suffix has an alias, try the rules on that too.
    alias = system.ORTHOGRAPHY_RULES_ALIASES.get(suffix, None)
    if alias is not None:
        _add_candidates_from_rules(candidates, word, alias)

    # From all candidates, choose the first by prominence in the dictionary.
    # In case of a tie, min() keeps the first item added to the candidates list.
    # If none of the candidates are in the dictionary, just return the first one.
    if candidates:
        dict_candidates = list(filter(in_dict_f, candidates))
        if dict_candidates:
            return min(dict_candidates, key=system.ORTHOGRAPHY_WORDS.__getitem__)
        else:
            return candidates[0]

    # If none of the rules matched *at all*, just do a simple join.
    return simple


def add_suffix(word, suffix):
    """Add a suffix to a word by applying the rules above
    
    Arguments:
        
    word -- A word
    suffix -- The suffix to add
    
    """
    suffix, sep, rest = suffix.partition(' ')
    expanded = _add_suffix(word, suffix)
    return expanded + sep + rest
