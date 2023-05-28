import ply.yacc as yacc
import re

from lexer import tokens

"""
Bottom up parsing

minipug ::= elemList

elemList ::= elemList elem
           | elemList inside
           | elem
           | inside

elem ::= init components insides INDENT elemList DEDENT
       | init components insides assign
       | comment
       | unbuffcomment
       | DOCTYPE

init ::= TAG
       | CLASS
       | ID

comment ::= COMMENT content

unbuffcomment ::= UNBUFFCOMMENT content

content ::= content CONTENT
          | epsilon

attributes ::= attributes ATTRIBUTE
            | ATTRIBUTE

styles ::= styles style
        | style

style ::= CLASS
       | ID

components ::- components attributes
          | components styles
          | epsilon

insides ::= insides inside
          | epsilon

inside ::= INTERPOLATION
         | tag_interpolation
         | TEXT

assign ::= ASSIGN
        | epsilon

tag_interpolation ::= TAGINTERPOLATION_START TAG components assign insides TAGINTERPOLATION_END
                    | TAGINTERPOLATION_TEXT

"""


def p_minipug(p):
    """minipug : elemList"""
    all = ''
    for elem in p[1]:
        all += elem
    p[0] = f'{all}'

    # print("p_minipug", p[0])


def p_elemList(p):
    """elemList : elemList elem
                | elemList inside"""
    if type(p[2]) == list:
        p[1].extend(p[2])
    else:
        p[1].append(p[2])
    p[0] = p[1]
    # print("p_elemList", p[0])


def p_elemList_elem(p):
    """elemList : elem
                | inside"""
    if type(p[1]) == list:
        p[0] = p[1]
    else:
        p[0] = [p[1]]
    # print("p_elemList_elem", p[0])


def p_init_tag(p):
    """init : TAG"""
    p[0] = ("tag", p[1])


def p_init_div(p):
    """init : CLASS
            | ID"""
    p[0] = ("div", p[1])


def p_elem_tag(p):
    """elem : init components insides assign"""
    atts = ''
    tag = ''
    # print(p[2])
    mydict = dict(p[2])
    if p[1][0] == "tag":
        tag += p[1][1]
    else:
        tag += p[1][0]
        p[2] = 1
    if p[2]:
        if p[1][0] == "div":
            if p[1][1].startswith("."):
                if "class" in mydict:
                    classes = mydict["class"]
                    mydict["class"] = p[1][1][1:] + ' ' + classes
                else:
                    mydict["class"] = p[1][1][1:]
            if p[1][1].startswith("#"):
                mydict["id"] = p[1][1][1:]
        for key, value in mydict.items():
            if key != 'attr':
                atts += f'{key}="{value}" '
            else:
                atts += f'{value}'
    if p[4] is not None:
        if atts == '':
            p[0] = f'<{tag}> {p[4]} </{tag}>'
        else:
            p[0] = f'<{tag} {atts.rstrip()}> {p[4]} </{tag}>'
    elif p[3] == '' and tag != "div":
        if atts == '':
            p[0] = f'<{tag}/>'
        else:
            p[0] = f'<{tag} {atts.rstrip()}/>'
    else:
        if atts == '':
            p[0] = f'<{tag}>{p[3]} </{tag}>'
        else:
            p[0] = f'<{tag} {atts.rstrip()}>{p[3]} </{tag}>'
    # print("p_elem_tag", p[0])


def p_elem(p):
    """elem : init components insides INDENT elemList DEDENT"""
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
            if p[1][1].startswith("."):
                if "class" in mydict:
                    classes = mydict["class"]
                    mydict["class"] = p[1][1][1:] + ' ' + classes
                else:
                    mydict["class"] = p[1][1][1:]
            if p[1][1].startswith("#"):
                mydict["id"] = p[1][1][1:]
        for key, value in mydict.items():
            if key != 'attr':
                atts += f'{key}="{value}" '
            else:
                atts += f'{value}'
    elemList = ''
    tabs = p[4] * '    '
    tabs2 = tabs + '    '

    for value in p[5]:
        if value != '':
            elemList += tabs2 + value + '\n'

    if atts == '':
        p[0] = f'<{tag}>\n{p[3]}{elemList}{tabs}</{tag}>'.replace('\\n', '\n')
    else:
        p[0] = f'<{tag} {atts.rstrip()}>\n{p[3]}{elemList}{tabs}</{tag}>'.replace('\\n', '\n')
    # print("p_elem", p[0])


def p_elem_comment(p):
    """elem : comment"""
    p[1][0] = f"<!--{p[1][0]}"
    p[1][-1] = f"{p[1][-1]} -->"
    for i in range(1, len(p[1])):
        p[1][i] = f"    {p[1][i]}"
    p[0] = p[1]
    # print("p_elem_comment", p[0])


def p_elem_unbuffcomment(p):
    """elem : UNBUFFCOMMENT content"""
    # print("p_elem_unbuffcomment")
    p[0] = ''


def p_elem_doctype(p):
    """elem : DOCTYPE"""
    # print("p_elem_doctype", p[0])
    p[0] = '<!DOCTYPE html>\n   '


def p_comment(p):
    """comment : COMMENT content"""
    comment = list(p[2])
    comment.insert(0, p[1])
    p[0] = comment
    # print("p_comment: ", p[0])


def p_content(p):
    """content : content CONTENT"""
    content = list(p[1])
    content.append(p[2])
    p[0] = content
    # print("p_content", p[0])


