import ply.yacc as yacc

from lexer import tokens

"""
Bottom up parsing

minipug ::= elemList

elemList ::= elemList elem
           | epsilon

elem ::= TAG attributes insides INDENT elemList DEDENT
       | TAG attributes insides
       | comment
       | unbuffcomment
       | DOCTYPE

init ::= TAG
       | CLASS

comment ::= COMMENT content

unbuffcomment ::= UNBUFFCOMMENT content

content ::= content CONTENT
          | epsilon

attributes ::= attributes attribute
             | epsilon

attribute ::= ATTR
            | CLASS
            | ID

insides ::= insides inside
          | epsilon

inside ::= ASSIGN
         | INTERPOLATION
         | tag_interpolation
         | TEXT

tag_interpolation ::= TAGINTERPOLATION_START TAG attributes insides TAGINTERPOLATION_END
                    | TAGINTERPOLATION_TEXT

"""

data = """doctype html
html
    head.HEAD
        meta(charset="UTF-8")
        meta(name="viewport", content="width=device-width, initial-scale=1.0")
        link(rel="stylesheet", href="styles.css")
        title My Pug Example
    body
        //-
            cont
            cont
        header#id.classe.classe2
            h1 Welcome to My Pug Example
        main.main.outra.aaa
            section.sec
                .section
                    p Div
                h2 #[b About] me
                p This is a simple example of a Pug template with nested elements and 4 spaces for indentation.
            .div
                .divdentro.classedentro
                    .divdentrooo
            section
                h2 Contact
                ul
                    li.classeli Email: example@example.com
                    li Phone: +1 123 456 7890
        footer
            p Copyright Â© 2023 - All Rights Reserved
"""


def p_minipug(p):
    """minipug : elemList"""
    p[0] = p[1]

    # print("p_minipug", p[0])


def p_elemList(p):
    """elemList : elemList elem"""
    p[0] = f'{p[1]} {p[2]} '
    #print("p_elemList", p[0])


def p_elemList_elem(p):
    """elemList : elem"""
    # print(p[1])
    p[0] = p[1]
    #print("p_elemList_elem", p[0])


# def p_elemList_epsilon(p):
#     """elemList : """
#     print("p_elemList_epsilon", p[0])
#     p[0] = ''


def p_init_tag(p):
    """init : TAG"""
    p[0] = ("tag", p[1])

def p_init_div(p):
    """init : CLASS"""
    p[0] = ("div", p[1][1:])

def p_elem_tag(p):
    """elem : init attributes insides"""
    atts = ''
    tag = ''
    mydict = dict(p[2])
    if p[1][0] == "tag":
        tag += p[1][1]
    else:
        tag += p[1][0]
        p[2] = 1
    if p[2]:
        if p[1][0] == "div":
            if "class" in mydict:
                classes = mydict["class"]
                mydict["class"] = p[1][1] + ' ' + classes
            else:
                mydict["class"] = p[1][1]
        for key, value in mydict.items():
            if key != 'attr':
                atts += f'{key}="{value}" '
            else:
                atts += f'{value}'
    if p[3] == '' and tag != "div":
        p[0] = f'<{tag} {atts}/>'
    else:
        p[0] = f'<{tag} {atts}> {p[3]} </{tag}>'
    print("p_elem_tag", p[0])


def p_elem(p):
    """elem : init attributes insides INDENT elemList DEDENT"""
    atts = ''
    mydict = dict(p[2])
    tag = ''
    if p[1][0] == "tag":
        tag += p[1][1]
    else:
        tag += p[1][0]
        p[2] = 1
    if p[2]:
        if p[1][0] == "div":
            if "class" in mydict:
                classes = mydict["class"]
                mydict["class"] = p[1][1] + ' ' + classes
            else:
                mydict["class"] = p[1][1]
        for key, value in mydict.items():
            if key != 'attr':
                atts += f'{key}="{value}" '
            else:
                atts += f'{value}'
    p[0] = f'<{tag} {atts}>{p[3]} {p[5]}</{tag}>'
    #print("p_elem", p[0])




