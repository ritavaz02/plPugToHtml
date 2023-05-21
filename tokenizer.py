import json
import sys
from lexer import lexer
from yacc import parser

# Read file with pug code
with open(sys.argv[1], 'r') as myfile:
    text = myfile.read()

# Read dictionary from json file with interpolations
with open(sys.argv[2], 'r') as myfile:
    interpolation = json.load(myfile)


# Give the lexer some input
lexer.input(text)

# Set the interpolation dictionary in the parser
parser.interpolation = interpolation

# Tokenize
parser.success = True
output = parser.parse(text)

# print output to file "result.html"
with open("result.html", "w") as f:
    f.write(output)

# Print output to console
print(output)