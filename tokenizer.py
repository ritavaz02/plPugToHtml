import json
import sys
from lexer import lexer
from yacc import parser

# if command is python3 tokenizer.py --help print help
if len(sys.argv) < 2 or (len(sys.argv) == 2 and sys.argv[1] == '--help'):
    print("Usage: python3 tokenizer.py <file.pug> <interpolation.json>")
    exit(1)

# Read file with pug code if exists
try:
    with open(sys.argv[1], 'r') as myfile:
        text = myfile.read()
except FileNotFoundError:
    print("File not found.")
    exit(1)

# Give the lexer some input
lexer.input(text)

# Read dictionary from json file with interpolations if file exists
if len(sys.argv) > 2:
    with open(sys.argv[2], 'r') as myfile:
        interpolation = json.load(myfile)

    # Set the interpolation dictionary in the parser
    parser.interpolation = interpolation

# Tokenize
parser.success = True
output = parser.parse(text)

# get the name of the file without the extension
name = sys.argv[1].split('.')[0]

# if the name contains a folder, get only the name of the file
if '/' in name:
    name = name.split('/')[-1]

# print output to file "result.html" to the folder "output"
with open("output/" + name + ".html", "w") as f:
    f.write(output)

# Print output to console
print(output)