import ply.yacc as yacc

from lex import tokens

"""
BOTTOM UP PARSING
z ::= linelist '$'

lineList ::= lineList line 
          | line
          
line ::= TAG
        | INDENT lineList DEDENT
        | TAG block
        | TAG attributes
        | TAG attributes block
        | attributes block

attributes ::= attributes attribute
             | attribute

attribute ::= ID
             | CLASS
             | ATTR
             | ASSIGN

block ::= TEXT
        | COMMENT
        | UNBUFFCOMMENT
        | INTERPOLATION
        | TAGINTERPOLATION_START tag_interpolation TAGINTERPOLATION_END
        | INDENT lineList DEDENT

tag_interpolation ::= TAGINTERPOLATION_TEXT
                     | TAGINTERPOLATION_TEXT_OPEN tag_interpolation TAGINTERPOLATION_END

"""

data = """html
    head
        title= Title
        p Welcome
    body
        h1 Title
        p Welcome home
$

"""

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


tag_stack = []

def p_linelist(p):
    '''linelist : linelist line'''
    p[1].append(p[2])
    p[0] = p[1]
    print("p_linelist: ", p[0])

def p_linelist_line(p):
    '''linelist : line'''
    p[0] = [p[1]]
    print("p_linelist_line: ", p[0])


# def p_linelist_indent(p):
#     '''content : linelist'''
#     p[0] = p[1]
#     print("p_linelist_indent: ", p[0])

# def p_linelist_indent(p):
#     '''linelist : INDENT line'''
#     p[0] = [p[2]]
#     print("p_linelist_indent: ", p[0])

# def p_linelist_dedent(p):
#     '''linelist : DEDENT line'''
#     p[0] = [p[2]]
#     print("p_linelist_dedent: ", p[0])



def p_line_tag(p):
    '''line : TAG'''
    p[0] = {
        "tag": p[1]
    }
    tag_stack.append(p[1])
    print("p_element_tag: ", p[0])


def p_line_indent(p):
    '''line : INDENT linelist DEDENT'''
    p[0] = {
        "tag": tag_stack.pop(),
        "block": p[2]
    }
    print("p_element_indent: ", p[0])

def p_line_tag_block(p):
    '''line : TAG block'''
    p[0] = {
        "tag": p[1],
        "block": p[2]
    }
    tag_stack.append(p[1])
    print("p_element_tag_block: ", p[0])

def p_line_tag_attributes(p):
    '''line : TAG attributes'''
    p[0] = {
        "tag": p[1],
        "attributes": p[2]
    }
    tag_stack.append(p[1])
    print("p_element_tag_attributes: ", p[0])

def p_line_tag_attributes_block(p):
    '''line : TAG attributes block'''
    p[0] = {
        "tag": p[1],
        "attributes": p[2],
        "block": p[3]
    }
    tag_stack.append(p[1])
    print("p_element_tag_attributes_block: ", p[0])

def p_line_attributes_block(p):
    '''line : attributes block'''
    p[0] = {
        "tag": tag_stack.pop(),
        "attributes": p[1],
        "block": p[2]
    }
    print("p_element_attributes_block: ", p[0])

def p_attributes_attribute(p):
    '''attributes : attributes attribute'''
    p[1].append(p[2])
    p[0] = p[1]
    print("p_attributes_attribute: ", p[0])

def p_attributes_attribute_single(p):
    '''attributes : attribute'''
    p[0] = [p[1]]
    print("p_attributes_attribute_single: ", p[0])

def p_attribute_id(p):
    '''attribute : ID'''
    p[0] = {
      "name": "id",
      "value": p[1][1:] #remove #
    }
    print("p_atribute_id: ", p[0])

def p_attribute_class(p):
  '''attribute : CLASS'''
  p[0] = {
    "name": "class",
    "value": p[1][1:] #remove .
  }
  print("p_attribute_class: ", p[0])

def p_attribute_attr(p):
  '''attribute : ATTR'''
  p[0] = {
    "name": "attr",
    "value": p[1][1:-1] #remove parêntesis ao redor
  }
  print("p_attribute_attr: ", p[0])

def p_attribute_assign(p):
  '''attribute : ASSIGN'''
  p[0] = {
    "name": "assign",
    "value": p[1][1:] #remove =
  }
  print("p_attribute_assign: ", p[0])
  
def p_block_text(p):
    '''block : TEXT'''
    p[0] = {
        "type": "text",
        "value": p[1]
    }
    print("p_block_text: ", p[0])

def p_block_comment(p):
    '''block : COMMENT'''
    p[0] = {
        "type": "comment",
        "value": p[1]
    }
    print("p_block_comment: ", p[0])

def p_block_unbuffcomment(p):
    '''block : UNBUFFCOMMENT'''
    p[0] = {
        "type": "unbuffcomment",
        "value": p[1]
    }
    print("p_block_unbuffcomment: ", p[0])

def p_block_interpolation(p):
    '''block : INTERPOLATION'''
    p[0] = {
        "type": "interpolation",
        "value": p[1][2:-1] #texto dentro de #{}
    }
    print("p_block_interpolation: ", p[0])

def p_block_taginterpolation(p):
    '''block : TAGINTERPOLATION_START tag_interpolation TAGINTERPOLATION_END'''
    p[0] = {
        "type": "taginterpolation",
        "value": p[2],
    }
    print("p_block_taginterpolation: ", p[0])

def p_block_indent(p):
    '''block : INDENT linelist DEDENT'''
    p[0] = p[2]
    print("p_block_indent: ", p[0])

def p_taginterpolation_text(p):
    '''tag_interpolation : TAGINTERPOLATION_TEXT'''
    p[0] = {
        "type": "text",
        "value": p[1]
    }
    print("p_taginterpolation_text: ", p[0])

def p_taginterpolation_text_open(p):
    '''tag_interpolation : TAGINTERPOLATION_TEXT_OPEN tag_interpolation TAGINTERPOLATION_END'''
    # p[0] = {
    #     "type": "text",
    #     "value": p[1] + p[2]["value"]
    # }
    p[0] = p[2]
    print("p_taginterpolation_text_open: ", p[0])


def p_error(p):
  if p:
    print(f"Syntax error at token {p.type} ({p.value}), line {p.lineno}, column {p.lexpos}")
  else:
    print("Syntax error at EOF")

parser = yacc.yacc()
output = parser.parse(data)

print("\noutput: ")
print(output)