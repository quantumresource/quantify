import math
import numpy as np

import cirq

from qramcircuits.mpmct_decomposition import *


class SmallDepthLargeWidth:

    def __init__(self, qubits, ctrlVal, decomp_type):
        self.decomposition_type = decomp_type
        self.size_adr_n = len(qubits)
        self.ctrlVal = ctrlVal
        self.circuit = self.construct_circuit(qubits, ctrlVal)

    def construct_circuit(self, qubits, ctrlVal):
        """
        large depth, small width circuits from
        arxiv: 1902.01329v1
        :param qubits: Number of bits for the address space
        :param ctrlVal: Number of bits for storing 2^q True addresses (q < n)
        :return: a Cirq Circuit
        """
        # exponent from 2^n
        n = len(qubits)
        # m = 2^q
        twoPowQ = len(ctrlVal)

        circuit = cirq.circuits.Circuit()

        ancillae = qubits + [cirq.LineQubit(i) for i in range(n * twoPowQ)[n:]]

        targetQubits = [cirq.LineQubit(i) for i in
                        range(twoPowQ * (n + 1))[n * twoPowQ:]]
        finalTarget = cirq.NamedQubit("target")
        k = 0
        step = 1
        op1 = []
        if(twoPowQ%2==1):
            p = int(math.floor(twoPowQ / 2))
        else:
            p = twoPowQ//2 - 1

        # All the gates inhere are parallel, with or without decomposition
        # Moreover, all the gates have structurally the same decomposition
        # Thus, it should be possible to add gates
        parallel_moments_for_op2 = []

        for i in range(p):

            op1 += [[cirq.ops.CNOT(ancillae[n * i + j],
                                         ancillae[n * (i + step) + j]) for j in range(n)]]

            op2 = MPMCTDecomposition(
                qubits = ancillae[n * k:(k + 1) * n],
                decomposition_type = self.decomposition_type,
                search = ctrlVal[k],
                target = targetQubits[k]).decompose(i)
            if len(parallel_moments_for_op2) == 0:
                parallel_moments_for_op2 += op2
            else:
                for g, moment in enumerate(op2):
                    empty_mom = cirq.Moment(parallel_moments_for_op2[g].operations
                                            + moment.operations)

                    parallel_moments_for_op2[g] = empty_mom

            k += 1
            step += 1
            for j in range(n):

                op1.append(cirq.ops.CNOT(ancillae[n * i + j],
                                         ancillae[n * (i + step) + j]))

            op2 = MPMCTDecomposition(
                qubits = ancillae[n * k:(k + 1) * n],
                decomposition_type = self.decomposition_type,
                search = ctrlVal[k],
                target = targetQubits[k]).decompose(i + p + 1)
            if len(parallel_moments_for_op2) == 0:
                parallel_moments_for_op2 += op2
            else:
                for f, moment in enumerate(op2):
                    empty_mom = cirq.Moment(parallel_moments_for_op2[f].operations
                                            + moment.operations)

                    parallel_moments_for_op2[f] = empty_mom

            k += 1

        if (twoPowQ % 2 == 0):
            op1 += [[cirq.ops.CNOT(ancillae[n * p + j],
                                         ancillae[n * (p + step) + j]) for j in range(n)]]
            op2 = MPMCTDecomposition(
                qubits = ancillae[n * k:(k + 1) * n],
                decomposition_type = self.decomposition_type,
                search = ctrlVal[k],
                target = targetQubits[k]).decompose(2 * p + 1)
            if len(parallel_moments_for_op2) == 0:
                parallel_moments_for_op2 = op2
            else:
                for f, moment in enumerate(op2):
                    empty_mom = cirq.Moment(parallel_moments_for_op2[f].operations
                                            + moment.operations)

                    parallel_moments_for_op2[f] = empty_mom

            op2 = MPMCTDecomposition(
                qubits = ancillae[n * (k+1):(k + 2) * n],
                decomposition_type = self.decomposition_type,
                search = ctrlVal[k+1],
                target = targetQubits[k+1]).decompose(2 * p + 2)
            if len(parallel_moments_for_op2) == 0:
                parallel_moments_for_op2 += op2
            else:
                for f, moment in enumerate(op2):
                    empty_mom = cirq.Moment(parallel_moments_for_op2[f].operations
                                            + moment.operations)

                    parallel_moments_for_op2[f] = empty_mom

        op = [[cirq.ops.H(targetQubits[i]) for i in range(twoPowQ-1)]]

        q = int(np.log2(twoPowQ))
        for i in range(q-1,-1,-1):
            op+=[[cirq.CNOT(targetQubits[j],targetQubits[j+2**i]) for j in range(2**i-1,2**q,2**(i+1))]]
        op3 = op[::-1][:q]

        circuit.append(op)
        circuit.append(op1, strategy=cirq.InsertStrategy.NEW_THEN_INLINE)

        # MPMCT
        circuit.append(parallel_moments_for_op2,
                       strategy=cirq.InsertStrategy.NEW_THEN_INLINE)

        # Parities
        circuit.append(op3, strategy=cirq.InsertStrategy.NEW_THEN_INLINE)
        circuit.append([cirq.ops.CNOT(targetQubits[-1],finalTarget),cirq.ops.CNOT(finalTarget,targetQubits[-1])])
        # Uncompute parities
        circuit.append(op3[::-1], strategy=cirq.InsertStrategy.NEW_THEN_INLINE)

        circuit.append(op1, strategy=cirq.InsertStrategy.NEW_THEN_INLINE)


        return circuit

    def verify_number_qubits(self):
        q = np.log2(len(self.ctrlVal))

        if self.decomposition_type == MPMCTDecompType.NO_DECOMP:
            paper_qubits = (self.size_adr_n+1)*2**q+1
        elif self.decomposition_type == MPMCTDecompType.ALLOW_DECOMP:
            paper_qubits = self.size_adr_n*2**(q+1) + 1
        else:
            return print("decomposition value should be either 0 or -1")
        nr_q = len(self.circuit.all_qubits())
        return nr_q == paper_qubits


    #verify depth

    def verify_depth(self):

        if self.decomposition_type == MPMCTDecompType.NO_DECOMP: # depth without decomposition
            formula_from_paper = 3*np.log2(len(self.ctrlVal))+1+2
            circ_depth = len(self.circuit)-len(self.ctrlVal)-1

        elif self.decomposition_type == MPMCTDecompType.ALLOW_DECOMP: # depth after decomposition
             MPMCTDepth = 28*self.size_adr_n-60 #7(4(n-2)-4) + 4x5 + 4

            # the first hadamard is not parallelizable
             formula_from_paper = 3*np.log2(len(self.ctrlVal)) + 2 + MPMCTDepth

             circ_depth = len(self.circuit)-(1+len(self.ctrlVal)+4*self.size_adr_n-6-4)
            #len(circuit) = 1+3q+2^q+4*n-6+2+28n-64

        print("have {} == {} should".format(circ_depth, formula_from_paper))
        verif = (circ_depth == formula_from_paper)
        return verif

    def verify_T_depth(self):
        if self.decomposition_type == MPMCTDecompType.NO_DECOMP:
            MPMCT_depth = 0
        elif self.decomposition_type == MPMCTDecompType.ALLOW_DECOMP:
            MPMCT_depth = 4*(self.size_adr_n-2)
        formula_from_paper = MPMCT_depth

        #we substracted that quantity because of the NEW_THEN_INLINE
        #but they are parallele
        t_depth = count_t_depth_of_circuit(self.circuit) #- (len(self.ctrlVal)-1)*MPMCT_depth

        print("have {} == {} should".format(t_depth, formula_from_paper))
        verif = (t_depth == formula_from_paper)
        return verif

    def verify_T_count(self):
        if self.decomposition_type == MPMCTDecompType.NO_DECOMP:
            MPMCT_t_count = 0 # 0 T when not decomposed
        elif self.decomposition_type == MPMCTDecompType.ALLOW_DECOMP:
            MPMCT_t_count = 12*self.size_adr_n-20

        formula_from_paper = len(self.ctrlVal)*MPMCT_t_count

        nr_t = count_t_of_circuit(self.circuit)

        print("have {} == {} should".format(nr_t, formula_from_paper))
        verif = (formula_from_paper == nr_t)
        return verif

    def verify_hadamard_count(self):
        if self.decomposition_type == MPMCTDecompType.NO_DECOMP:
            MPMCT_h_count = 0
        elif self.decomposition_type == MPMCTDecompType.ALLOW_DECOMP:
            MPMCT_h_count = 4*self.size_adr_n - 6

        formula_from_paper = len(self.ctrlVal)*MPMCT_h_count
        nr_h = count_h_of_circuit(self.circuit) - len(self.ctrlVal)+1


        print("have {} == {} should".format(nr_h, formula_from_paper))
        verif = (formula_from_paper == nr_h)
        return verif

    def verify_cnot_count(self):
        if self.decomposition_type == MPMCTDecompType.NO_DECOMP:
            num_cnots_dec = 0
            formula_from_paper = 2*self.size_adr_n*(len(self.ctrlVal)-1)+2*len(self.ctrlVal)
        elif self.decomposition_type == MPMCTDecompType.ALLOW_DECOMP:
            num_cnots_dec = 26*self.size_adr_n-38
            formula_from_paper = len(self.ctrlVal)*num_cnots_dec -2*self.size_adr_n

        nr_cnot = count_cnot_of_circuit(self.circuit)-(len(self.ctrlVal)-1) # ignoring the first cnots
        print("have {} == {} should".format(nr_cnot, formula_from_paper))
        verif = (formula_from_paper == nr_cnot)
        return verif