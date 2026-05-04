import glob

for f in glob.glob("examples/**/*.ucl", recursive=True):
    txt = open(f).read().strip()
    open(f, "w").write(txt + "\n")
