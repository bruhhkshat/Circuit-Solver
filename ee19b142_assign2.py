from numpy import *
from sys import argv, exit


# A function created to converted exponents to real numbers.


# Classes are declared for each component.
class Resistor:
    def __init__(self, name, n1, n2, value):
        self.name = name
        self.n1 = n2
        self.n2 = n1
        self.value = value


class Capacitor:
    def __init__(self, name, n1, n2, value):
        self.name = name
        self.n1 = n2
        self.n2 = n1
        self.value = value


class Inductor:
    def __init__(self, name, n1, n2, value):
        self.name = name
        self.n1 = n2
        self.n2 = n1
        self.value = value




class CurrentSource:
    def __init__(self, name, n1, n2, value):
        self.name = name
        self.n1 = n2
        self.n2 = n1
        self.value = value


class VoltageSource:
    def __init__(self, name, n1, n2, value):
        self.name = name
        self.n1 = n2
        self.n2 = n1
        self.value = value


# The program will throw in an error if there isn't exactly 2 arguments in the commandline.
#if len(argv) != 2:
 #   print("Please provide the correct 2 arguments in the commandline.")
  #  exit()

# Assigning constants variables to .circuit and .end
CIRCUIT = ".circuit"
END = ".end"
AC = ".ac"

try:

    # Opening the file mentioned in the commandline.
    with open(argv[1]) as f:
        lines = f.readlines()

        # These are parameters to check the errors in the file format.
        start = -1;
        checkstart = -1;
        end = -2;
        checkend = -1;
        ac = -1;
        checkac = -1

        # The program will traverse through the file and take out only the required part.
        for line in lines:
            if CIRCUIT == line[:len(CIRCUIT)]:
                start = lines.index(line)
                checkstart = 0

            elif END == line[:len(END)]:
                end = lines.index(line)
                checkend = 0
            # This part is to check if the circuit has an AC or a DC source.
            elif AC == line[:len(AC)]:
                ac = lines.index(line)
                checkac = 1

        # The program will throw in an error if the circuit definition format is not proper.
        if start >= end or checkstart == -1 or checkend == -1:
            print("Invalid circuit definition.")
            exit()

        # Creating a list and storing the necessary information into it.
        l = [];
        k = 0
        # For AC circuit, the required information is collected.
        try:
            if checkac == 1:
                _, ac_name, frequency = lines[ac].split("#")[0].split()
                frequency = 2 * 3.1415926 * float(frequency)

            for line in (lines[start + 1:end]):
                name, n1, n2, *value = line.split("#")[0].split()

                if name[0] == 'R':
                    item = Resistor(name, n1, n2, value)

                elif name[0] == 'C':
                    item = Capacitor(name, n1, n2, value)

                elif name[0] == 'L':
                    item = Inductor(name, n1, n2, value)

                elif name[0] == 'V':
                    item = VoltageSource(name, n1, n2, value)
                    k = k + 1

                elif name[0] == 'I':
                    item = CurrentSource(name, n1, n2, value)

                # Converting the values of the components into real numbers by using the converter() function.
                if len(item.value) == 1:
                    if item.value[0].isdigit() == 0:
                        item.value = float(float(item.value[0]))
                    else:
                        item.value = float(item.value[0])

                # In case of an AC source, the voltage and phase are assigned properly.
                else:
                    item.value = (float(item.value[1]) / 2) * complex(cos(float(item.value[2])),
                                                                          sin(float(item.value[2])))

                l.append(item)

        # The program will throw an error if the netlist is not written properly.
        except IndexError:
            print("Please make sure the netlist is written properly.")
            exit()

    # Nodes are creating using a dictionary.
    node = {}
    for item in l:
        if item.n1 not in node:
            if item.n1 == 'GND':
                node['n0'] = 'GND'

            else:
                name = "n" + item.n1
                node[name] = int(item.n1)

        if item.n2 not in node:
            if item.n2 == 'GND':
                node['n0'] = 'GND'

            else:
                name = "n" + item.n2
                node[name] = int(item.n2)

    node['n0'] = 0
    n = len(node)

    # Creating the M and b matrices for solving the equations.
    M = zeros(((n + k - 1), (n + k - 1)), dtype="complex_")
    b = zeros(((n + k - 1), 1), dtype="complex_")
    p = 0

    # This part of code will fill the matrices M and b taking into consideration if it is an AC or a DC source.
    for item in l:

        # In case of a resistor, the matrix M is filled in a certain way as shown below.
        if item.name[0] == 'R':
            if item.n2 == 'GND':
                M[int(item.n1) - 1][int(item.n1) - 1] += 1 / item.value

            elif item.n1 == 'GND':
                M[int(item.n2) - 1][int(item.n2) - 1] += 1 / item.value

            else:
                M[int(item.n1) - 1][int(item.n1) - 1] += 1 / item.value
                M[int(item.n2) - 1][int(item.n2) - 1] += 1 / item.value
                M[int(item.n1) - 1][int(item.n2) - 1] += -1 / item.value
                M[int(item.n2) - 1][int(item.n1) - 1] += -1 / item.value

        # In case of a capacitor, the impedance is calculated first and then the matrix M is filled.
        elif item.name[0] == 'C':
            if checkac == 1:
                Xc = -1 / (float(item.value) * frequency)
                item.value = complex(0, Xc)

            if item.n2 == 'GND':
                M[int(item.n1) - 1][int(item.n1) - 1] += 1 / item.value
            elif item.n1 == 'GND':
                M[int(item.n2) - 1][int(item.n2) - 1] += 1 / item.value

            else:
                M[int(item.n1) - 1][int(item.n1) - 1] += 1 / item.value
                M[int(item.n2) - 1][int(item.n2) - 1] += 1 / item.value
                M[int(item.n1) - 1][int(item.n2) - 1] += -1 / item.value
                M[int(item.n2) - 1][int(item.n1) - 1] += -1 / item.value

        # In case of an inductor, the impedance is calculated first and then the matrix M is filled.
        elif item.name[0] == 'L':
            if checkac == 1:
                Xl = (float(item.value) * frequency)
                item.value = complex(0, Xl)

            if item.n2 == 'GND':
                M[int(item.n1) - 1][int(item.n1) - 1] += 1 / item.value
            elif item.n1 == 'GND':
                M[int(item.n2) - 1][int(item.n2) - 1] += 1 / item.value

            else:
                M[int(item.n1) - 1][int(item.n1) - 1] += 1 / item.value
                M[int(item.n2) - 1][int(item.n2) - 1] += 1 / item.value
                M[int(item.n1) - 1][int(item.n2) - 1] += -1 / item.value
                M[int(item.n2) - 1][int(item.n1) - 1] += -1 / item.value

        # In case of a current source, the matrix b is filled as shown.
        elif item.name[0] == 'I':
            if item.n2 == 'GND':
                b[int(item.n1) - 1][0] += item.value

            elif item.n1 == 'GND':
                b[int(item.n2) - 1][0] += -item.value

            else:
                b[int(item.n1) - 1][0] += item.value
                b[int(item.n2) - 1][0] += -item.value

        # In case of a voltage source, the matrices M and b are filled as shown.
        elif item.name[0] == 'V':
            if item.n2 == 'GND':
                M[int(item.n1) - 1][n - 1 + p] += 1
                M[n - 1 + p][int(item.n1) - 1] += 1
                b[n - 1 + p] += item.value
                p = p + 1
            elif item.n1 == 'GND':
                M[int(item.n2) - 1][n - 1 + p] += -1
                M[n - 1 + p][int(item.n2) - 1] += -1
                b[n - 1 + p] += item.value
                p = p + 1
            else:
                M[int(item.n1) - 1][n - 1 + p] += 1
                M[int(item.n2) - 1][n - 1 + p] += -1
                M[n - 1 + p][int(item.n1) - 1] += 1
                M[n - 1 + p][int(item.n2) - 1] += -1
                b[n - 1 + p] += item.value
                p = p + 1

    # The linalg.solve() function is used to solve the circuit equations.
    V = linalg.solve(M, b)

    print(V, "\n")

    for i in range(n - 1):
        print("V", i + 1, "=", V[i], "\n")
    for j in range(k):
        print("I", j + 1, "=", V[j + n - 1], "\n")

# The program will throw in this error if the name of the netlist file is not proper
# or if the netlist file is not found in the same directory as the program.

except FileNotFoundError:
    print("Invalid File.")
    exit()