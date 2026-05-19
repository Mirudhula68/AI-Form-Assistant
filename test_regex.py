import re

lines = [
    "1. (a) Name of the worker",
    "(b) Sex [ M ] [ F ] [ TG ]",
    "(c) Religion",
    "2. Name of the Father/Husband :",
    "Date of issue .................",
    "Department: ____________",
    "Age:",
    "noisy line do not match",
    "some text with no colon or dots"
]

MAIN_Q = re.compile(r"^\s*(\d{1,2})[\.\)]\s*(.+)")
SUB_Q = re.compile(r"^\s*\(([a-z])\)\s*(.+)")
COLON_BLANK_Q = re.compile(r"^([^:]+?)(?:\s*:|\s*_{3,}|\s*\.{3,})")

for line in lines:
    print(f"--- Line: {line}")
    m = MAIN_Q.match(line)
    if m:
        print("   MAIN:", m.groups())
    
    s = SUB_Q.match(line)
    if s:
        print("   SUB:", s.groups())
        
    c = COLON_BLANK_Q.search(line)
    if c:
        qtext = c.group(1).strip()
        # strip leading numbers/letters from qtext since main/sub handles them?
        # actually, if we use COLON as fallback:
        # wait, if COLON_BLANK_Q uses .search instead of .match, it might find it anywhere.
        print("   COLON/BLANK:", qtext)
