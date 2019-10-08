from grammar import Grammar

def main():
    grm = Grammar()
    
    grm.load_def("assign: 'test'=['a' 'b' 'c'] 'name'=IDENT")
    
    print grm.parse_line("a Hola", 'assign')

main()
