import ply.lex as lex

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
    'ASSIGN'
)

# tag name
def t_TAG(t):
    r'[a-zA-Z][a-zA-Z0-9]*'
    return t


def t_INDENT_DEDENT(t):
    r'(?:\n)[\s\t]+'
    indent = len(t.value.strip('\n'))
    if indent > t.lexer.indent_level:
        t.type = 'INDENT'
        t.value = indent
    elif indent < t.lexer.indent_level:
        t.type = 'DEDENT'
        t.value = t.lexer.indent_level - indent
    else:
        return
    t.lexer.indent_level = indent
    return t

# interpolation = #{interpolation}
def t_INTERPOLATION(t):
    r'\#\{[a-zA-Z0-9-_]+\}'
    return t

# Regular expression rules for simple tokens
def t_TEXT(t):
    r'[\|\s]\s*[^\{\n]+(?!{)'
    return t

# id = #id
def t_ID(t):
    r'\#[a-zA-Z][a-zA-Z0-9-]*'
    return t

# class = .class
def t_CLASS(t):
    r'\.[a-zA-Z][a-zA-Z0-9-_]*'
    return t

# attribute = (attr) - '(' then catch all untill ')' then ')'
def t_ATTR(t):
    r'\([^\)]+\)'
    return t

# unbuffered comment = //-comment
def t_UNBUFFCOMMENT(t):
    r'//-.*'
    return t

# comment = //comment
def t_COMMENT(t):
    r'//.*'
    return t

# assignment = =variable
def t_ASSIGN(t):
    r'\=\s*[a-zA-Z0-9-_]+'
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


# A string containing ignored characters (spaces and tabs)
t_ignore  = ''

# Error handling rule
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

# Build the lexer
lexer = lex.lex()

lexer.indent_level = 0

data = '''html
  head
    title= pageTitle
    meta(name='description', content='Example Pug code with 5 levels of hierarchy')
    // This is a comment inside the head tag
  body
    h1#main-heading.main-title Welcome to my website
    p This is some text on the page.
    //- This is an unbuffered comment
    p More text on the page.
    ul
        li item: #{item}
        // This is a comment inside the for loop
      //- This is an unbuffered comment inside the ul tag
      li
        a(href='#') Click here for more information
      li
        a(href='/about') About Us
        //- This is an unbuffered comment inside a li tag ! '''

# Give the lexer some input
lexer.input(data)

for tok in lexer:
    print(tok)
    print(tok.type, tok.value, tok.lineno, tok.lexpos)