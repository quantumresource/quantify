import cirq

import optimizers as qopt
import mathematics
import mathematics.draper0406142 as drp
from qramcircuits.toffoli_decomposition import *


def main():

    print("Hello Mathematics circuits!")

    decompositions = [
        ToffoliDecompType.NO_DECOMP,
        ToffoliDecompType.NO_DECOMP,
        ToffoliDecompType.NO_DECOMP,
        ToffoliDecompType.NO_DECOMP
    ]

    n = 10
    A = [cirq.NamedQubit(f"{i}_A") for i in range(n)]
    B = [cirq.NamedQubit(f"{i}_B") for i in range(n)]

    adder = drp.CarryLookaheadAdder(A, B, decompositions)

    print(adder.circuit)

if __name__ == "__main__":
    main()