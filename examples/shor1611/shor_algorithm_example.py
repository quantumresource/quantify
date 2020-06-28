import cirq

from mathematics.shor1611.shor_algorithm import ShorAlgorithm


def example():
    # Input register that will be initialized with | 1 >
    a = [cirq.NamedQubit("a" + str(i)) for i in range(4)]

    # Input register initialized with | 0 >
    b = [cirq.NamedQubit("b" + str(i)) for i in range(4)]

    # The controlling qubit
    control = [cirq.NamedQubit("zxcontrol")]

    # Qubit used for the addition
    zero_qubit = cirq.NamedQubit("zero_qubit")

    hardwired_constant = 6

    N = 7
    circuit, measurment, result = ShorAlgorithm(N=N, ancillae=b, control=control, exponentiation_result=a,
                                harwired_constant=hardwired_constant,
                                zero_qubit=zero_qubit).construct_circuit()
    print(result)
    print(measurment)

def __main__():
    example()


if __name__ == "__main__":
    __main__()
