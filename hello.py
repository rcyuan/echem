import gamry_parser

f = '/Users/rachelyuan/src/echem/gamry-parser-master/EIS_090624_W94-CE_E2_PostPEDOT.DTA'
Z = gamry_parser.Impedance()
Z.load(f)

print(Z.curve())