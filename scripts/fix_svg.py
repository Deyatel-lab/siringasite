import re
from pathlib import Path

p = Path(__file__).resolve().parents[1] / "assets" / "logo_siringa.svg"
t = p.read_text(encoding="utf-8")
t = t.replace('fill="#1C1C1E"', 'fill="#000000"')
t = re.sub(r'aria-label="[^"]*"', 'aria-label="Сиринга"', t, count=1)
p.write_text(t, encoding="utf-8")
print("paths", t.count("<path"), "fills", t.count('fill="#000000"'))
