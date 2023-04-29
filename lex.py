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
    'ASSIGN',
    'TAGINTERPOLATION_START',
    'TAGINTERPOLATION_END',
    'TAGINTERPOLATION_TEXT',
    'TAGINTERPOLATION_TEXT_OPEN'
)

states = (
    ('taginterpolation', 'inclusive'),
)

previous_indents = 0
indent_stack = [0]

# tag name
def t_ANY_TAG(t):
    r'[a-zA-Z0-9]+(?![a-zA-Z0-9,])'
    return t


def t_INDENT_DEDENT(t):
    r'(?<=\n)(\s|\$)+'
    indent = len(t.value.strip('\n'))//4
    global total_lines
    if '$' in t.value:
        t.type = 'DEDENT'
        t.value = t.lexer.indent_level - 1
        t.lexer.indent_level = t.lexer.indent_level - 1
        return t
    else:
        if indent > t.lexer.indent_level:
            t.type = 'INDENT'
            t.value = indent
            t.lexer.indent_level = indent
        elif indent < t.lexer.indent_level:
            t.type = 'DEDENT'
            t.value = t.lexer.indent_level - 1
            t.lexer.indent_level = t.lexer.indent_level - 1
            if indent < t.lexer.indent_level:
                t.lexer.lexpos = last_token_pos
                total_lines += t.lexer.lineno - last_lineno
        else:
            return
        #t.lexer.indent_level = indent
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
            t.type = 'TAGINTERPOLATION_TEXT'
    else:
        print('Nenhuma tag aberta.')
    return t


def t_taginterpolation_TAGINTERPOLATION_TEXT_OPEN(t):
    r'\s*\[\s?'
    t.lexer.stack.append('[')
    t.type = "TAGINTERPOLATION_TEXT"
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


def t_taginterpolation_TAGINTERPOLATION_TEXT(t):
    r'[^\[\n\]](?:(?!\#\{)(?!\#\[)[^\[\n\]])*'
    return t


# A string containing ignored characters (spaces and tabs)
t_ignore = ''


# Error handling rule
def t_ANY_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


# Build the lexer
lexer = lex.lex()
lexer.stack = list()
lexer.indent_level = 0
last_token_pos = lexer.lexpos
last_lineno = lexer.lineno
lexer.flag = 0
# a chave é o numero da linha
# o valor é o nível de indentação

# data = """
# html
#     head
#         title= pageTitle
#         meta(name='description', content='Example Pug code with 5 levels of hierarchy')
#         // This is a comment inside the head tag
#     body
#         h1#main-heading.main-title Welcome to #[strong my website {inter}]
#         p #[q(lang="en") This] is some text on the page list [1,2,3] dict {a,b,c}.

#         //- This is an unbuffered comment
#         p More text on the page.
#         ul
#             li item: #{item}
#             // This is a comment inside the for loop
#             //- This is an unbuffered comment inside the ul tag
#             li
#                 a(href='#') Click here for more information
#             li
#                 a(href='/about') About Us
#                 //- This is an unbuffered comment inside a li tag !
# $

# """

data = """html
    head
        title= Title
        p Welcome
    body
        h1 Title
        p Welcome home
$

# """

lexer.input(data)
total_lines = data.count('\n')
for tok in lexer:
    print(tok)
    if lexer.lineno == total_lines and lexer.indent_level > 0:
        lexer.lexpos = last_token_pos
        total_lines += 1
    last_token_pos = lexer.lexpos
    last_lineno = lexer.lineno

