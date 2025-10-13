##Create a function which:
#  has inFile and outFile as parameters (filenames as strings, not filehandles or lists)
#  each line of the input file contains factors, space separated
#  followed by ':'
#  followed by multiples, space separated
#  the output file should prepend each line of the input file with the result of
#  summing the multiples of the factors.
#  followed by ':'

def f7(inFile, outFile):
    f = open(inFile, 'r')
    r = open(outFile, 'w')
    for line in f:
        line = line.strip()
        if line == '':
          continue

        parts = line.split(':')
        factors_part = parts[0]
        multiples_part = ''
        if len(parts) > 1:
            multiples_part = parts[1]

        factors_list = factors_part.split()
        multiples_list = multiples_part.split()

        factors = []
        for x in factors_list:
            factors.append(int(x))

        multiples = []
        for x in multiples_list:
            multiples.append(int(x))
        total = 0
        for z in multiples:
            for a in factors:
                if z % a == 0:
                    total =total+ z
                    break
        r.write(f"{total}:{factors_part}:{multiples_part}\n")

    f.close()
    r.close()

with open('input','w') as f:
  f.write('3 5:1 2 3 4 5 6 7 8 9\n3 5:')
  for i in range(1000):
    f.write(str(i)+' ')
  f.write('\n2 3 5:1 2 3 4 5 6 7 8 9')

f7('input','output')

with open('sampleoutput','w') as f:
  f.write('23:3 5:1 2 3 4 5 6 7 8 9\n233168:3 5:')
  for i in range(1000):
    f.write(str(i)+' ')
  f.write('\n37:2 3 5:1 2 3 4 5 6 7 8 9')

y=open('output', 'r')
print(y.read())
