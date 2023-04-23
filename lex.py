import ply.lex as lex
from ply.lex import LexToken

# List of token names.
tokens = (
    'TAG',
    'ID',
    'CLASS',
    'ATTR',
    'INDENT',
    'DEDENT',
    'TEXT',
    'COMMENT',
    'INTERPOLATION',
    'UNBUFFCOMMENT',
    'ASSIGN','EOF',
    'TAGINTERPOLATION_START',
    'TAGINTERPOLATION_END',
    'TAGINTERPOLATION_TEXT',
    'TAGINTERPOLATION_TEXT_OPEN'
)

states = (
    ('taginterpolation', 'inclusive'),
)

# tag name
def t_ANY_TAG(t):
    r'[a-zA-Z][a-zA-Z0-9]*'
    return t


def t_INDENT_DEDENT(t):
    r'(?:\n)[\s\t]+'
    indent = len(t.value.strip('\n'))/4
    if indent > t.lexer.indent_level:
        t.type = 'INDENT'
        t.value = indent
        t.lexer.indent_level = t.lexer.indent_level + 1
    elif indent < t.lexer.indent_level:
        t.type = 'DEDENT'
        t.lexer.indent_level = t.lexer.indent_level - 1
    else:
        return
    t.lexer.token_stream.append(t)
    return t

# interpolation = #[tag interpolation]
def t_TAGINTERPOLATION_START(t):
    r'\s*\#\['
    t.lexer.stack.append('[') 
    t.lexer.begin('taginterpolation')
    return t

def t_TAGINTERPOLATION_END(t):
    r'\]'
    if len(t.lexer.stack) > 0 and t.lexer.stack[-1] == '[':
        t.lexer.stack.pop()
        if not '[' in t.lexer.stack:
            t.lexer.begin('INITIAL')
    else:
        print('Nenhuma tag aberta.')
    return t

def t_taginterpolation_TAGINTERPOLATION_TEXT(t):
    r'[\|\s]\s*(?:(?!\#\{)(?!\#\[)[^\n\]])*'
    return t

def t_taginterpolation_TAGINTERPOLATION_TEXT_OPEN(t):
    r'\s*\[\s?'
    t.lexer.stack.append('[') 
    return t

# interpolation = #{interpolation}
def t_ANY_INTERPOLATION(t):
    r'\#\{[a-zA-Z0-9-_]+\}'
    return t

def t_ANY_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Regular expression rules for simple tokens
def t_TEXT(t):
    r'[\|\s]\s*(?:(?!\#\{)(?!\#\[)[^\n])*'
    return t


# id = #id
def t_ANY_ID(t):
    r'\#[a-zA-Z][a-zA-Z0-9-]*'
    return t

# class = .class
def t_ANY_CLASS(t):
    r'\.[a-zA-Z][a-zA-Z0-9-_]*'
    return t

# attribute = (attr) - '(' then catch all untill ')' then ')'
def t_ANY_ATTR(t):
    r'\([^\)]+\)'
    return t

# unbuffered comment = //-comment
def t_ANY_UNBUFFCOMMENT(t):
    r'//-.*'
    return t

# comment = //comment
def t_ANY_COMMENT(t):
    r'//.*'
    return t

# assignment = =variable
def t_ANY_ASSIGN(t):
    r'\=\s*[a-zA-Z0-9-_]+'
    return t

def t_eof(t):
    # Add your logic for handling the end of file here
    # For example, add DEDENT tokens to the end of the token stream
    while t.lexer.indent_level > 0:
        tok = lex.LexToken()
        tok.type = 'DEDENT'
        tok.value = None
        tok.lineno = t.lineno
        tok.lexpos = t.lexpos
        t.lexer.token_stream.append(tok)
        t.lexer.indent_level -= 1

    # Return the next token from the token stream, or None if the stream is empty
    return t.lexer.token_stream.pop(0) if t.lexer.token_stream else None
    
               
# A string containing ignored characters (spaces and tabs)
t_ignore  = ''

# Error handling rule
def t_ANY_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


# Build the lexer
lexer = lex.lex()
lexer.stack = list()
lexer.indent_level = 0
lexer.token_stream = []

data = """html
    head
        title= page_title
        p Welcome
    body
        h1 Title
        p Welcome
"""

lexer.input(data)


for tok in lexer:
    print(tok)


















# # for tok in lexer:
# #     print(tok)

# tokens = []
# for tok in lexer:
#     tokens.append(tok)

# # Manually inject a token at the end of the token stream
# while lexer.indent_level > 0:
#     prev_token = tokens[-1]
#     num_newlines = prev_token.value.count('\n')
#     injected_token = lex.LexToken()
#     injected_token.type = 'DEDENT'
#     injected_token.value = '\n    '
#     injected_token.lineno = prev_token.lineno + num_newlines
#     injected_token.lexpos = len(tokens)
#     tokens.append(injected_token)
#     lexer.indent_level -= 1

# lexer.token = lambda: None

# # Iterate over the tokens again, including the manually injected token
# for token in tokens:
#     print(token)


# # Get all the tokens
# tokens = []
# for tok in lexer:
#     tokens.append(tok)

# # Manually inject a token at the end of the token stream
# while lexer.indent_level > 0:
#     prev_token = tokens[-1]
#     injected_token = lex.LexToken()
#     injected_token.type = 'DEDENT'
#     injected_token.value = '\n' + '    ' * lexer.indent_level
#     injected_token.lineno = prev_token.lineno + 1
#     injected_token.lexpos = len(tokens)
#     tokens.append(injected_token)
#     lexer.indent_level -= 1

# # Iterate over the sorted tokens
# for token in tokens:
#     print(token)