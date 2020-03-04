# SXG
SXG is the grammar analyzer used in Slex compiler

---
## Usage

```python
import sxg

grm = sxg.Grammar() # Instance the grammar

# Load grammar definitions
grm.load_def("def: 'ident'=IDENT")

# Try to get the definition("def") in the line
grm.parse_line("def", "identifier") # -> (True|False, {"ident": "identifier"})
```