def p_elem_comment(p):
    """elem : comment"""
    p[0] = p[1]
    # print("p_elem_comment", p[0])


def p_elem_unbuffcomment(p):
    """elem : UNBUFFCOMMENT content"""
    #print("p_elem_unbuffcomment")
    p[0] = ''


def p_elem_doctype(p):
    """elem : DOCTYPE"""
    # print("p_elem_doctype", p[0])
    p[0] = '<!DOCTYPE html>'


def p_comment(p):
    """comment : COMMENT content"""
    p[0] = f'<!--{p[2]}-->'
    # print("p_comment", p[0])


def p_content(p):
    """content : content CONTENT"""
    p[0] = p[1] + f' {p[2]}'
    # print("p_content", p[0])


def p_content_epsilon(p):
    """content : """
    # print("p_content_epsilon", p[0])
    p[0] = ''


def p_attributes(p):
    """attributes : attributes attribute"""
    dictatts = {}
    if p[1]:
        dictatts = p[1]
        if p[2][0] in dictatts:
            atts = dictatts[p[2][0]]
            dictatts[p[2][0]] = atts + ' ' + p[2][1]
        else:
            dictatts[p[2][0]] = p[2][1]
    else:
        dictatts[p[2][0]] = p[2][1]
    p[0] = dictatts
    #print("p_attributes", p[0])


def p_attributes_epsilon(p):
    """attributes : """
    p[0] = ''


def p_attribute_id(p):
    """attribute : ID"""
    # p[0] = f'id="{p[1][1:]}" '  # remove #
    p[0] = ("id", p[1][1:])
    #print("p_attribute_id", p[0])


def p_attribute_class(p):
    """attribute : CLASS"""
    # p[0] = f'class="{p[1][1:]}" '  # remove .
    p[0] = ("class", p[1][1:])
    #print("p_attribute_class", p[0])


def p_attribute_attr(p):
    """attribute : ATTR"""
    # p[0] = f'{p[1][1:-1]} '  # remove []
    p[0] = ("attr", f'{p[1][1:-1]}')
    # print("p_attribute_attr", p[0])


def p_insides(p):
    """insides : insides inside"""
    if (p[1]):
        p[0] = p[1] + ' ' + p[2]
    else:
        p[0] = p[2]
    # print("p_insides", p[0])


def p_insides_epsilon(p):
    """insides : """
    # print("p_insides_epsilon", p[0])
    p[0] = ''


def p_inside_assign(p):
    """inside : ASSIGN"""
    p[0] = f'{p[1][1:]}'  # remove =
    # print("p_inside_assign", p[0])


def p_inside_interpolation(p):
    """inside : INTERPOLATION"""
    p[0] = f'{p[1][2:-1]}'  # remove #{}
    # print("p_inside_interpolation", p[0])


def p_inside_tag_interpolation(p):
    """inside : tag_interpolation"""
    p[0] = p[1]
    # print("p_inside_tag_interpolation", p[0])


def p_inside_text(p):
    """inside : TEXT"""
    p[0] = p[1]
    # print("p_inside_text", p[0])


def p_tag_interpolation(p):
    """tag_interpolation : TAGINTERPOLATION_START TAG attributes insides TAGINTERPOLATION_END"""
    p[0] = f'<{p[2]} {p[3]}> {p[4]} </{p[2]}>'
    # print("p_tag_interpolation", p[0])


def p_tag_interpolation_text(p):
    """tag_interpolation : TAGINTERPOLATION_TEXT"""
    p[0] = p[1]
    # print("p_tag_interpolation_text", p[0])


def p_error(p):
    if p:
        print(f"Syntax error at token {p.type} ({p.value}), line {p.lineno}, column {p.lexpos}")
    else:
        print("Syntax error at EOF")


# parser = yacc.yacc()
parser = yacc.yacc(debug=True)
output = parser.parse(data)
print("\noutput: ")
print(output)

