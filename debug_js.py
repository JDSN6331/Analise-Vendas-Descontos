"""Find the exact JS error by extracting and checking key sections."""
f = open('analytics/dashboard/dashboard.html', 'r', encoding='utf-8')
c = f.read()
f.close()

# Extract the full afterFit sections with surrounding context
for i, label in enumerate(['first (motivos)', 'second (grupo)']):
    start = 0 if i == 0 else c.find('afterFit', c.find('afterFit') + 10)
    if i == 0:
        start = c.find('afterFit')
    
    # Get 3 lines before and 3 after
    line_start = c.rfind('\n', 0, start)
    for _ in range(3):
        line_start = c.rfind('\n', 0, line_start)
    line_end = start
    for _ in range(5):
        line_end = c.find('\n', line_end + 1)
    
    print(f"=== afterFit {label} ===")
    snippet = c[line_start:line_end]
    for j, line in enumerate(snippet.split('\n')):
        print(f"  {j}: {line.rstrip()}")
    print()

# Check if the resize listener brackets are balanced
idx = c.find("window.addEventListener('resize'")
if idx >= 0:
    end = c.find(');', idx) + 2
    print("=== Resize listener ===")
    print(c[idx:end])
    opens = c[idx:end].count('{')
    closes = c[idx:end].count('}')
    print(f"Braces: {opens} open, {closes} close")
    
# Check overall script syntax by looking for common errors
# Sometimes f-string issues produce things like {0} or just empty {}
script_start = c.find('<script>') + 8
script_end = c.find('</script>')
js = c[script_start:script_end]

# Look for orphaned { } or empty {}
import re
empties = [(m.start(), m.group()) for m in re.finditer(r'\{\s*\}', js)]
if empties:
    print(f"\nEmpty braces found: {len(empties)}")
    for pos, match in empties[:5]:
        context_start = max(0, pos - 30)
        print(f"  at {pos}: ...{repr(js[context_start:pos+len(match)+10])}...")
