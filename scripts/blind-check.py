#!/usr/bin/env python3
# Strips lens names and author phrases from one Owl position, in place.
# Prints how many it found. ego-resolve Step 4 runs it on each position.
# The patterns are fixed: do not edit them for a run.
import re, sys
p = sys.argv[1]
leak = re.compile(r"\begm-[a-z0-9-]+|\b(goldfish|elephant|my draft|as the author|the reviewers?)\b", re.I)
text = open(p).read()
n = len(leak.findall(text))
open(p, "w").write(re.sub(r"[ \t]{2,}", " ", leak.sub("", text)))
print(n)
