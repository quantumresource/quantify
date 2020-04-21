from utils.counting_utils import *
from qramcircuits.toffoli_decomposition import ToffoliDecomposition, \
    ToffoliDecompType

import utils.clifford_t_utils as ctu
import utils.misc_utils as miscutils

import optimizers as qopt
import numpy as np

class BucketBrigadeDecompType:
    def __init__(self, toffoli_decomp_types, parallel_toffolis):
        self.dec_fan_in = toffoli_decomp_types[0]
        self.dec_mem = toffoli_decomp_types[1]
        self.dec_fan_out = toffoli_decomp_types[2]

        # Should the Toffoli decompositions be parallelised?
        # In this case it is assumed that the ToffoliDecompType.ZERO_ANCILLA_TDEPTH_4
        # is used (not checked, for the moment)...
        # We are not sure how to design this. Keep it.
        self.parallel_toffolis = parallel_toffolis


    # def get_dec_fan_in(self):
    #     return self.dec_fan_in
    #
    # def get_dec_fan_out(self):
    #     return self.dec_fan_out
    #
    # def get_dec_mem(self):
    #     return  self.dec_mem

    def get_decomp_types(self):
        return [self.dec_fan_in,
                self.dec_mem,
                self.dec_fan_out]


class BucketBrigade():

    def __init__(self, qubits, decomp_scenario):

        self._qubit_order = []

        self.decomp_scenario = decomp_scenario
        self.qubits = qubits
        self.size_adr_n = len(qubits)

        self.circuit = self.construct_circuit(qubits)

        # # Cancel other CNOTs
        # qopt.CancelNghCNOTs().apply_until_nothing_changes(self.circuit,
        #                                                   count_cnot_of_circuit)

    @staticmethod
    def optimise_h_and_cnot(circuit_1):
        # Allow the optimization of Hadamard gates
        miscutils.flag_operations(circuit_1, [cirq.ops.H])

        # Hadamards that cancel transfer the flag to neighbouring gates
        qopt.CancelNghHadamards(transfer_flag=True).optimize_circuit(circuit_1)
        #
        # The hope is that the neighbouring gates are CNOTs that will transfer
        # optimization flags
        qopt.CancelNghCNOTs(transfer_flag=True) \
            .apply_until_nothing_changes(circuit_1, count_cnot_of_circuit)

        # Clean the empty moments
        cirq.optimizers.DropEmptyMoments().optimize_circuit(circuit_1)

        # clean all the flags
        miscutils.remove_all_flags(circuit_1)

    @property
    def qubit_order(self):
        return self._qubit_order

    def get_b_ancilla_name(self, i, n):
        return "b_" + str(miscutils.my_bin(i, n))

    def construct_fan_structure(self, qubits):
        n = len(qubits)

        all_ancillas = []

        anc_created = [cirq.NamedQubit(self.get_b_ancilla_name(i, n)) for i in range(2)]
        all_ancillas += anc_created

        compute_fanin_moments = [
            cirq.Moment([cirq.ops.CNOT(qubits[0], anc_created[0])]),
            cirq.Moment([cirq.ops.CNOT(anc_created[0], anc_created[1])])
        ]

        # circuit.append(cirq.ops.CNOT(qubits[0], anc_created[0]))
        # circuit.append(cirq.ops.CNOT(anc_created[0], anc_created[1]))
        # we will need the ancillae
        anc_previous = anc_created

        for i in range(1, n):
            # defining the new ancillae
            # in each iteration we create 2**i new ancillae
            anc_created = [cirq.NamedQubit(self.get_b_ancilla_name(i, n)) for i in
                           range(2 ** i, 2 ** (i + 1))]
            # all_ancillas += anc_created

            # The number of created ancillas equals the number of previous ancilla
            assert (len(anc_created) == len(anc_previous))

            # appending the Toffoli operations to the circuit
            # ccx_ops = []
            cnot_moment_ops = []

            for j in range(2 ** i):
                ccx_first_control = qubits[i]
                ccx_second_control = anc_previous[j]
                ccx_target = anc_created[j]

                compute_fanin_moments += [
                    cirq.Moment([cirq.TOFFOLI(ccx_first_control,
                                           ccx_second_control,
                                           ccx_target)])
                ]

                cnot_control = ccx_target
                cnot_target = ccx_second_control
                cnot_moment_ops.append(cirq.ops.CNOT(cnot_control, cnot_target))

            # circuit.append(ccx_ops)
            # circuit.append(cirq.Moment(cnot_moment_ops))
            compute_fanin_moments.append(cirq.Moment(cnot_moment_ops))

            """
            Create the pattern necessary for the next step to work
            One created ancilla followed by one existing ancilla
            """
            # saving the current ancillae to use them in the next iteration
            prev_ancilla_2 = anc_previous
            anc_previous = []

            for l in range(0, len(anc_created)):
                anc_previous.append(anc_created[l])
                anc_previous.append(prev_ancilla_2[l])

        assert (len(anc_previous) == 2 ** n)

        return anc_previous, compute_fanin_moments

    def construct_circuit(self, qubits):

        # first part of the circuit (in case n = 2)

        circuit = cirq.Circuit()

        # number of qubits
        n = len(qubits)
        memory = [cirq.NamedQubit("m" + miscutils.my_bin(i, n)) for i in range(2 ** (n))]
        target = cirq.NamedQubit("target")

        """
            According to the notes received from Olivia DiMatteo the 
            the FANIN and the FANOUT Toffolis are decomposed differently
            to the Toffolis connected to the memory
        # """
        # if self.decomposition_type == ToffoliDecompType.FOUR_ANCILLA_TDEPTH_1_B:
        #     dec_fan_in = ToffoliDecompType.FOUR_ANCILLA_TDEPTH_1_A
        #     dec_fan_out = ToffoliDecompType.FOUR_ANCILLA_TDEPTH_1_A
        #     dec_mem = ToffoliDecompType.FOUR_ANCILLA_TDEPTH_1_B
        # elif self.decomposition_type == ToffoliDecompType.ZERO_ANCILLA_TDEPTH_2_COMPUTE:
        #     dec_fan_in = ToffoliDecompType.FOUR_ANCILLA_TDEPTH_1_COMPUTE
        #     dec_fan_out = ToffoliDecompType.NO_DECOMP
        #     dec_mem = ToffoliDecompType.NO_DECOMP
        # else:
        #     dec_fan_in = self.decomposition_type
        #     dec_fan_out = self.decomposition_type
        #     dec_mem = self.decomposition_type
        # [dec_fan_in, dec_fan_out, dec_mem] = self.decomp_scenario.get_decomp_type()

        all_ancillas, compute_fanin_moments = self.construct_fan_structure(qubits)

        """
            Adding the FANIN
        """

        comp_fan_in = cirq.Circuit(
            ToffoliDecomposition.
                construct_decomposed_moments(compute_fanin_moments,
                                             self.decomp_scenario.dec_fan_in)
        )

        # If necessary, parallelise the Toffoli decompositions
        if self.decomp_scenario.parallel_toffolis:
            comp_fan_in = BucketBrigade.parallelise_toffolis(comp_fan_in)

        circuit.append(comp_fan_in)

        """
            Adding Memory wiring
        """
        # wiring with the memory
        memory_operations = []
        for i in range(len(memory)):
            mem_toff = cirq.TOFFOLI.on(
                all_ancillas[len(memory) - 1 - i],
                memory[i],
                target)

            memory_operations.append(cirq.Moment([mem_toff]))

        permutation = [0, 1, 2]
        # If necessary, prepare for the parallelisation of Toffoli decompositions
        if self.decomp_scenario.parallel_toffolis:
            permutation = [0, 2, 1]

        # Create a sub-circuit from the moments
        # TODO: This is redundant, should be from the beginning
        memory_decomposed = cirq.Circuit(\
            ToffoliDecomposition.\
                construct_decomposed_moments(memory_operations,
                                             self.decomp_scenario.dec_mem,
                                             permutation)
        )
        if self.decomp_scenario.dec_mem in [ToffoliDecompType.FOUR_ANCILLA_TDEPTH_1_A, ToffoliDecompType.FOUR_ANCILLA_TDEPTH_1_B, ToffoliDecompType.ZERO_ANCILLA_TDEPTH_4]:
            BucketBrigade.optimise_h_and_cnot(memory_decomposed)

            # If necessary, parallelise the Toffoli decompositions
        if self.decomp_scenario.parallel_toffolis:
            memory_decomposed = BucketBrigade.parallelise_toffolis(memory_decomposed)

        circuit.append(memory_decomposed)

        """
            Adding the FANOUT
        """
        compute_fanout_moments = ctu.reverse_moments(compute_fanin_moments)

        # If necessary, parallelise the Toffoli decompositions
        comp_fan_out = cirq.Circuit(
            ToffoliDecomposition.
                construct_decomposed_moments(compute_fanout_moments,
                                             self.decomp_scenario.dec_fan_out,
                                             [1, 0, 2]))

        if self.decomp_scenario.parallel_toffolis:
            comp_fan_out = BucketBrigade.parallelise_toffolis(
                cirq.Circuit(comp_fan_out.all_operations())
            )

        circuit.append(comp_fan_out)

        # This is the qubit order for drawing the circuits
        # similar to Olivia's paper
        self._qubit_order += qubits[::-1]
        # Sort the ancillas by their name
        self._qubit_order += sorted(all_ancillas)
        self._qubit_order += memory[::-1]

        # Add only the necessary ancilla
        all_qubits = circuit.all_qubits()
        for qub in ToffoliDecomposition(None, None).ancilla:
            if qub in all_qubits:
                self._qubit_order += [qub]

        self._qubit_order += [target]

        return circuit

    @staticmethod
    def parallelise_toffolis(circuit_1):

        # Assume that the first and the last moment are only with Hadamards
        # Remove the moments for the optimisation to work
        circuit_2 = circuit_1[1:-1]
        # circuit_2 = circuit_1
        # print(circuit_2)

        """
            This is to say that as long as the circuit has been changed
            Very expensive in terms of computation, because drawing the
            circuit takes a lot of time
        """
        # str_circ = ""
        # while str_circ != str(circuit_2):
        #     str_circ = str(circuit_2)
        old_circuit_2 = cirq.Circuit()
        while old_circuit_2 != circuit_2:
            old_circuit_2 = cirq.Circuit(circuit_2)

            qopt.CommuteTGatesToStart().optimize_circuit(circuit_2)
            cirq.optimizers.DropEmptyMoments().optimize_circuit(circuit_2)

            qopt.ParallelizeCNOTSToLeft().optimize_circuit(circuit_2)

            # print(circuit_2)

            # print("... reinsert")
            circuit_2 = cirq.Circuit(circuit_2.all_operations()
                                     # ,strategy=cirq.InsertStrategy.NEW
                                     )



        circuit_1 = cirq.Circuit(circuit_1[0] + circuit_2 + circuit_1[-1])
        # circuit_1 = circuit_2

        return circuit_1


    """
        Verifications
    """

    def verify_number_qubits(self):

        # The Toffoli ancilla are not counted, because we assume at this state
        # that the circuit is not decomposed
        formula_from_paper = self.size_adr_n + 2**(self.size_adr_n + 1) + 1

        # If decomposed, the Toffoli would introduce this number of ancilla
        # I am passing None to qubits in the ToffoliDecomposition, because
        # I do not care about the decomposition circuit, but about a number
        # that depends only on the decomposition_type
        [dec_fan_in, dec_fan_out, dec_mem] = self.decomp_scenario.get_decomp_types()
        local_toffoli = max(
            ToffoliDecomposition(dec_fan_in, None).number_of_ancilla(),
            ToffoliDecomposition(dec_fan_out, None).number_of_ancilla(),
            ToffoliDecomposition(dec_mem, None).number_of_ancilla())
        formula_from_paper += local_toffoli

        # The total number of qubits from the circuit
        circ_qubits = len(self.circuit.all_qubits())

        # print("have {} == {} should".format(circ_qubits, formula_from_paper))
        verif = (circ_qubits == formula_from_paper)
        return verif

    def verify_depth(self,Alexandru_scenario=False):
        """"
            We consider a mixture of Toffoli decompositions
            For the moment, the mixture is of two types
            For each type we have a number of CNOTs - a tuple with two values
        """
        # [dec_fan_in, dec_fan_out, dec_mem] = self.decomp_scenario.get_decomp_types()

        num_toffolis_per_type = np.array([2**self.size_adr_n - 2,
                                          2**self.size_adr_n,
                                          2**self.size_adr_n - 2])
        if(Alexandru_scenario):
            num_toffolis_per_type = np.array([self.size_adr_n - 1,
                                              1,
                                            self.size_adr_n - 1]) #it's rather the number of parallel Tofollis
        # if self.dec_fan_in == ToffoliDecompType.ZERO_ANCILLA_TDEPTH_3:
        #     toff_dec_depth_per_type = np.array([10, 0, 0])
        # if self.dec_fan_out == ToffoliDecompType.ZERO_ANCILLA_TDEPTH_3:
        #     toff_dec_depth_per_type += np.array([0, 0, 10])
        # if self.dec_mem == ToffoliDecompType.ZERO_ANCILLA_TDEPTH_3:
        #     toff_dec_depth_per_type += np.array([0, 9, 0])
        toff_dec_depth_per_type = [
            ToffoliDecomposition(self.decomp_scenario.dec_fan_in).depth,
            ToffoliDecomposition(self.decomp_scenario.dec_mem).depth,
            ToffoliDecomposition(self.decomp_scenario.dec_fan_out).depth,
        ]

        formula_from_paper = 0
        for elem in zip(num_toffolis_per_type,toff_dec_depth_per_type):
            formula_from_paper += elem[0] * elem[1]
        # depth after decomposition
        # if self.decomposition_type == ToffoliDecompType.NO_DECOMP:
        #     toff_dec_depth_per_type = (1, 0)
        #     num_toffolis_per_type = (3 * 2**self.size_adr_n - 4, 0)
        #
        # elif self.decomposition_type == ToffoliDecompType.ZERO_ANCILLA_TDEPTH_3:
        #     """
        #         The Toffoli decomposition has depth 10, but the Toffolis
        #         that are touching the memory have the same target such that,
        #         for all but one, the Hadamard gate on the target is cancelled
        #         leaving the depth, for all but one, being 9 instead of 10
        #     """
        #     toff_dec_depth_per_type = (10, 9)
        #     num_toffolis_per_type = (2 * 2**self.size_adr_n - 4, 2**self.size_adr_n)
        #
        # elif self.decomposition_type == ToffoliDecompType.ONE_ANCILLA_TDEPTH_2:
        #     toff_dec_depth_per_type = (13, 12)
        #     num_toffolis_per_type = (2 * 2**self.size_adr_n - 4, 2**self.size_adr_n)
        #
        # elif self.decomposition_type == ToffoliDecompType.FOUR_ANCILLA_TDEPTH_1_A:
        #     toff_dec_depth_per_type = (7, 0)
        #     num_toffolis_per_type = (3 * 2**self.size_adr_n - 4, 0)
        #
        # elif self.decomposition_type == ToffoliDecompType.FOUR_ANCILLA_TDEPTH_1_B:
        #
        #     num_toffolis_fan = 2 ** (self.size_adr_n + 1) - 4
        #     num_toffolis_mem = 2 ** self.size_adr_n
        #     num_toffolis_per_type = (num_toffolis_fan, num_toffolis_mem)
        #
        #     toff_dec_depth_per_type = (7, 13)

        depth_coupling_nodes = 2*self.size_adr_n + 2

        # formula_from_paper = 0
        # for elem in zip(num_toffolis_per_type, toff_dec_depth_per_type):
        #     formula_from_paper += elem[0] * elem[1]

        formula_from_paper += depth_coupling_nodes

        """
            Special cases
        """
        reduced_depth = 0 #it's the canceled cnots and hadamards for olivia's scenario
        if (self.decomp_scenario.dec_mem == ToffoliDecompType.FOUR_ANCILLA_TDEPTH_1_B):
            reduced_depth = 8 * (2 ** self.size_adr_n - 1) # 8=2(3cnots +1hadmard)

        formula_from_paper -= reduced_depth
        # if self.decomposition_type in [ToffoliDecompType.ZERO_ANCILLA_TDEPTH_3, ToffoliDecompType.ONE_ANCILLA_TDEPTH_2]:
        #     # This is the "one Toffoli with depth 10"
        #     formula_from_paper += 1
        # elif self.decomposition_type == ToffoliDecompType.FOUR_ANCILLA_TDEPTH_1_B:
        #     # The mixture leaves 8 depth which are not cancelled
        #     formula_from_paper += 8




        circ_depth = len(self.circuit)

        print("have {} == {} should".format(circ_depth, formula_from_paper))
        verif = (circ_depth == formula_from_paper)
        return verif




    def verify_T_count(self):
        # if self.decomposition_type == ToffoliDecompType.NO_DECOMP:
        #     t_count_toffoli = 0
        # elif self.decomposition_type in \
        #         [ToffoliDecompType.ZERO_ANCILLA_TDEPTH_3,
        #         ToffoliDecompType.ONE_ANCILLA_TDEPTH_2,
        #         ToffoliDecompType.FOUR_ANCILLA_TDEPTH_1_A,
        #         ToffoliDecompType.FOUR_ANCILLA_TDEPTH_1_B]:
        #     t_count_toffoli = 7
        num_toffolis_per_type = np.array([2 ** self.size_adr_n - 2,
                                          2 ** self.size_adr_n - 2,
                                          2 ** self.size_adr_n])

        # [dec_fan_in, dec_fan_out, dec_mem] = self.decomp_scenario.get_decomp_types()

        toff_dec_t_count_per_type = [
            ToffoliDecomposition(self.decomp_scenario.dec_fan_in).number_of_t,
            ToffoliDecomposition(self.decomp_scenario.dec_fan_out).number_of_t,
            ToffoliDecomposition(self.decomp_scenario.dec_mem).number_of_t
        ]

        formula_from_paper = 0
        for elem in zip(toff_dec_t_count_per_type,num_toffolis_per_type):
            formula_from_paper += elem[0]*elem[1]


        nr_t = count_t_of_circuit(self.circuit)

        # print("have {} == {} should".format(nr_t, formula_from_paper))
        verif = (formula_from_paper == nr_t)
        return verif

    def verify_T_depth(self, Alexandru_scenario=False):
        # if self.decomposition_type == ToffoliDecompType.NO_DECOMP:
        #     tof_dec_t_depth = 0
        # elif self.decomposition_type == ToffoliDecompType.ZERO_ANCILLA_TDEPTH_3:
        #     tof_dec_t_depth = 3
        # elif self.decomposition_type == ToffoliDecompType.ONE_ANCILLA_TDEPTH_2:
        #     tof_dec_t_depth = 2
        # elif self.decomposition_type in \
        #         [ToffoliDecompType.FOUR_ANCILLA_TDEPTH_1_A,
        #          ToffoliDecompType.FOUR_ANCILLA_TDEPTH_1_B]:
        #     tof_dec_t_depth = 1
        num_toffolis_per_type = np.array([2 ** self.size_adr_n - 2,
                                          2 ** self.size_adr_n - 2,
                                          2 ** self.size_adr_n])

        if (Alexandru_scenario):
            num_toffolis_per_type = np.array([self.size_adr_n - 1, 1,
                                              self.size_adr_n - 1]) #it's rather the number of parallel Tofollis
        # [dec_fan_in, dec_fan_out, dec_mem] = self.decomp_scenario.get_decomp_types()

        toff_dec_t_depth_per_type = [
            ToffoliDecomposition(self.decomp_scenario.dec_fan_in).t_depth,
            ToffoliDecomposition(self.decomp_scenario.dec_fan_out).t_depth,
            ToffoliDecomposition(self.decomp_scenario.dec_mem).t_depth
        ]

        formula_from_paper = 0
        for elem in zip(toff_dec_t_depth_per_type, num_toffolis_per_type):
            formula_from_paper += elem[0] * elem[1]

        t_depth = count_t_depth_of_circuit(self.circuit)

        print("have {} == {} should".format(t_depth, formula_from_paper))
        verif = (t_depth == formula_from_paper)
        return verif

    def verify_hadamard_count(self, Alexandru_scenario=False):
        # if self.decomposition_type == ToffoliDecompType.NO_DECOMP:
        #     formula_from_paper = 0
        # else:
        #     # This formula assumes that Hadamard gates are optimized in pairs
        #     formula_from_paper = 4 * 2**self.size_adr_n - 6
        num_toffolis_per_type = np.array([2 ** self.size_adr_n - 2,
                                          2 ** self.size_adr_n - 2,
                                          2 ** self.size_adr_n])

        # [dec_fan_in, dec_fan_out, dec_mem] = self.decomp_scenario.get_decomp_types()

        toff_dec_H_count_per_type = [
            ToffoliDecomposition(self.decomp_scenario.dec_fan_in).number_of_hadamards,
            ToffoliDecomposition(self.decomp_scenario.dec_fan_out).number_of_hadamards,
            ToffoliDecomposition(self.decomp_scenario.dec_mem).number_of_hadamards
        ]

        formula_from_paper = 0
        for elem in zip(toff_dec_H_count_per_type, num_toffolis_per_type):
            formula_from_paper += elem[0] * elem[1]
        """
        special cases
        """
        num_of_canceled_H = 0
        if(self.decomp_scenario.dec_mem in [ToffoliDecompType.FOUR_ANCILLA_TDEPTH_1_A, ToffoliDecompType.FOUR_ANCILLA_TDEPTH_1_B] or Alexandru_scenario):
            num_of_canceled_H = 2**(self.size_adr_n+1)-2
        formula_from_paper-=num_of_canceled_H
        nr_h = count_h_of_circuit(self.circuit)
        print("have {} == {} should".format(nr_h, formula_from_paper))
        verif = (formula_from_paper == nr_h)
        return verif

    def verify_cnot_count(self,Alexandru_scenario=False):
        """"
            We consider a mixture of Toffoli decompositions
            For the moment, the mixture is of two types
            For each type we have a number of CNOTs - a tuple with two values
        """
        # [dec_fan_in, dec_fan_out, dec_mem] = self.decomp_scenario.get_decomp_types()

        num_toffolis_per_type = np.array([2 ** self.size_adr_n - 2,
                                          2 ** self.size_adr_n,
                                          2 ** self.size_adr_n - 2])

        toff_dec_cnot_count_per_type = [
            ToffoliDecomposition(self.decomp_scenario.dec_fan_in).number_of_cnots,
            ToffoliDecomposition(self.decomp_scenario.dec_mem).number_of_cnots,
            ToffoliDecomposition(self.decomp_scenario.dec_fan_out).number_of_cnots
        ]

        # if self.decomposition_type == ToffoliDecompType.NO_DECOMP:
        #     num_cnots_dec_per_type = (0, 0)
        #     num_toffolis = 3 * 2 ** self.size_adr_n - 4
        #     num_toffolis_per_type = (num_toffolis, 0)
        #
        # elif self.decomposition_type == ToffoliDecompType.ZERO_ANCILLA_TDEPTH_3:
        #     num_cnots_dec_per_type = (7, 0)
        #     num_toffolis = 3 * 2 ** self.size_adr_n - 4
        #     num_toffolis_per_type = (num_toffolis, 0)
        #
        # elif self.decomposition_type == ToffoliDecompType.ONE_ANCILLA_TDEPTH_2:
        #     num_cnots_dec_per_type = (10, 0)
        #     num_toffolis = 3 * 2 ** self.size_adr_n - 4
        #     num_toffolis_per_type = (num_toffolis, 0)
        #
        # elif self.decomposition_type == ToffoliDecompType.FOUR_ANCILLA_TDEPTH_1_A:
        #     num_cnots_dec_per_type = (16, 0)
        #     num_toffolis = 3 * 2 ** self.size_adr_n - 4
        #     num_toffolis_per_type = (num_toffolis, 0)
        #
        # elif self.decomposition_type == ToffoliDecompType.FOUR_ANCILLA_TDEPTH_1_B:
        """
        A bit misleading, because this decomposition is not entirely used 
        alone, but in conjunction with the FOUR_ANCILLA_TDEPTH_1_A
        
        The following formula_from_paper is because:
        -> we received notes from Olivia on the 11 November 2019
        
        Theoretically, FOUR_ANCILLA_TDEPTH_1_B has 18 CNOTs, but after
        cancelling out, only 12 remain...and 6 which are added (see below)
        """
            # num_cnots_dec_per_type = (16, 12)
            #
            # num_toffolis_fan = 2 ** (self.size_adr_n + 1) - 4
            # num_toffolis_mem = 2 ** self.size_adr_n
            # num_toffolis_per_type = (num_toffolis_fan, num_toffolis_mem)

        # See naming from arxiv: 1502.03450
        num_coupling_nodes = 2 * 2 ** self.size_adr_n

        formula_from_paper = 0
        for elem in zip(num_toffolis_per_type, toff_dec_cnot_count_per_type):
            formula_from_paper += elem[0] * elem[1]
        formula_from_paper += num_coupling_nodes

        # if self.decomposition_type == ToffoliDecompType.FOUR_ANCILLA_TDEPTH_1_B:
        #     """
        #     The mixture leaves 6 CNOTS. See Olivia notes.
        #     """
        #     formula_from_paper += 6
        """
        special cases
        """
        num_of_canceled_cnot = 0
        if (self.decomp_scenario.dec_mem == ToffoliDecompType.FOUR_ANCILLA_TDEPTH_1_B):
            num_of_canceled_cnot = 6*(2 ** self.size_adr_n-1)
        formula_from_paper -= num_of_canceled_cnot
        nr_cnot = count_cnot_of_circuit(self.circuit)
        # print("have {} == {} should".format(nr_cnot, formula_from_paper))
        verif = (formula_from_paper == nr_cnot)
        return verif

