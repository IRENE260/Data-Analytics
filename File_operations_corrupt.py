def f9(inFile, outFile):
    r = open(inFile, 'r')
    w = open(outFile, 'w')

    for line in r:
        line = line.strip()
        if line == '':
            continue

        parts = line.split(':')
        if len(parts) != 2:
            w.write(f"corrupt:{line}\n")
            continue

        factors_part = parts[0]
        multiples_part = parts[1]

        factors_list = factors_part.split()
        multiples_list = multiples_part.split()

        try:
            factors = [int(x) for x in factors_list]
            multiples = [int(x) for x in multiples_list]
        except ValueError:
            w.write(f"corrupt:{line}\n")
            continue

        total = 0
        for num in multiples:
            for fact in factors:
                if num % fact == 0:
                    total += num
                    break

        w.write(f"{total}:{factors_part}:{multiples_part}\n")

    r.close()
    w.close()

with open('input', 'w') as f:
    f.write('3 5:1 2 3 4 5 6 7 8 9\n2 3 hello:1 2 3 4 5 6 7 8\n3 5:')
    for i in range(1000):
        f.write(str(i) + ' ')
    f.write('\n2 3 5:1 2 3 4 5 6 7 8 9\n2 3 5 97')

f9('input', 'output')

with open('output', 'r') as f:
    print(f.read())
