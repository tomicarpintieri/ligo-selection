import json,pathlib,re
ROOT=pathlib.Path(__file__).resolve().parents[1]
text=(ROOT/'page'/'template.html').read_text(encoding='utf8'); values=json.loads((ROOT/'results.json').read_text())
for key,value in values.items(): text=text.replace(f'__{key}__',f'{value:.5g}' if isinstance(value,float) else str(value))
assert not re.search(r'__[A-Z_a-z0-9]+__',text)
(ROOT/'page'/'index.html').write_text(text,encoding='utf8')
