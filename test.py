from grammar import Grammar

def main():
    grm = Grammar()
    
    grm.load_def("dotted_name: 'name'=IDENT 'list'=*('.' 'name'=IDENT)") # a.b.c
    grm.load_def("assign: 'name_a'=dotted_name '=' 'name_b'=dotted_name") # a.b.c
    
    data = {}
    grm.set_line("a.b.c")
    print grm.parse('dotted_name', data), data
    # output: True {'name': 'a', 'list': [{'name': b}, {'name': c}]}
    
    print grm.parse_line("a.b = b.c", 'assign')
    # output: (True, {'name_b': {'list': [{'name': 'c'}], 'name': 'b'}, 'name_a': {'list': [{'name': 'b'}], 'name': 'a'}})

main()