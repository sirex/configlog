import configlog.parser as parser


def test_tokens():
    tokens = list(parser.split_tokens('module key=val== new=old'))
    assert tokens == ['module', 'key=val==', 'new=old']

def test_with_module():
    assert parser.parse('module key=val') == dict(logger='module', key='val')

def test_without_module():
    assert parser.parse('key=val') == dict(logger='', key='val')

def test_extra_equals():
    assert parser.parse('key=val== new=old') == dict(
        logger='', key='val==', new='old',
    )

def test_extra_spaces():
    assert parser.parse('key=two words some=value') == dict(
        logger='', key='two words', some='value',
    )
