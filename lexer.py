import ply.lex as lex
from ply.lex import LexToken

# List of token names.
tokens = (
    'DOCTYPE',
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
    'TAGINTERPOLATION_TEXT_OPEN',
    'CONTENT',
    'ATTRIBUTE',
    'IGNORE'
)

states = (
    ('taginterpolation', 'inclusive'),
    ('commentblock', 'exclusive'),
    ('attributes', 'exclusive')
)

previous_state = None

def t_DOCTYPE(t):
    r'doctype\s+html'
    return t

def t_commentblock_CONTENT(t):
    r'[^\s].+'
    return t

def t_attributes_ATTRIBUTE(t):
    r'[a-z]+(={[^{}]+}|[^\),\s]+)?'
    return t

def t_attributes_IGNORE(t):
    r',\s'
    pass

# tag name
def t_ANY_TAG(t):
    r'[a-zA-Z0-9]+(?![a-zA-Z0-9,])'
    return t


dedent_tokens = []


def t_ANY_INDENT_DEDENT(t):
    r'(?<=\n)\s+'
    indent = len(t.value.strip('\n')) // 4
    global dedent_tokens
    if indent > t.lexer.indent_level:
        if t.lexer.current_state() == 'INITIAL':
            t.type = 'INDENT'
            t.value = indent
            t.lexer.indent_level = indent
        else:
            return
    elif indent < t.lexer.indent_level:
        if t.lexer.current_state() == 'commentblock':
            t.lexer.begin('INITIAL')
        if t.lexer.current_state() == 'INITIAL':
            while indent < t.lexer.indent_level:
                t.type = 'DEDENT'
                t.value = t.lexer.indent_level - 1
                t.lexer.indent_level = t.lexer.indent_level - 1
                dedent_tokens.append(t)
            # print(dedent_tokens)
            return dedent_tokens.pop(0) if dedent_tokens else None
    else:
        if t.lexer.current_state() == 'commentblock':
            t.lexer.begin('INITIAL')
        return
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
    r'\(|\)'
    global previous_state
    if t.value == '(':
        previous_state= t.lexer.current_state()
        t.lexer.begin('attributes')
    else:
        t.lexer.begin(previous_state)
    pass


# unbuffered comment = //-comment
def t_ANY_UNBUFFCOMMENT(t):
    r'//-(?P<content>.*)'
    if len(t.value) > 2:
        t.lexer.begin('commentblock')
    t.value = t.lexer.lexmatch.group('content')
    return t


# comment = //comment
def t_ANY_COMMENT(t):
    r'//(?P<content>.*)'
    if len(t.value) > 2:
        t.lexer.begin('commentblock')
    t.value = t.lexer.lexmatch.group('content')
    return t


# assignment = =variable
def t_ANY_ASSIGN(t):
    r'\=\s*[a-zA-Z0-9-_]+'
    return t


def t_taginterpolation_TAGINTERPOLATION_TEXT(t):
    r'[^\[\n\]](?:(?!\#\{)(?!\#\[)[^\[\n\]])*'
    return t


def t_eof(t):
    if lexer.indent_level > 0:
        t.type = 'DEDENT'
        t.value = lexer.indent_level - 1
        lexer.indent_level -= 1
        return t
    else:
        return None


# A string containing ignored characters (spaces and tabs)
t_ignore = ''


# # Error handling rule
def t_ANY_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


# Build the lexer
lexer = lex.lex()
original_token = lexer.token


def custom_token():
    if dedent_tokens:
        return dedent_tokens.pop(0)
    return original_token()


lexer.token = custom_token
lexer.stack = list()
lexer.indent_level = 0