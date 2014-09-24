import re

var_re = re.compile(r'^[a-z]+=')
vars_re = re.compile(r' +[a-z]+=')


def split_tokens(line):
    last = 0
    for match in vars_re.finditer(line):
        yield line[last:match.start()].lstrip()
        last = match.start()
    yield line[last:].lstrip()


def parse(line):
    settings = {}

    tokens = list(split_tokens(line))

    if tokens and var_re.match(tokens[0]):
        settings['logger'] = ''
    else:
        settings['logger'] = tokens.pop(0)

    for token in tokens:
        key, val = token.split('=', 1)
        settings[key] = val

    return settings
