import re

text = """Election of Members of the Tamil Nadu Wakf Board from the Electoral College
consisting of ..............................................................

NOMINATION PAPER

I propose the name of Thiru....................................................................
as a candidate for election as a Member of the Tamil Nadu Wakf Board from the
electoral college consisting of............................................"""

blocks = re.split(r'\n\s*\n', text)

MAIN_Q = re.compile(r"^\s*(\d{1,2})[\.\)]\s*(.+)")
SUB_Q = re.compile(r"^\s*\(([a-z])\)\s*(.+)")

# Regex to find a chunk ending in colon or blanks
# It finds: Any text (non-greedy) followed by colon or blanks
CHUNK_BLANK = re.compile(r"(.*?)(?:\s*:|\s*_{3,}|\s*\.{3,})")

for block in blocks:
    s_block = block.replace("\n", " ").strip()
    
    # Can we find blanks in this block?
    # Because finditer will match consecutively
    matches = list(CHUNK_BLANK.finditer(s_block))
    
    if not matches:
        continue
        
    last_end = 0
    for m in matches:
        # The text before the blank
        raw_text = m.group(1).strip()
        
        # If it's the first match in the block, raw_text is the start of the block up to the blank.
        # This is EXACTLY the context we want!
        # E.g., "Election of Members of the Tamil Nadu Wakf Board from the Electoral College consisting of"
        
        # But wait! If we have multiple blanks in a block:
        # "Name: ....... Age: ......"
        # m1 group(1) = "Name"
        # m2 group(1) = "Age"
        print(f"Match extracted: '{raw_text}'")
        
