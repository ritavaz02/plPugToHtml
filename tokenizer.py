import sys
from lexer import lexer
from yacc import parser

# Read input
text = sys.stdin.read()

# Give the lexer some input
lexer.input(text)

# Tokenize
parser.success = True
output = parser.parse(text)

# Print output
print("\noutput: ")
print(output)



