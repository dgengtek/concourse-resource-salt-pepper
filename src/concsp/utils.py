import textwrap

def _indent_char(s, repeat=1, count=4, character=" "):
    result = s if type(s) == str else str(s)
    for i in range(repeat):
        result = textwrap.indent(result, character * count)
    return result
