import cirq

from optimizers import LookAheadAnalysis

def main():
    a = cirq.NamedQubit('a')
    b = cirq.NamedQubit('b')
    c = cirq.NamedQubit('c')
    d = cirq.NamedQubit('d')
    e = cirq.NamedQubit('e')
    f = cirq.NamedQubit('f')

    m=cirq.T(a)
    circuit=cirq.Circuit()

    circuit.append(cirq.TOFFOLI(a,b,c))
    circuit.append(cirq.TOFFOLI(d,e,f))
    circuit.append(cirq.TOFFOLI(a,e,d))
    circuit.append(cirq.TOFFOLI(d,e,f))
    circuit.append(cirq.TOFFOLI(a,c,d))
    circuit.append(cirq.TOFFOLI(a,c,d))

    print(circuit)
    print(len(circuit))

    look = LookAheadAnalysis()
    analysis = look.lookahead(circuit, 3, LookAheadAnalysis.find_parallel_Toffolis)

    print(analysis)


if __name__ == "__main__":
    main()
