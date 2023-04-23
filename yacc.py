import ply.yacc as yacc

from lex import tokens
"""

TOP DOWN PARSING

document ::= element_list

element_list ::= element_list_tail element

element_list_tail ::= empty
                      | element_list_tail element_indent

element_indent ::= element INDENT element_list_tail DEDENT

element ::= TAG attributes block
           | TEXT
           | COMMENT
           | UNBUFFCOMMENT
           | INTERPOLATION
           | TAGINTERPOLATION_START tag_interpolation TAGINTERPOLATION_END

block ::= INDENT element_list DEDENT
         | element

tag_interpolation ::= TAGINTERPOLATION_TEXT
                     | TAGINTERPOLATION_TEXT_OPEN tag_interpolation TAGINTERPOLATION_END

attributes ::= attribute attributes
               | attribute

attribute ::= ID
             | CLASS
             | ATTR
             | ASSIGN


"""

"""
BOTTOM UP PARSING

z ::= element_list '$'

element_list ::= element_list element_indent
               | element

element_indent ::= element INDENT element_list DEDENT

element ::= TAG attributes block
           | TAG attributes
           | TAG block
           | TAG
           | TEXT
           | COMMENT
           | UNBUFFCOMMENT
           | INTERPOLATION
           | TAGINTERPOLATION_START tag_interpolation TAGINTERPOLATION_END
block ::= INDENT element_list DEDENT
         | element
tag_interpolation ::= TAGINTERPOLATION_TEXT
                     | TAGINTERPOLATION_TEXT_OPEN tag_interpolation TAGINTERPOLATION_END
attributes ::= attribute attributes
               | attribute
attribute ::= ID
             | CLASS
             | ATTR
             | ASSIGN
          
"""

data = """html
    head
        title= page_title
        p Welcome
    body
        h1 Title
        p Welcome
"""


tag_stack = []

def p_element_list(p):
  '''element_list : element_list element_indent'''
  p[1].append(p[2])
  p[0] = p[1]
  print("p_element_list: ", p[0])
               
def p_element_list_single(p):
  '''element_list : element'''
  p[0] = [p[1]]
  print("p_element_single: ", p[0])

def p_element_indent(p):
  '''element_indent : element INDENT element_list DEDENT'''
  if isinstance(p[3], list):
    p[0] = {
      "parent": p[1],
      "children": p[3]
    }
  else:
    p[0] = {
      "parent": p[1],
      "children": [p[3]]
    }
  print("p_element_indent: ", p[0])

def p_element_tag(p):
  '''element : TAG'''
  p[0] = {
    "tag": p[1],
  }
  tag_stack.append(p[1])
  print("p_element_tag: ", p[0])

def p_element_tag_att_block(p):
  '''element : TAG attributes block'''
  p[0] = {
    "tag": p[1],
    "attributes": p[2],
    "block": p[3]
  }
  tag_stack.append(p[1])
  print("p_element_tag_att_block: ", p[0])

def p_element_tag_att(p):
  '''element : TAG attributes'''
  p[0] = {
    "tag": p[1],
    "attributes": p[2]
  }
  tag_stack.append(p[1])
  print("p_element_tag_att: ", p[0])

def p_element_tag_block(p):
  '''element : TAG block'''
  p[0] = {
    "tag": p[1],
    "block": p[2]
  }
  tag_stack.append(p[1])
  print("p_element_tag_block: ", p[0])

def p_element_text(p):
  '''element : TEXT'''
  p[0] = {
    "type": "text",
    "content": p[1]
  }
  print("p_element_text: ", p[0])

def p_element_comment(p):
  '''element : COMMENT'''
  p[0] = {
    "type": "comment",
    "content": p[1]
  }
  print("p_element_comment: ", p[0])

def p_element_unbuffcomment(p):
  '''element : UNBUFFCOMMENT'''
  p[0] = {
    "type": "unbuffcomment",
    "content": p[1]
  }
  print("p_element_unbuffcomment: ", p[0])

def p_element_interpolation(p):
  '''element : INTERPOLATION'''
  p[0] = {
    "type": "interpolation",
    "content": p[1][2:-1] #texto dentro de #{}
  }
  print("p_element_interpolation: ", p[0])

def p_element_taginterpolation(p):
  '''element : TAGINTERPOLATION_START tag_interpolation TAGINTERPOLATION_END'''
  p[0] = {
    "type": "tag_interpolation",
    "content": p[2]
  }
  print("p_element_taginterpolation: ", p[0])


def p_block(p):
  '''block : INDENT element_list DEDENT'''
  p[0] =  p[2]
  print("p_block: ", p[0])

def p_block_single(p):
  '''block : element'''
  p[0] = [p[1]]
  print("p_block_single: ", p[0])

def p_tag_interpolation_text(p):
  '''tag_interpolation : TAGINTERPOLATION_TEXT'''
  p[0] = p[1]
  print("p_tag_interpolation_text: ", p[0])

def p_tag_interpolation(p):
  '''tag_interpolation : TAGINTERPOLATION_TEXT_OPEN tag_interpolation TAGINTERPOLATION_END'''
  p[0] =  p[2]
  print("p_tag_interpolation: ", p[0])

def p_atributes(p):
  '''attributes : attribute attributes'''
  p[2].append(p[1])
  p[0] = p[2]
  print("p_atributes: ", p[0])

def p_atributes_single(p):
  '''attributes : attribute'''
  p[0] = [p[1]]
  print("p_atributes_single: ", p[0])

def p_attributes(p):
  '''attributes : epsilon'''
  p[0] = []
  print("p_atributes: ", p[0])

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
  


def p_error(p):
  if p:
    print(f"Syntax error at token {p.type} ({p.value}), line {p.lineno}, column {p.lexpos}")
  else:
    print("Syntax error at EOF")

parser = yacc.yacc()
output = parser.parse(data)
print(output)