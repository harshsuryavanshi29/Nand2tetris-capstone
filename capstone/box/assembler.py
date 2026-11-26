import sys, re

COMP = {
 '0':'0101010','1':'0111111','-1':'0111010','D':'0001100','A':'0110000',
 '!D':'0001101','!A':'0110001','-D':'0001111','-A':'0110011','D+1':'0011111',
 'A+1':'0110111','D-1':'0001110','A-1':'0110010','D+A':'0000010','D-A':'0010011',
 'A-D':'0000111','D&A':'0000000','D|A':'0010101',
 'M':'1110000','!M':'1110001','-M':'1110011','M+1':'1110111','M-1':'1110010',
 'D+M':'1000010','D-M':'1010011','M-D':'1000111','D&M':'1000000','D|M':'1010101'}
JUMP = {'':'000','JGT':'001','JEQ':'010','JGE':'011','JLT':'100','JNE':'101','JLE':'110','JMP':'111'}
PREDEF = {'SP':0,'LCL':1,'ARG':2,'THIS':3,'THAT':4,'SCREEN':16384,'KBD':24576}
PREDEF.update({f'R{i}': i for i in range(16)})
SYMBOL_RE = re.compile(r'^[A-Za-z_.$:][A-Za-z0-9_.$:]*$')

def dest_bits(d):
    if any(c not in 'ADM' for c in d) or len(set(d)) != len(d):
        raise ValueError(f'invalid destination "{d}"')
    return ('1' if 'A' in d else '0') + ('1' if 'D' in d else '0') + ('1' if 'M' in d else '0')

def assemble(path):
    symbols = dict(PREDEF)
    label_line = {}      # label -> line where it was first defined
    cmds = []            # (source line number, cleaned text)
    errors = 0

    # FIRST READING: strip comments/blanks, record labels
    for n, raw in enumerate(open(path), 1):
        line = raw.split('//')[0].replace(' ', '').replace('\t', '').strip()
        if not line:
            continue
        if line.startswith('('):
            if not (line.endswith(')') and SYMBOL_RE.match(line[1:-1])):
                print(f'Line {n}: invalid label'); errors += 1; continue
            name = line[1:-1]
            if name in label_line:   # EXTRA FEATURE (K mod 3 = 2)
                print(f'Warning: label "{name}" on line {n} was already defined on line {label_line[name]}')
                continue             # keep the first definition
            label_line[name] = n
            symbols[name] = len(cmds)   # address of the NEXT instruction
        else:
            cmds.append((n, line))

    # SECOND READING: translate to 16 bits
    out, next_var = [], 16
    for n, line in cmds:
        try:
            if line.startswith('@'):
                v = line[1:]
                if v.isdigit():
                    num = int(v)
                    if num > 32767: raise ValueError('number too large')
                elif SYMBOL_RE.match(v):
                    if v not in symbols:
                        symbols[v] = next_var; next_var += 1
                    num = symbols[v]
                else:
                    raise ValueError('invalid A-instruction')
                out.append(format(num, '016b'))
            else:
                dest, comp, jump = '', line, ''
                if '=' in comp: dest, comp = comp.split('=', 1)
                if ';' in comp: comp, jump = comp.split(';', 1)
                if comp not in COMP: raise ValueError('invalid instruction')
                if jump not in JUMP: raise ValueError('invalid jump')
                out.append('111' + COMP[comp] + dest_bits(dest) + JUMP[jump])
        except ValueError as e:
            errors += 1
            print(f'Error on line {n}: {e}')

    if errors:
        print(f'{errors} error(s). No output written.'); return
    base = path.rsplit('.', 1)[0]
    open(base + '.hack', 'w', newline='\n').write('\n'.join(out))
    print(f'Wrote {base}.hack ({len(out)} instructions)')

if __name__ == '__main__':
    assemble(sys.argv[1])