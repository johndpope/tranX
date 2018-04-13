# coding=utf-8
import re
from babel.numbers import parse_decimal, NumberFormatError

from .lib.query import Query


num_re = re.compile(r'[-+]?\d*\.\d+|\d+')


def my_detokenize(tokens, token_dict, raise_error=False):
    literal = []
    for token in tokens:
        match = False
        for word, gloss, after in zip(token_dict['words'], token_dict['gloss'], token_dict['after']):
            if token == word:
                literal.extend([gloss, after])
                match = True
                break

        if not match and raise_error:
            raise ValueError('cannot find the entry for %s in the token dict' % token)

    return ''.join(literal).strip()


def detokenize_query(query, example_dict, header):
    detokenized_conds = []
    for i, (col, op, val) in enumerate(query.conditions):
        val_tokens = val.split(' ')

        detokenized_cond_val = my_detokenize(val_tokens, example_dict['question'])

        if header[col].type == 'real' and not isinstance(detokenized_cond_val, (int, float)):
            try:
                detokenized_cond_val = float(parse_decimal(val))
            except NumberFormatError as e:
                detokenized_cond_val = float(num_re.findall(val)[0])

        detokenized_conds.append((col, op, detokenized_cond_val))

    detokenized_query = Query(sel_index=query.sel_index, agg_index=query.agg_index, conditions=detokenized_conds)

    return detokenized_query
