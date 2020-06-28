"""
    Implementation of modular adder from arXiv:1611.07995v2 of figure 5
"""

import cirq
import numpy as np

from mathematics.shor1611 import ShorCarryGate, ShorRecursiveAdder
from mathematics.shor1611.shor_incrementer import ShorIncrementer
from mathematics.shor1611.shor_sign_gate import ShorSignGate


class ShorModularAdder():
    def __init__(self, value_of_b, hardwired_constant, N, sum_register, garbage,
                 carry):
        """
        :param sum_register: the quantum register holding the integer
        :param garbage: dirty ancillae
        :param carry: qubit controlling whether to add a or a-N
        :param hardwired_constant: constant to be added to b
        :param value_of_b: value of b
        :param N:
        """
        # x is the intger value that the register b is holding
        # We need it because we're going to simulate the circuit later
        self.value_of_b = value_of_b

        self.sum_register, self.g, self.carry, self.constant, self.N = sum_register, garbage, carry, hardwired_constant, N

    def construct_circuit(self):
        N_minus_a = self.N - self.constant

        """
            CMP(N-a) is the first part of the circuit
            The first part is for inverting b to -b which not(b) + 1
            This is not described in the paper
        """
        moments = []
        moments += self.to_two_complement(self.sum_register, self.g)

        # Running the comparator using the carry gate
        moments += ShorCarryGate(self.sum_register,  # two's complement of B
                                 N_minus_a,     #
                                 self.g[:-1],   # a single garbage bit is needed
                                 self.carry     # the carry will indicate the
                                                # sign of the result
                                 ).construct_circuit().moments
        #
        # Returning b to its original value
        moments += self.from_two_complement(self.sum_register, self.g)

        """
        - For b=0 after running the comparator the carry bit will be 0
            => the circuit subtracting N-a will be executed
            ==> result = 0+a-N=a-N

        - For b = N-a after running the comparator the carry bit = 1
            => the circuit adding a will be run
            ==> result = b+a= N-a+a=N
        """

        """
            ADD(a) or SUB(N-a)
        """
        # Adding a or subtracting N-a depending on the result of the comparison
        # True=|1> for adding a
        moments += ShorRecursiveAdder(
            A_reg = self.sum_register,
            hardwired_constant = self.constant,
            garbage = self.g[1],
            control = [self.carry]).construct_controlled_circuit(True)

        # False=|0> for subtracting N-a
        # Run the circuit in reverse. The reverse of addition is substraction
        moments += ShorRecursiveAdder(
            A_reg = self.sum_register,
            hardwired_constant = N_minus_a,
            garbage = self.g[1],
            control = [self.carry]).construct_controlled_circuit(False)[::-1]

        """
            CMP(a)
        """
        # Supposedly resetting the carry qubit to 0
        moments += self.to_two_complement(self.sum_register, self.g)

        moments += ShorCarryGate(self.sum_register,  # two's complement of B
                                 # which contains (a+b)%N
                                 self.constant,  # a
                                 self.g[:-1],  # a single garbage bit is needed
                                 self.carry  # the carry will be uncomputed
                                 ).construct_circuit().moments

        moments += self.from_two_complement(self.sum_register, self.g)



        # circuit = cirq.Circuit(moments)
        #
        # # We need to run the circuit to determine if the value of carry is 0 or 1
        # # In the latter case we apply a NOT gate on the carry qubit
        #
        # simulator = cirq.Simulator()
        # qubits = sorted(list(circuit.all_qubits()))[::-1]
        # initial_state = [0] * 2 ** (len(qubits))
        #
        # # Preparing the register b with the value x
        # initial_state[self.x] = 1
        # initial_state = np.array(initial_state, dtype=np.complex64)
        #
        # # Measuring the value of carry
        # circuit.append(cirq.measure(self.carry))
        # result = simulator.simulate(circuit, qubit_order=qubits,
        #                             initial_state=initial_state)
        #
        # if np.array_equal(result.measurements['x'], np.array([1])):
        #     # In case carry == 1 then apply a NOT gate
        #     circuit.append(cirq.Moment([cirq.X(self.carry)]))
        #
        #     # Final result
        #     result = simulator.simulate(circuit, qubit_order=qubits,
        #                                 initial_state=initial_state)

        circuit = cirq.Circuit(moments)
        circuit.append(cirq.measure(self.carry))

        return circuit
            # , result


    def from_two_complement(self, register, garbage):

        return self.to_two_complement(register, garbage)[::-1]


    def to_two_complement(self, register, garbage):
        ret_moments = []
        ret_moments += [cirq.X(i) for i in register]
        ret_moments += ShorIncrementer(register,
                                   garbage).construct_unctrolled_circuit().moments
        return ret_moments

    """
        Controlled modular adder
    """

    def construct_controlled_circuit(self, control):
        """

        :param control: Control Quubit
        :return:
        """
        # Two's complement of a
        bin_complement = self.N - self.constant

        # The first part is for inverting b to -b which not(b) + 1
        # This is not described in the paper
        # Please double check
        moments = [cirq.X(i) for i in self.sum_register]
        # moments += ShorIncrementer(self.b, self.g).construct_unctrolled_circuit().moments
        moments += ShorIncrementer(self.sum_register, self.g, control=control).construct_circuit()

        # Running the comparator using the carry gate
        # moments += ShorCarryGate(self.b, bin_complement, self.g[:-1], self.carry) \
        #     .construct_circuit().moments
        moments += ShorCarryGate(self.sum_register, bin_complement, self.g[::-1], self.carry,
                                 control=control).construct_controlled_circuit(True).moments

        # Returning b to its original value
        #moments += ShorIncrementer(self.b, self.g).construct_unctrolled_circuit().moments[::-1]
        moments += ShorIncrementer(self.sum_register, self.g, control=control).construct_circuit().moments[::-1]
        moments += [cirq.X(i) for i in self.sum_register]

        # Adding a or subtracting N-a depending on the result of the comparison
        # 1 for adding a
        moments += ShorRecursiveAdder(self.sum_register, self.constant, self.g[1], self.carry) \
            .construct_controlled_circuit(True)
        # 0 for subtracting N-a
        moments += ShorRecursiveAdder(self.sum_register, bin_complement, self.g[1],
                                      self.carry) \
                       .construct_controlled_circuit(False)[::-1]

        circuit = cirq.Circuit(moments)

        # We need to run the circuit to determine if the value of carry is 0 or 1
        # In the latter case we apply a NOT gate on the carry qubit

        simulator = cirq.Simulator()
        qubits = sorted(list(circuit.all_qubits()))[::-1]
        initial_state = [0] * 2 ** (len(qubits))

        # Preparing the register b with the value x
        initial_state[self.value_of_b] = 1
        initial_state = np.array(initial_state, dtype=np.complex64)

        # Measuring the value of carry
        circuit.append(cirq.measure(self.carry))
        result = simulator.simulate(circuit, qubit_order=qubits,
                                    initial_state=initial_state)

        if np.array_equal(result.measurements['x'], np.array([1])):
            # In case carry == 1 then apply a NOT gate
            circuit.append(cirq.Moment([cirq.X(self.carry)]))

            # Final result
            result = simulator.simulate(circuit, qubit_order=qubits,
                                        initial_state=initial_state)

        #######################################################################
        # Supposedly resetting the carry qubit to 0
        # moments += [cirq.X(i) for i in self.b]
        # moments += ShorIncrementer(self.b, self.g).construct_unctrolled_circuit().moments
        # moments += ShorCarryGate(self.b, self.a, self.g[:-1], self.carry) \
        #     .construct_circuit().moments
        # moments += ShorIncrementer(self.b, self.g).construct_unctrolled_circuit().moments[::-1]
        # moments += [cirq.X(i) for i in self.b]
        #########################################################################

        return circuit, result


    """
        Modular adder with the sign gate  
    """
    def construct_circuit_with_sign_gate(self):
        # Two's complement of a
        bin_complement = self.N - self.constant

        # The first part is for inverting b to -b which not(b) + 1
        # This is not described in the paper
        # Please double check
        moments = [cirq.X(i) for i in self.sum_register]
        moments += ShorIncrementer(self.sum_register, self.g).construct_unctrolled_circuit().moments

        # Running the comparator using the carry gate
        moments += ShorSignGate(self.sum_register, bin_complement, self.g[:-2]) \
            .construct_circuit().moments


        circuit = cirq.Circuit(moments)
        simulator = cirq.Simulator()
        qubits = sorted(list(circuit.all_qubits()))[::-1]
        initial_state = [0] * 2 ** (len(qubits))

        # Preparing the register b with the value x
        initial_state[self.value_of_b] = 1
        initial_state = np.array(initial_state, dtype=np.complex64)

        # Measuring the value of carry
        circuit.append(cirq.measure(self.sum_register[-1]))
        result = simulator.simulate(circuit, qubit_order=qubits,
                                    initial_state=initial_state)
        print(result)

        # The sign bit is the most significant bit of b
        # 1 for adding a
        if np.array_equal(result.measurements[self.sum_register[-1].name], np.array([0])):
            # Returning b to its original value
            moments += [cirq.X(self.sum_register[-1])]
            moments += ShorIncrementer(self.sum_register, self.g).construct_unctrolled_circuit().moments[::-1]
            moments += [cirq.X(i) for i in self.sum_register]
            moments += ShorRecursiveAdder(self.sum_register, self.constant, self.g[1]) \
                .construct_circuit().moments

        else:
            # 0 for substracting N-a
            # Returning b to its original value
            moments += ShorIncrementer(self.sum_register, self.g).construct_unctrolled_circuit().moments[::-1]
            moments += [cirq.X(i) for i in self.sum_register]
            moments += ShorRecursiveAdder(self.sum_register, bin_complement, self.g[1]) \
                           .construct_circuit()[::-1]

        circuit = cirq.Circuit(moments)


        # Simulation of circuit (Optional)
        simulator = cirq.Simulator()
        qubits = sorted(list(circuit.all_qubits()))[::-1]
        initial_state = [0] * 2 ** (len(qubits))

        # Preparing the register b with the value x
        initial_state[self.value_of_b] = 1
        initial_state = np.array(initial_state, dtype=np.complex64)

        # Measuring the value of carry
        circuit.append(cirq.measure(self.sum_register[-1]))
        result = simulator.simulate(circuit, qubit_order=qubits,
                                    initial_state=initial_state)
        print(result.measurements)

        return circuit, result