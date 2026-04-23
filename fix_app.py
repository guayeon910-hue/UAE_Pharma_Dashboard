import re

path = 'frontend/static/app.js'
content = open(path, 'r', encoding='utf-8').read()
content = content.replace('_p2SarPerUsd', '_p2AedPerUsd')
content = content.replace('refSar', 'refAed')
content = content.replace('mnSar', 'mnAed')
open(path, 'w', encoding='utf-8').write(content)
print("Replaced variables in app.js")
