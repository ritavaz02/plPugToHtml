import ply.yacc as yacc

from lex import tokens

"""

expression : empression NUMBER PLUS term
           | expression NUMBER MINUS term
           | NUMBER 

term : term TIMES NUMBER
     | term DIVIDE NUMBER
     | NUMBER



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


    '''
html
  head
    title= pageTitle
    meta(name='description', content='Example Pug code with 5 levels of hierarchy')
    // This is a comment inside the head tag
  body
    h1#main-heading.main-title Welcome to #[strong my website {inter}]
    p #[q(lang="en") This] is some text on the page list [1,2,3] dict {a,b,c}.
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
            //- This is an unbuffered comment inside a li tag ! 


TAG <html>
INDENT 
  TAG <head>
    INDENT 
      TAG ASSIGN <title>
      TAG ATTR <meta>
      COMMENT
    DEDENT </head>
  TAG <body>
    INDENT 
      TAG ID CLASS TEXT TAGINTERPOLATION_START TAG TAGINTERPOLATION_TEXT TAGINTERPOLATION_END
      TAG TAGINTERPOLATION_START TAG ATTR TAGINTERPOLATION_TEXT TAGINTERPOLATION_END TEXT
      UNBUFFCOMMENT
      TAG TEXT
      TAG <ul>
        INDENT 
          TAG TEXT INTERPOLATION
          COMMENT
          UNBUFFCOMMENT
          TAG <li>
            INDENT 
              TAG ATTR TEXT
            DEDENT </li>
          TAG <li>
            INDENT 
              TAG ATTR TEXT
              UNBUFFCOMMENT
            DEDENT </li>
        DEDENT </ul>
    DEDENT </body>
DEDENT </html>

TAG
TAG | INDENT TAG
INDENT TAG | TAG | COMMENT | DEDENT | UNBUFFCOMMENT

TAG : ASSIGN | ID | TAGINTERPOLATION_START | TEXT | ATTR
ID : CLASS | TEXTO | TAGINTERPOLATION_START



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

empty ::= 


"""