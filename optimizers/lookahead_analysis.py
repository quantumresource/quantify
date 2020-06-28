import cirq
import numpy as np
import matplotlib.pyplot as plt


class LookAheadAnalysis:

    def __init__(self, circuit):
        self.circuit = circuit

    def lookahead(self, window_size, function):

        """
        This function generates the analysis data as a matrix of the form step, #A and Look#A
        where #A the number of gates executed  at the current step and Look#A the number of gates
        that will be executed in the next window_size steps.
        :param window_size:
        :param function:
        :return:  a matrix of the form step, #A and Look#A
        """
        size = len(self.circuit) - window_size + 1
        result = np.zeros((size + 1, 3))
        for i in range(size):
            result[i][0], result[i][1], result[i][2] = i, function(self.circuit[i:i + 1]), \
                                                       function(self.circuit[i:i + window_size])

        result[size][0], result[size][1], result[size][2] = size, function(self.circuit[size:size + 1]), \
                                                            function(self.circuit[size:])

        return result

    @staticmethod
    def find_T_gates(subcircuit):
        """
        Function that returns the number of T-gates in a sub-circuit/circuit
        :param subcircuit:
        :return:
        """
        op_count = 0
        for moment in subcircuit:
            for operation in moment:
                # if a gate is found in this moment,
                #  then increase depth and break to the next moment
                if isinstance(operation, cirq.GateOperation) \
                        and operation.gate in [cirq.T, cirq.T**-1]:
                    op_count += 1
        return op_count

    @staticmethod
    def find_parallel_Toffolis(self, subcircuit):

        """
        Function that returns the parallel Toffolis in a sub-circuit/circuit
        :param subcircuit: circuit/sub-circuit in which the parallel Toffolis are to be found
        :return: a dictionnary where the keys are the indice of the moment which
                 contain Toffolis and the values are the list of toffolis which are
                 parallel to the first Toffoli moment in circuit/subcircuit
        """
        result = dict()
        i = 0
        # the idea is as long as a Toffoli controls is not in the same wire the target of one of the previous
        # Toffolis is or vice versa  then it's parallel with the previous Toffolis otherwise it's not and the
        # following Toffolis are checked against this Toffoli
        for moment in subcircuit:
            result[i] = []
            for operation in moment:

                if isinstance(operation, cirq.GateOperation) \
                        and operation.gate in [cirq.TOFFOLI]:
                    temp = True

                    for j in range(i):
                        for x in result[j]:
                            if operation.qubits[2] in x.qubits[:2] or (
                                    operation.qubits[0] == x.qubits[2] or operation.qubits[1] == x.qubits[2]):
                                temp = False
                    if temp:
                        result[i].append(operation)
                    else:
                        return result
            i += 1

        return result

    def save_csv(self, results_as_matrix, output_file_name="output.csv"):
        np.savetxt(output_file_name, results_as_matrix, fmt='%i', delimiter=",")



    def plot_data(self, data, fname=None):
        """
        plot_data plots the number of gates executed at a specific step against the time (step) axis
        and the next number of executed gates in the "window_size" from "step" also wrt the time axis
        :param: data: data to be ploted
        :param fname: path to save data
        """

        plt.figure()
        plt.xlabel("Time step")
        plt.plot(data[:, 0], data[:, 1], marker='o', label="#A", color='r')
        plt.plot(data[:, 0], data[:, 2], marker='o', label="analysis", color='g')
        plt.legend()

        if fname is None:
            plt.show()
        else:
            plt.savefig(fname)