def p_content_epsilon(p):
    """content : """
    # print("p_content_epsilon", p[0])
    p[0] = ''


def styleFormat(string):
    # Encontre a parte entre chaves, começando por "style={"
    match = re.search(r"style=\{(.+?)\}", string)
    if match:
        content = match.group(1)
        content = re.sub(r"[\s'\"-]+", "", content)
        content = re.sub(r",", ";", content)

        result = 'style="' + content + ';"'
        return result

    return string


def p_attributes(p):
    """attributes : attributes ATTRIBUTE"""
    if p[2] == "checked":
        p[0] = p[1] + f' checked="checked"'
    elif p[2] == "checked=true":
        p[0] = p[1] + f' checked="checked"'
    elif p[2] == "checked=false":
        p[0] = p[1] + " "
    elif p[2].startswith("style="):
        p[0] = p[1] + f" {styleFormat(p[2])}"
    else:
        p[0] = p[1] + f" {p[2]}"
    # print("p_attributes", p[0])


def p_attributes_attribute(p):
    """attributes : ATTRIBUTE"""
    if p[1].startswith("style={"):
        p[0] = styleFormat(p[1])
    else:
        p[0] = p[1]
    # print("p_attributes_attribute", p[0])


def p_styles(p):
    """styles : styles style"""
    dictatts = {}
    if p[1]:
        dictatts = p[1]
        if p[2][0] in dictatts:
            if p[2][0] != "id":
                atts = dictatts[p[2][0]]
                dictatts[p[2][0]] = atts + ' ' + p[2][1]
        else:
            dictatts[p[2][0]] = p[2][1]
    else:
        dictatts[p[2][0]] = p[2][1]
    p[0] = dictatts
    # print("p_styles", p[0])


def p_styles_style(p):
    """styles : style"""
    p[0] = {p[1][0]: p[1][1]}


def p_style_class(p):
    """style : CLASS"""
    p[0] = ("class", p[1][1:])
    # print("p_style_class", p[0])


def p_style_id(p):
    """style : ID"""
    p[0] = ("id", p[1][1:])
    # print("p_style_id", p[0])


def p_components_attributes(p):
    """components : components attributes"""
    components = dict(p[1])
    # add attributes a components
    if "attr" in components:
        components["attr"] = components["attr"] + f" {p[2]}"
    else:
        components["attr"] = p[2]
    p[0] = components
    # print("p_components_attributes", p[0])


def p_components_styles(p):
    """components : components styles"""
    components = dict(p[1])
    #add conteudo de styles para components
    if p[2]:
        for key,value in p[2].items():
            if key in components:
                if key != 'id':
                    components[key] = components[key] + f" {value}"
            else:
                components[key] = value
    p[0] = components
    # print("p_components_styles", p[0])


def p_components_epsilon(p):
    """components : """
    p[0] = {}


def p_insides(p):
    """insides : insides inside"""
    if p[1]:
        p[0] = p[1] + ' ' + p[2]
    else:
        p[0] = p[2]
    # print("p_insides", p[0])


def p_insides_epsilon(p):
    """insides : """
    # print("p_insides_epsilon", p[0])
    p[0] = ''


def p_assign(p):
    """assign : ASSIGN"""
    var = f'{p[1][1:]}'
    # verify if dict exists
    if hasattr(parser, 'interpolation'):
        if var in parser.interpolation:
            p[0] = parser.interpolation[var]
        else:
            print(f"Error: {var} is not defined")
    else:
        print(f"Error: interpolation dictionay is not defined")
        p[0] = 'ERROR'
    # print("p_inside_assign", p[0])


def p_assign_epsilon(p):
    """assign : """
    pass


def p_inside_interpolation(p):
    """inside : INTERPOLATION"""
    var = f'{p[1][2:-1]}'  # remove #{}
    if hasattr(parser, 'interpolation'):
        if var in parser.interpolation:
            p[0] = parser.interpolation[var]
        else:
            print(f"Error: {var} is not defined")
    else:
        print(f"Error: interpolation dictionay is not defined")
        p[0] = 'ERROR'
    # print("p_inside_interpolation", p[0])


def p_inside_tag_interpolation(p):
    """inside : tag_interpolation"""
    p[0] = p[1]
    # print("p_inside_tag_interpolation", p[0])


def p_inside_text(p):
    """inside : TEXT"""
    if p[1][0] == "|":
        p[0] = p[1][1:]
    else:
        p[0] = p[1]
    # print("p_inside_text", p[0])


def p_tag_interpolation(p):
    """tag_interpolation : TAGINTERPOLATION_START TAG components insides assign TAGINTERPOLATION_END"""
    atts = ''
    mydict = dict(p[3])
    if p[3]:
        for key, value in mydict.items():
            if key != 'attr':
                atts += f'{key}="{value}" '
            else:
                atts += f'{value}'
    if p[5] is not None:
        if not atts:
            p[0] = f'<{p[2]}> {p[5]} </{p[2]}>'
        else:
            p[0] = f'<{p[2]} {atts.rstrip()}> {p[5]} </{p[2]}>'
    elif p[4] == '':
        if not atts:
            p[0] = f'<{p[2]}/>'
        else:
            p[0] = f'<{p[2]} {atts.rstrip()}/>'
    else:
        if not atts:
            p[0] = f'<{p[2]}>{p[4]} </{p[2]}>'
        else:
            p[0] = f'<{p[2]} {atts.rstrip()}>{p[4]} </{p[2]}>'
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


parser = yacc.yacc(debug=True)
