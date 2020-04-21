import cirq

from qramcircuits.mpmct_decomposition import *


class LargeDepthSmallWidth:
    def __init__(self, qubits, search, decomp_type):
        self.decomposition_type = decomp_type
        self.size_adr_n = len(qubits)
        self.search = search
        self.circuit = self.construct_circuit(qubits, search)


    def construct_circuit(self, qubits, search):
        circuit = cirq.Circuit()
        op = []
        target = cirq.NamedQubit("target")
        for b in search:
            op.append(MPMCTDecomposition(qubits, self.decomposition_type, b, target).decompose())

        # circuit.append(op, strategy=cirq.InsertStrategy.NEW_THEN_INLINE)
        circuit.append(op)

        # return a new circuit with earliest insertion strategy
        # such that the depth is correct
        # is this a hack or a proper solution?
        n_circuit = cirq.Circuit()
        for moment in circuit:
            n_moment = cirq.Moment()
            for op in moment:
                if isinstance(op, cirq.GateOperation) and \
                    op.gate not in [cirq.T, cirq.T**-1]:
                    # earliest insertion for all gates except T gates
                    n_circuit.append(op)
                else:
                    # This moment does include only T gates
                    n_moment = n_moment.with_operation(op)

            if len(n_moment) > 0 :
                n_circuit.append(n_moment)

        return n_circuit

    def verify_number_qubits(self):

        if self.decomposition_type == MPMCTDecompType.NO_DECOMP: # this is the original circuit without any decomposition
            formula_from_paper = self.size_adr_n+1
        elif self.decomposition_type == MPMCTDecompType.ALLOW_DECOMP: #circuit in case of decomposition
            formula_from_paper = 2*self.size_adr_n

        # The total number of qubits from the circuit
        circ_qubits = len(self.circuit.all_qubits())

        print("have {} == {} should".format(circ_qubits, formula_from_paper))
        verif = (circ_qubits == formula_from_paper)
        return verif

    def verify_depth(self):

        if self.decomposition_type == MPMCTDecompType.NO_DECOMP: # depth without decomposition
            return len(self.circuit) == len(self.search)
        elif self.decomposition_type == MPMCTDecompType.ALLOW_DECOMP: # depth after decomposition
             MPMCTDepth = 28*self.size_adr_n-60 #7(4(n-2)-4) + 4x5 + 4

        formula_from_paper = len(self.search)*MPMCTDepth + 1  #the first hadamard is not parallelizable

        circ_depth = len(self.circuit)

        print("have {} == {} should".format(circ_depth, formula_from_paper))
        verif = (circ_depth == formula_from_paper)
        return verif

    def verify_T_count(self):
        if self.decomposition_type == MPMCTDecompType.NO_DECOMP:
            MPMCT_t_count = 0 # 0 T when not decomposed
        elif self.decomposition_type == MPMCTDecompType.ALLOW_DECOMP:
            MPMCT_t_count = 12*self.size_adr_n-20

        formula_from_paper = len(self.search)*MPMCT_t_count

        nr_t = count_t_of_circuit(self.circuit)

        print("have {} == {} should".format(nr_t, formula_from_paper))
        verif = (formula_from_paper == nr_t)
        return verif

    def verify_T_depth(self):
        if self.decomposition_type == MPMCTDecompType.NO_DECOMP:
            MPMCT_depth = 0
        elif self.decomposition_type == MPMCTDecompType.ALLOW_DECOMP:
            MPMCT_depth = 4*(self.size_adr_n-2)
        formula_from_paper = len(self.search)*MPMCT_depth
        # t_depth = count_t_depth_of_circuit(self.circuit)
        t_depth = count_t_depth_of_circuit(self.circuit)

        print("have {} == {} should".format(t_depth, formula_from_paper))
        verif = (t_depth == formula_from_paper)
        return verif

    def verify_hadamard_count(self):
        if self.decomposition_type == MPMCTDecompType.NO_DECOMP:
            MPMCT_h_count = 0
        elif self.decomposition_type == MPMCTDecompType.ALLOW_DECOMP:
            MPMCT_h_count = 4*self.size_adr_n - 6

        formula_from_paper = len(self.search)*MPMCT_h_count
        nr_h = count_h_of_circuit(self.circuit)


        print("have {} == {} should".format(nr_h, formula_from_paper))
        verif = (formula_from_paper == nr_h)
        return verif

    def verify_cnot_count(self):
        if self.decomposition_type == MPMCTDecompType.NO_DECOMP:
            num_cnots_dec = 0
        elif self.decomposition_type == MPMCTDecompType.ALLOW_DECOMP:
            num_cnots_dec = 24*self.size_adr_n-40


        formula_from_paper = len(self.search)*num_cnots_dec
        nr_cnot = count_cnot_of_circuit(self.circuit)
        print("have {} == {} should".format(nr_cnot, formula_from_paper))
        verif = (formula_from_paper == nr_cnot)
        return verif