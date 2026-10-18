import json, re
s = open('src/src.html').read()
plan = json.dumps(json.load(open('src/plan.json')), separators=(',', ':')).replace('</', '<\\/')
s = s.replace('/*PLAN*/', plan).replace('/*SHARED*/', open('src/shared.js').read()).replace('/*MAIN*/', open('src/main.js').read())
open('index.html', 'w').write(s)
pass
print(len(s), 'bytes')
