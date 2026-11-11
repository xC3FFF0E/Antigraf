import io
import glob
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

# The pages carry two kinds of number that must never be guessed at again:
#   the count of tools -> taken from the folder
#   the version of Python -> a fact, never touched by a refresh
# This is the check a person would run, written down so it runs every time.

problems = []

def rows(text):
    tools = [l for l in text.splitlines() if "skills/antigraf/scripts" in l and "Python" in l]
    version = [l for l in text.splitlines() if "Where it runs" in l or "動く場所" in l
               or "실행 위치" in l or "Dónde corre" in l or "Où il tourne" in l
               or "Onde roda" in l or "Chạy ở đâu" in l or "執行環境" in l or "运行环境" in l]
    return (tools[0] if tools else ""), (version[0] if version else "")

for p in sorted(glob.glob("README*.md")):
    text = io.open(p, encoding="utf-8-sig").read()
    tool_row, version_row = rows(text)
    if "49" not in tool_row:
        problems.append((p, "tools row does not say 49", tool_row.strip()[:80]))
    if "41" not in tool_row:
        problems.append((p, "tools row lost the Python count", tool_row.strip()[:80]))
    if "47" in tool_row or "48" in tool_row:
        problems.append((p, "tools row still has an old count", tool_row.strip()[:80]))
    # Japanese, Korean and both Chinese pages count Python tools as "Python 40",
    # which is a count and not a version, so the tools row is read out first.
    prose = "\n".join(l for l in text.splitlines() if l != tool_row)
    for bad in ("Python 40", "Python 40.8", "Python 400"):
        if bad in prose:
            problems.append((p, "version damaged: " + bad, version_row.strip()[:80]))
    if text.count("Python 3.8") < 2:
        problems.append((p, "install section lost Python 3.8", version_row.strip()[:80]))

print("problems:", len(problems))
for row in problems:
    print(" ", row[0], "|", row[1], "|", row[2])
sys.exit(1 if problems else 0)
