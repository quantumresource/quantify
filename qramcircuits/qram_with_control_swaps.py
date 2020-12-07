import cirq
from utils import *

class QramWithControlSwaps:
    def __init__(self, qubits, target):
        """
        :param n: address size
        """
        self.qubits = qubits
        self.target = target
        self.memory = [cirq.NamedQubit("m" + str(i)) for i in range(2 ** len(qubits))]

    def controlled_swap_multiple_target(self, control, targets, decomposition_type):
        """
        :param control: control qubit
        :param targets: target qubits
        :return:
        """
        index = len(targets) // 2
        print(index)
        swap_moments = []
        swap_moments += [cirq.TOFFOLI(control, targets[i], targets[index + i]) for i in range(index)]

        swap_moments += [cirq.TOFFOLI(control, targets[index+i], targets[i]) for i in range(index)]

        swap_moments += [cirq.TOFFOLI(control, targets[i], targets[index + i]) for i in range(index)]

        return swap_moments

    def construct_circuit(self, decomposition_type=MPMCTDecompType.NO_DECOMP):
        n = len(self.qubits)
        moments = []
        for i in range(n):
            moments += self.controlled_swap_multiple_target(control=self.qubits[i],
                                                            targets=self.memory[:2 ** (n - i)],
                                                            decomposition_type=decomposition_type)

        # swapping m_0 with target
        final_swap = [cirq.CNOT(self.memory[0], self.target)]
        final_swap += [cirq.CNOT(self.target, self.memory[0])]
        final_swap += [cirq.CNOT(self.memory[0], self.target)]

        circuit = cirq.Circuit()
        # First third of the circuit
        circuit.append(moments)

        # Final swap
        circuit.append(final_swap)

        # Undoing the swaps
        circuit.append(moments[::-1])
        return circuit
