from enum import Enum, auto

from utils.counting_utils import *
import utils.clifford_t_utils as ctu
import utils.misc_utils as miscutils

class MPMCTDecompType(Enum):
    NO_DECOMP = auto()
    ALLOW_DECOMP = auto()

class MPMCTDecomposition():

    def __init__(self, qubits, decomposition_type, search, target):
        self.decomposition_type = decomposition_type
        self.qubits = qubits
        self.search = search
        self.n = len(qubits)
        self.target = target

    def decompose(self, new_ancilla_index = -1):
        """
        Decomposition Figure 4.d from
        https://nabdessaied.github.io/assets/pdf/p10.pdf

        Is uses the parallel decomposition
        :return:
        """

        barenco_ancillae = None
        iz_decomp_ancilla = None

        # Naming convention
        # XXX_S_ID means
        # XXX is name,
        # S = sequential, if integer then parallel
        # ID = index if parallel (S is integer)

        if new_ancilla_index >= 0:
            # A new ancilla each time
            barenco_ancillae = [cirq.NamedQubit("barenco_ancilla_{}_{}".format(new_ancilla_index, i))
                                for i in range(self.n - 2)]

            iz_decomp_ancilla = cirq.NamedQubit("iz_d_{}".format(new_ancilla_index))

        elif new_ancilla_index < 0:
            # Use the same ancilla
            barenco_ancillae = [cirq.NamedQubit("barenco_ancilla_s_{}" + str(i))
                                for i in range(self.n - 2)]

            iz_decomp_ancilla = cirq.NamedQubit("iz_d_s")

        return self.MPMCT_decomp(barenco_ancillae, iz_decomp_ancilla)

    def MPMCT_decomp(self, barenco_ancillae, ancilla):
        """
        Parallel version of decomposition()
        :param step: Parameter to guarantee that each MPMCT has its own ancilla
        :return:
        """

        # The moments of the decomposition
        moments = []
        # # Generate the ancilla wires starting with names prefixed by "step"
        # barenco_ancillae = [cirq.NamedQubit("barenco_ancilla_{}_{}".format(step, i))
        #                 for i in range(self.n - 2) ]

        # Get the integer bits of the controls/search by padding to n bits
        # binary = [int(x) for x in bin(self.search)[2:].zfill(self.n)]
        binary = [int(x) for x in miscutils.my_bin(self.search, self.n)]

        if self.decomposition_type == MPMCTDecompType.NO_DECOMP:
            # No decomposition
            moments.append(cirq.Moment([cirq.ops.ControlledOperation(self.qubits[:self.n],
                                                         cirq.ops.X.on(self.target),
                                                         binary)]))
        elif self.decomposition_type == MPMCTDecompType.ALLOW_DECOMP:
            # Decomposition with iZ and iwZ

            praet_guard = []
            praet_guard.append(cirq.Moment([cirq.H(self.target)]))
            praet_guard += self.iZ_decomp(
                ctrlQbts=[self.qubits[-1], self.target],
                trgtQbt = barenco_ancillae[-1],
                ctrlVlus=[binary[-1], 1],
                ancilla = ancilla)

            # Number of iwZ in the first half of the circuit
            caesar_half = []
            d = self.n - 2
            for i in range(1, d):
                caesar_half.append(cirq.Moment([cirq.H(barenco_ancillae[d - i])]))
                caesar_half += self.iwZ_decomp(
                    ctrlQbts = [self.qubits[self.n - i - 1], barenco_ancillae[d - i]],
                    trgtQbt = barenco_ancillae[d - i - 1],
                    # TODO: configure bits
                    ctrlVlus = [binary[self.n - i - 1], 1])

            # Add Hadamard to trgtQbt: CCX -> CCZ
            iz_moment = [cirq.Moment([cirq.H(barenco_ancillae[0])])]
            iz_moment += self.iZ_decomp(
                ctrlQbts=[self.qubits[0], self.qubits[1]],
                trgtQbt = barenco_ancillae[0], ctrlVlus=[binary[0], binary[1]],
                ancilla = ancilla)
            # Undo previous Hadamard to trgtQbt
            iz_moment += [cirq.Moment([cirq.H(barenco_ancillae[0])])]

            # caesar = caesar_half + iz_moment + caesar_half[::-1]
            caesar = caesar_half + iz_moment + ctu.reverse_moments(caesar_half)

            # caesar_plus_guards = praet_guard + caesar + praet_guard[::-1]
            caesar_plus_guards = praet_guard + caesar + ctu.reverse_moments(praet_guard)

            # Brutus has a dagger. It is Caesar reversed.
            # brutus = caesar[::-1]
            brutus = ctu.reverse_moments(caesar)

            moments = caesar_plus_guards + brutus

        return moments

    def iZ_decomp(self, ctrlQbts, trgtQbt, ctrlVlus, ancilla):
        """
            Each iZ decomposition has its own ancilla
        :param ctrlQbts: qubits for control
        :param trgtQbt: target qubit
        :param ctrlVlus: bits for how to control the qubis - affects the T gates
        :param step: integer to start counting the ancilla
        :return: a list of Cirq Moments
        """

        encoder = [cirq.Moment([cirq.ops.CX(trgtQbt, ctrlQbts[1]),
                    cirq.ops.CX(ctrlQbts[0], ancilla)]),
                   cirq.Moment([cirq.ops.CX(trgtQbt, ctrlQbts[0]),
                    cirq.ops.CX(ctrlQbts[1], ancilla)])]

        dagger = [0, 0, 0, 0]
        if ctrlVlus == [0, 0]:
            dagger = [ 1,  1,  1,  1]
        elif ctrlVlus == [0, 1]:
            dagger = [ 1, -1,  1, -1]
        elif ctrlVlus == [1, 0]:
            dagger = [-1,  1,  1, -1]
        elif ctrlVlus == [1, 1]:
            dagger = [-1, -1,  1,  1]

        parallel_t_gates = [cirq.Moment([
            (cirq.T ** dagger[0])(ctrlQbts[0]),
            (cirq.T ** dagger[1])(ctrlQbts[1]),
            (cirq.T ** dagger[2])(trgtQbt),
            (cirq.T ** dagger[3])(ancilla)])]

        # decoder = encoder[::-1]
        decoder = ctu.reverse_moments(encoder)

        moments = encoder + parallel_t_gates + decoder

        return moments

    def iwZ_decomp(self, ctrlQbts, trgtQbt, ctrlVlus):
        """
        Decomposition of iwZ from
        https://nabdessaied.github.io/assets/pdf/p10.pdf
        :param ctrlQbts:
        :param trgtQbt:
        :param ctrlVlus:
        :return:
        """
        encoder =  [
                    cirq.Moment([cirq.ops.CX(trgtQbt, ctrlQbts[0])]),
                    cirq.Moment([cirq.ops.CX(ctrlQbts[1], trgtQbt)]),
                    cirq.Moment([cirq.ops.CX(ctrlQbts[0], ctrlQbts[1])])
        ]

        dagger = [0, 0, 0]
        if ctrlVlus == [0, 0]:
            dagger = [-1, -1, -1]
        elif ctrlVlus == [0, 1]:
            dagger = [-1, 1, 1]
        elif ctrlVlus == [1, 0]:
            dagger = [1, 1, -1]
        elif ctrlVlus == [1, 1]:
            dagger = [1, -1, 1]

        parallel_t_gates = [cirq.Moment(
                    [(cirq.T ** dagger[0])(ctrlQbts[0]),
                    (cirq.T ** dagger[1])(ctrlQbts[1]),
                    (cirq.T ** dagger[2])(trgtQbt)])]

        # decoder = encoder[::-1]
        decoder = ctu.reverse_moments(encoder)

        moments = encoder + parallel_t_gates + decoder

        return moments


 # def BarencoDecomposition(self):
    #     """
    #     Barenco decomposition from https://arxiv.org/abs/quant-ph/9503016
    #     :return:
    #     """
    #     moments = []
    #     ancillae = [cirq.NamedQubit("ancilla"+str(i)) for i in range(self.n-2)]
    #     binary = list(bin(self.search)[2:].zfill(self.n))
    #     binary = [int(x) for x in binary]
    #     if self.decomposition_type == -1:
    #         moments.append([cirq.ops.ControlledOperation(self.qubits[:self.n], cirq.ops.X.on(self.target), binary)])
    #     elif self.decomposition_type == 0:
    #         d = self.n-2
    #         moments.append(cirq.ops.ControlledOperation(
    #             [self.qubits[-1], ancillae[-1]], cirq.ops.X.on(self.target), [binary[-1], 1]))
    #         for i in range(1, d):
    #             moments.append([cirq.ops.ControlledOperation(
    #                 [self.qubits[self.n-i-1], ancillae[d-i-1]], cirq.X(ancillae[d-i]), [binary[self.n-i-1], 1])])
    #         moment = [[cirq.ops.ControlledOperation(
    #             [self.qubits[0], self.qubits[1]], cirq.X(ancillae[0]), [binary[0], binary[1]])]]
    #         moments += moment + moments[::-1] + moments[1:] + moment + moments[::-1][1:]
    #     return moments