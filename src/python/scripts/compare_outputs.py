import sys
a=open(sys.argv[1]).read()
b=open(sys.argv[2]).read()
print("same" if a==b else "diff")
