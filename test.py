from grammar import Grammar

def main():
	grm = Grammar()

	grm.load_def("assign: 'n'=IDENT 'next'=(',' 'n'=IDENT)")

	data = {}
	grm.set_line("a,")
	print grm.parse('assign', data), data

main()
