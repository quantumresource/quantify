"""
    Implementation of Carry gate from Fig.3 in arXiv:1611.07995v2
"""

import cirq


class ShorCarryGate:
    def __init__(self, a, c, g, ancilla, control=None):
        """

        :param a: quantum register
        :param c: classical constant
        :param g: dirty ancillae
        :param ancilla: the ancilla wich will carry the result
        :param control: control qubit
        """
        self.a, self.constant, self.g, self.ancilla, self.control = a, c, g, ancilla, control

    def construct_circuit(self):
        n = len(self.a)
        b = bin(self.constant)[2:].zfill(n)[::-1]
        circuit = cirq.Circuit()

        # Particular cases (Not defined in the paper)
        # Please double check it
        if len(self.a) == 1:
            if b[0] == '1':
                circuit.append(cirq.CNOT(self.a[0], self.ancilla))
            return circuit
        elif len(self.a) == 2:
            if b[1] == '1':
                circuit.append(cirq.CNOT(self.a[1], self.ancilla))
                circuit.append(cirq.X(self.a[1]))
            if b[0] == '1':
                circuit.append(cirq.TOFFOLI(self.a[0], self.a[1], self.ancilla))
            if b[1] == '1':
                circuit.append(cirq.X(self.a[1]))
            return circuit

        # General case
        # first moment applied on the result qubit
        moment_1 = [cirq.CNOT(self.g[-1], self.ancilla)]

        # If the least significant bit is a 0 then do nothing otherwise place a Toffoli
        if b[0] == '1':

            # Hold the first part of the circuit with the eventual X and CNOTs
            moments_2 = [cirq.TOFFOLI(self.a[0], self.a[1], self.g[0])]
        else:
            moments_2 = []

        # Holds only the Toffoli part
        moments_3 = []

        # Refer to the paper for the methodology
        if b[1] == '1':
            moments_2 += [cirq.X(self.a[1]), cirq.CNOT(self.a[1], self.g[0])]
        for i in range(2, n):
            moments_2 += [cirq.TOFFOLI(self.g[i - 2], self.a[i], self.g[i - 1])]
            moments_3 += [cirq.TOFFOLI(self.g[i - 2], self.a[i], self.g[i - 1])]
            if b[i] == '1':
                moments_2 += [cirq.X(self.a[i]), cirq.CNOT(self.a[i], self.g[i - 1])]

        # First moment
        circuit.append(moment_1)

        # Second set of moments
        circuit.append(moments_2[::-1])

        # Tird set of moments (Toffolis)
        circuit.append(moments_3)

        circuit.append(moment_1)

        # For reversibility
        circuit.append(moments_3[::-1])
        circuit.append(moments_2)

        #
        # if (len(b) > n):
        #     if b[n] == '1':
        #         circuit.append(cirq.Moment([cirq.X(self.ancilla)]))

        return circuit

    """
        Controlled version of construct circuit
    """

    def construct_controlled_circuit(self, choice):

        # # The choice parameter will serve to choose between adding c or N-c
        # n = len(self.a)
        # b = bin(self.constant)[2:].zfill(n)[::-1]
        # circuit = cirq.Circuit()
        #
        # # Particular cases (Not defined in the paper)
        # # Please double check them
        # if len(self.a) == 1:
        #     if b[0] == '1':
        #         if choice:
        #             circuit.append(cirq.TOFFOLI(self.control, self.a[0], self.ancilla))
        #         else:
        #             circuit.append(cirq.ControlledOperation([self.control, self.a[0]],
        #                                                     cirq.X(self.ancilla), control_values=[0, 1]))
        #     return circuit
        # elif len(self.a) == 2:
        #     if b[1] == '1':
        #         if choice:
        #             circuit.append(cirq.TOFFOLI(self.control, self.a[1], self.ancilla))
        #             circuit.append(cirq.CNOT(self.control, self.a[1]))
        #         else:
        #             circuit.append(cirq.ControlledOperation([self.control, self.a[1]],
        #                                                     cirq.X(self.ancilla), control_values=[0, 1]))
        #             circuit.append(cirq.ControlledOperation([self.control], cirq.X(self.a[1]), control_values=[0]))
        #     if b[0] == '1':
        #         if choice:
        #             circuit.append(cirq.ControlledOperation([self.control, self.a[0], self.a[1]],
        #                                                     cirq.X(self.ancilla), control_values=[1, 1, 1]))
        #         else:
        #             circuit.append(cirq.ControlledOperation([self.control, self.a[0], self.a[1]],
        #                                                     cirq.X(self.ancilla), control_values=[0, 1, 1]))
        #     if b[1] == '1':
        #         if choice:
        #             circuit.append(cirq.CNOT(self.control, self.a[1]))
        #         else:
        #             circuit.append(cirq.ControlledOperation([self.control], cirq.X(self.a[1]),
        #                                                     control_values=[0]))
        #     return circuit
        #
        # # If the (choice == True) the operation will carried if the control qubit is equal to 1
        # # Otherwise it will be done if the control qubit is equal to 0
        # if choice:
        #     moment1 = [cirq.TOFFOLI(self.control, self.g[-1], self.ancilla)]
        # else:
        #     moment1 = [cirq.ControlledOperation([self.control, self.g[-1]], cirq.X(self.ancilla),
        #                                         control_values=[0, 1])]
        #
        # if b[0] == '1':
        #     moments = [cirq.TOFFOLI(self.a[0], self.a[1], self.g[0])]
        # else:
        #     moments = []
        #
        # moment3 = []
        #
        # if b[1] == '1':
        #     moments += [cirq.X(self.a[1]), cirq.CNOT(self.a[1], self.g[0])]
        # for i in range(2, n):
        #     moments += [cirq.TOFFOLI(self.g[i - 2], self.a[i], self.g[i - 1])]
        #     moment3 += [cirq.TOFFOLI(self.g[i - 2], self.a[i], self.g[i - 1])]
        #     if b[i] == '1':
        #         moments += [cirq.X(self.a[i]), cirq.CNOT(self.a[i], self.g[i - 1])]
        # circuit.append(moment1)
        # circuit.append(moments[::-1])
        # circuit.append(moment3)
        # circuit.append(moment1)
        # circuit.append(moment3[::-1])
        # circuit.append(moments)
        # # if len(b) > n:
        # #     if b[n] == '1':
        # #         if choice:
        # #             circuit.append(cirq.Moment([cirq.CNOT(self.control, self.ancilla)]))
        # #         else:
        # #             circuit.append(cirq.Moment([cirq.ControlledOperation([self.control, self.ancilla],
        # #                                                                  control_values=[0])]))
        #return circuit

        # The choice parameter will serve to choose between adding c or N-c
        n = len(self.a)
        b = bin(self.constant)[2:].zfill(n)[::-1]
        circuit = cirq.Circuit()

        # Particular cases (Not defined in the paper)
        # Please double check them
        if len(self.a) == 1:
            if b[0] == '1':
                if choice:
                    circuit.append(cirq.ControlledOperation(self.control + [self.a[0]], cirq.X(self.ancilla)))
                else:
                    circuit.append(cirq.ControlledOperation(self.control + [self.a[0]],
                                                            cirq.X(self.ancilla), control_values=[0]*len(self.control)+[1]))
            return circuit
        elif len(self.a) == 2:
            if b[1] == '1':
                if choice:
                    # circuit.append(cirq.TOFFOLI(self.control, self.a[1], self.ancilla))
                    # circuit.append(cirq.CNOT(self.control, self.a[1]))
                    circuit.append(cirq.ControlledOperation(self.control + [self.a[1]], cirq.X(self.ancilla)))
                    circuit.append(cirq.ControlledOperation(self.control, cirq.X(self.a[1])))
                else:
                    circuit.append(cirq.ControlledOperation(self.control+[self.a[1]],
                                                            cirq.X(self.ancilla), control_values=[0]*len(self.control)+[1]))
                    circuit.append(cirq.ControlledOperation(self.control, cirq.X(self.a[1]), control_values=[0]*len(self.control)))
            if b[0] == '1':
                if choice:
                    circuit.append(cirq.ControlledOperation(self.control + [self.a[0], self.a[1]],
                                                            cirq.X(self.ancilla)))
                else:
                    circuit.append(cirq.ControlledOperation(self.control+[self.a[0], self.a[1]],
                                                            cirq.X(self.ancilla), control_values=[0]*len(self.control)+[1, 1]))
            if b[1] == '1':
                if choice:
                    circuit.append(cirq.ControlledOperation(self.control, cirq.X(self.a[1])))
                else:
                    circuit.append(cirq.ControlledOperation(self.control, cirq.X(self.a[1]),
                                                            control_values=[0]*len(self.control)))
            return circuit

        # If the (choice == True) the operation will carried if the control qubit is equal to 1
        # Otherwise it will be done if the control qubit is equal to 0
        if choice:
            moment1 = [cirq.ControlledOperation(self.control + [self.g[-1]], cirq.X(self.ancilla))]
        else:
            moment1 = [cirq.ControlledOperation(self.control+[self.g[-1]], cirq.X(self.ancilla),
                                                control_values=[0]*len(self.control)+[1])]

        if b[0] == '1':
            moments = [cirq.TOFFOLI(self.a[0], self.a[1], self.g[0])]
        else:
            moments = []

        moment3 = []

        if b[1] == '1':
            moments += [cirq.X(self.a[1]), cirq.CNOT(self.a[1], self.g[0])]
        for i in range(2, n):
            moments += [cirq.TOFFOLI(self.g[i - 2], self.a[i], self.g[i - 1])]
            moment3 += [cirq.TOFFOLI(self.g[i - 2], self.a[i], self.g[i - 1])]
            if b[i] == '1':
                moments += [cirq.X(self.a[i]), cirq.CNOT(self.a[i], self.g[i - 1])]
        circuit.append(moment1)
        circuit.append(moments[::-1])
        circuit.append(moment3)
        circuit.append(moment1)
        circuit.append(moment3[::-1])
        circuit.append(moments)
        return circuit
