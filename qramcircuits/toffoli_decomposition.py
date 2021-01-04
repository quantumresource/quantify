from enum import Enum, auto

from utils.counting_utils import *
import utils.clifford_t_utils as ctu

class ToffoliDecompType(Enum):
    #
    # If decomps are added, for the moment, update number_of_ancilla() below
    #
    NO_DECOMP = auto()

    # Equation 3 from arxiv:1210.0974v2
    ZERO_ANCILLA_TDEPTH_3 = auto()

    #Decomp from Thaplyal
    ZERO_ANCILLA_TDEPTH_3_DEPTH_10 = auto()

    # Figure 3 from arxiv:1303.2042
    ONE_ANCILLA_TDEPTH_2 = auto()

    # Figure 1 from from arxiv:1210.0974v2
    FOUR_ANCILLA_TDEPTH_1_A = auto()

    # Figure 6 from from arxiv:1303.2042
    FOUR_ANCILLA_TDEPTH_1_B = auto()
    FOUR_ANCILLA_TDEPTH_1_B_P = auto()
    FOUR_ANCILLA_TDEPTH_1_B_PP = auto()

    # arxiv:1709.06648 Figure 3
    ZERO_ANCILLA_TDEPTH_2_COMPUTE = auto()

    # arxiv:1709.06648 Figure 3
    ZERO_ANCILLA_TDEPTH_0_UNCOMPUTE = auto()

    FOUR_ANCILLA_TDEPTH_1_COMPUTE = auto()

    # experimental
    ONE_ANCILLA_TDEPTH_4 = auto()
    ZERO_ANCILLA_TDEPTH_4 = auto()
    ZERO_ANCILLA_TDEPTH_4_COMPUTE = auto()

    # Relative phase Toffoli (Figure 18/19 from arxiv:2010.00255)
    ZERO_ANCILLA_CNOT_3 = auto
    ZERO_ANCILLA_CNOT_3_INV = auto
    
    ZERO_ANCILLA_CNOT_4 = auto
    ZERO_ANCILLA_CNOT_4_INV = auto


class ToffoliDecomposition():

    def __init__(self, decomposition_type,
                 qubits = None,
                 target_qubit = None):

        self.decomp_type = decomposition_type

        self.qubits = qubits
        if self.qubits is None:
            # This is used mostly when the decompositions are analysed
            # for resource counts
            self.qubits = [
                cirq.NamedQubit("fake_0"),
                cirq.NamedQubit("fake_1"),
                cirq.NamedQubit("fake_2")
            ]


        self._ancilla = [
                cirq.NamedQubit("toff_a0"),
                cirq.NamedQubit("toff_a1"),
                cirq.NamedQubit("toff_a2"),
                cirq.NamedQubit("toff_a3")
        ]

        self.target_qubit = target_qubit
        # If the target qubit is not specified, then it is the third one
        # from the list
        if self.target_qubit is None:
            self.target_qubit = self.qubits[2]

    @property
    def ancilla(self):
        return self._ancilla

    @staticmethod
    def construct_decomposed_moments(subcircuit,
                                     toff_decomp,
                                     qubit_permutation = [0, 1, 2]):
        decomp_moments = []

        for moment in subcircuit:
            moment_w_toffolis = cirq.Moment()
            moment_wo_toffolis = cirq.Moment()

            # Extract from the moments the Toffoli gates
            for op in moment:
                if op.gate != cirq.ops.TOFFOLI:
                    moment_wo_toffolis = moment_wo_toffolis.with_operation(op)
                else:
                    moment_w_toffolis = moment_w_toffolis.with_operation(op)


            moments_toffoli_decomps = []
            for toff in moment_w_toffolis:
                moments_toffoli_decomps += \
                    ToffoliDecomposition(toff_decomp, [
                                        toff.qubits[qubit_permutation[0]],
                                        toff.qubits[qubit_permutation[1]],
                                        toff.qubits[qubit_permutation[2]]
                                    ],
                                    target_qubit=toff.qubits[2]).decomposition()

            # Add the moment without Toffolis
            if len(moment_wo_toffolis) > 0:
                decomp_moments.append(moment_wo_toffolis)

            # Add the moments corresponding to the Toffoli decompositions
            decomp_moments += moments_toffoli_decomps

        return decomp_moments

    def decomposition(self):
        moments = []

        if self.decomp_type == ToffoliDecompType.NO_DECOMP:

            # No decomposition at all



            moments.append(
                    cirq.TOFFOLI.on(*self.qubits)
            )
        elif self.decomp_type == ToffoliDecompType.ZERO_ANCILLA_TDEPTH_3:
            # Equation 3 from arxiv:1210.0974v2
            # No ancilla, T-depth 3
            moments += [
                cirq.Moment([cirq.H.on(self.target_qubit)]),
                cirq.Moment([cirq.T.on(self.qubits[0])**-1,
                cirq.T.on(self.qubits[1]),
                cirq.T.on(self.qubits[2])]),
                cirq.Moment([cirq.CNOT.on(self.qubits[0], self.qubits[1])]),
                cirq.Moment([cirq.CNOT.on(self.qubits[2], self.qubits[0])]),
                cirq.Moment([(cirq.T**-1).on(self.qubits[0]),
                cirq.CNOT.on(self.qubits[1], self.qubits[2])]),
                cirq.Moment([cirq.CNOT.on(self.qubits[1], self.qubits[0])]),
                cirq.Moment([cirq.T.on(self.qubits[0]) ** -1,
                cirq.T.on(self.qubits[1]) ** -1,
                cirq.T.on(self.qubits[2])]),
                cirq.Moment([cirq.CNOT.on(self.qubits[2], self.qubits[0])]),
                cirq.Moment([cirq.S.on(self.qubits[0]),
                cirq.CNOT.on(self.qubits[1], self.qubits[2])]),
                cirq.Moment([cirq.CNOT.on(self.qubits[0], self.qubits[1]),
                cirq.H.on(self.target_qubit)])
            ]
            #strategy=cirq.InsertStrategy.NEW_THEN_INLINE)
        elif self.decomp_type == ToffoliDecompType.ONE_ANCILLA_TDEPTH_2:
            # Figure 3 from arxiv:1303.2042
            moments += [
                cirq.Moment([cirq.H.on(self.target_qubit)]),
                cirq.Moment([cirq.CNOT.on(self.qubits[0], self.qubits[2])]),
                cirq.Moment([cirq.CNOT.on(self.qubits[2], self.ancilla[0])]),
                cirq.Moment([cirq.CNOT.on(self.qubits[1], self.ancilla[0])]),
                cirq.Moment([cirq.T.on(self.ancilla[0])**-1,
                cirq.T.on(self.qubits[2]),
                cirq.T.on(self.qubits[1]) ** -1,
                cirq.T.on(self.qubits[0]) ** -1]),
                cirq.Moment([cirq.CNOT.on(self.qubits[1], self.ancilla[0])]),
                cirq.Moment([cirq.CNOT.on(self.qubits[2], self.ancilla[0])]),
                cirq.Moment([cirq.CNOT.on(self.qubits[0], self.qubits[2])]),
                cirq.Moment([cirq.CNOT.on(self.qubits[1], self.qubits[0])]),
                cirq.Moment([cirq.CNOT.on(self.qubits[2], self.qubits[1])]),
                cirq.Moment([cirq.T.on(self.qubits[2]) ** -1,
                cirq.T.on(self.qubits[1]),
                cirq.T.on(self.qubits[0])]),
                cirq.Moment([cirq.CNOT.on(self.qubits[2], self.qubits[1])]),
                cirq.Moment([cirq.CNOT.on(self.qubits[1], self.qubits[0]),
                cirq.H.on(self.target_qubit)])

            ] #strategy=cirq.InsertStrategy.NEW_THEN_INLINE)

        elif self.decomp_type == ToffoliDecompType.FOUR_ANCILLA_TDEPTH_1_A:
            # Figure 1 from from arxiv:1210.0974v2
            # Four ancilla, T-depth 1
            encoder = [
                cirq.Moment([cirq.H.on(self.target_qubit),
                cirq.CNOT.on(self.qubits[1], self.ancilla[2]),
                cirq.CNOT.on(self.qubits[0], self.ancilla[0])]),
                cirq.Moment([cirq.CNOT.on(self.qubits[1], self.ancilla[1]),
                cirq.CNOT.on(self.qubits[2], self.ancilla[2]),
                cirq.CNOT.on(self.ancilla[0], self.ancilla[3])]),
                cirq.Moment([cirq.CNOT.on(self.qubits[0], self.ancilla[1]),
                cirq.CNOT.on(self.qubits[2], self.ancilla[3]),
                cirq.CNOT.on(self.ancilla[2], self.ancilla[0])])
            ]
            # in order to have parallel CNOTs
            moments += encoder
            # in order to have sequential CNOTs
            # self.decomposition.append(encoder, strategy=cirq.InsertStrategy.NEW)

            moments += [
                cirq.Moment([cirq.T.on(self.qubits[0]),
                cirq.T.on(self.qubits[1]),
                cirq.T.on(self.qubits[2]),
                cirq.T.on(self.ancilla[0]),
                cirq.T.on(self.ancilla[1])**-1,
                cirq.T.on(self.ancilla[2])**-1,
                cirq.T.on(self.ancilla[3])**-1])
            ]

            # in order to have parallel CNOTs
            # moments += encoder[::-1]
            moments += ctu.reverse_moments(encoder)

            # in order to have sequential CNOTs
            # self.decomposition.append(encoder[::-1], strategy=cirq.InsertStrategy.NEW)
        elif self.decomp_type == ToffoliDecompType.FOUR_ANCILLA_TDEPTH_1_B:
            # Figure 6 from from arxiv:1303.2042
            # TODO: replace [] with cirq.Moment
            encoder = [
                cirq.Moment([cirq.H.on(self.target_qubit)]),
                 cirq.Moment([cirq.CNOT.on(self.qubits[2], self.ancilla[3])]),
                 cirq.Moment([cirq.CNOT.on(self.qubits[2], self.ancilla[1])]),
                cirq.Moment([cirq.CNOT.on(self.qubits[2], self.ancilla[0])]),
                 cirq.Moment([cirq.CNOT.on(self.qubits[1], self.ancilla[2])]),
                 cirq.Moment([cirq.CNOT.on(self.qubits[1], self.ancilla[1])]),
                cirq.Moment([cirq.CNOT.on(self.qubits[1], self.ancilla[0])]),
                 cirq.Moment([cirq.CNOT.on(self.qubits[0], self.ancilla[2])]),
                 cirq.Moment([cirq.CNOT.on(self.qubits[0], self.ancilla[1])]),
                cirq.Moment([cirq.CNOT.on(self.qubits[0], self.qubits[2])])
            ]
            # in order to have parallel CNOTs
            moments += encoder
            # in order to have sequential CNOTs
            # self.decomposition.append(encoder, strategy=cirq.InsertStrategy.NEW)

            moments += [
                cirq.Moment([cirq.T.on(self.qubits[0])**-1,
                 cirq.T.on(self.qubits[1])**-1,
                 cirq.T.on(self.qubits[2]),
                 cirq.T.on(self.ancilla[0]),
                 cirq.T.on(self.ancilla[1])**-1,
                 cirq.T.on(self.ancilla[2]),
                 cirq.T.on(self.ancilla[3])**-1])
            ]

            # in order to have parallel CNOTs
            # moments += encoder[::-1]
            moments += ctu.reverse_moments(encoder)
        elif self.decomp_type == ToffoliDecompType.FOUR_ANCILLA_TDEPTH_1_B_P:
            # Figure 6 from from arxiv:1303.2042
            # TODO: replace [] with cirq.Moment
            encoder = [
                cirq.Moment([cirq.H.on(self.target_qubit)]),
                cirq.Moment([cirq.CNOT.on(self.qubits[2], self.ancilla[3])]),
                cirq.Moment([cirq.CNOT.on(self.qubits[2], self.ancilla[1])]),
                cirq.Moment([cirq.CNOT.on(self.qubits[2], self.ancilla[0])]),

                cirq.Moment([cirq.T.on(self.qubits[0]) ** -1,
                             cirq.T.on(self.qubits[1]) ** -1,
                             cirq.T.on(self.ancilla[3]) ** -1]),

                cirq.Moment([cirq.CNOT.on(self.qubits[1], self.ancilla[2])]),
                cirq.Moment([cirq.CNOT.on(self.qubits[1], self.ancilla[1])]),

                cirq.Moment([cirq.CNOT.on(self.qubits[1], self.ancilla[0])]),
                cirq.Moment([cirq.T.on(self.ancilla[0])]),
                cirq.Moment([cirq.CNOT.on(self.qubits[1], self.ancilla[0])]),

                cirq.Moment([cirq.CNOT.on(self.qubits[0], self.ancilla[1])]),
                cirq.Moment([cirq.T.on(self.ancilla[1])**-1]),
                cirq.Moment([cirq.CNOT.on(self.qubits[0], self.ancilla[1])]),

                cirq.Moment([cirq.CNOT.on(self.qubits[0], self.ancilla[2])]),
                cirq.Moment([cirq.T.on(self.ancilla[2])]),
                cirq.Moment([cirq.CNOT.on(self.qubits[0], self.ancilla[2])]),

                cirq.Moment([cirq.CNOT.on(self.qubits[0], self.qubits[2])]),
                cirq.Moment([cirq.T.on(self.qubits[2])]),
                cirq.Moment([cirq.CNOT.on(self.qubits[0], self.qubits[2])]),

                cirq.Moment([cirq.CNOT.on(self.qubits[1], self.ancilla[1])]),
                cirq.Moment([cirq.CNOT.on(self.qubits[1], self.ancilla[2])]),

                cirq.Moment([cirq.CNOT.on(self.qubits[2], self.ancilla[0])]),
                cirq.Moment([cirq.CNOT.on(self.qubits[2], self.ancilla[1])]),
                cirq.Moment([cirq.CNOT.on(self.qubits[2], self.ancilla[3])]),
                cirq.Moment([cirq.H.on(self.target_qubit)])
            ]

            moments = encoder
        elif self.decomp_type == ToffoliDecompType.FOUR_ANCILLA_TDEPTH_1_B_PP:
            # Figure 6 from from arxiv:1303.2042
            # TODO: replace [] with cirq.Moment
            # Figure 6 from from arxiv:1303.2042
            # TODO: replace [] with cirq.Moment
            encoder = [
                cirq.Moment([cirq.H.on(self.target_qubit)]),
                cirq.Moment([cirq.CNOT.on(self.qubits[2], self.ancilla[3])]),
                cirq.Moment([cirq.CNOT.on(self.qubits[2], self.ancilla[1])]),
                cirq.Moment([cirq.CNOT.on(self.qubits[2], self.ancilla[0])]),

                cirq.Moment([cirq.T.on(self.qubits[0]) ** -1,
                             cirq.T.on(self.qubits[1]) ** -1,
                             cirq.T.on(self.ancilla[3]) ** -1]),

                cirq.Moment([cirq.CNOT.on(self.qubits[1], self.ancilla[2])]),
                cirq.Moment([cirq.CNOT.on(self.qubits[1], self.ancilla[1])]),

                cirq.Moment([cirq.CNOT.on(self.ancilla[0], self.qubits[1])]),
                cirq.Moment([cirq.T.on(self.qubits[1])]),
                cirq.Moment([cirq.CNOT.on(self.ancilla[0], self.qubits[1])]),

                cirq.Moment([cirq.CNOT.on(self.ancilla[1], self.qubits[0])]),
                cirq.Moment([cirq.T.on(self.qubits[0]) ** -1]),
                cirq.Moment([cirq.CNOT.on(self.ancilla[1], self.qubits[0])]),

                cirq.Moment([cirq.CNOT.on(self.ancilla[2], self.qubits[0])]),
                cirq.Moment([cirq.T.on(self.qubits[0])]),
                cirq.Moment([cirq.CNOT.on(self.ancilla[2], self.qubits[0])]),

                cirq.Moment([cirq.CNOT.on(self.qubits[2], self.qubits[0])]),
                cirq.Moment([cirq.T.on(self.qubits[0])]),
                cirq.Moment([cirq.CNOT.on(self.qubits[2], self.qubits[0])]),

                cirq.Moment([cirq.CNOT.on(self.qubits[1], self.ancilla[1])]),
                cirq.Moment([cirq.CNOT.on(self.qubits[1], self.ancilla[2])]),

                cirq.Moment([cirq.CNOT.on(self.qubits[2], self.ancilla[0])]),
                cirq.Moment([cirq.CNOT.on(self.qubits[2], self.ancilla[1])]),
                cirq.Moment([cirq.CNOT.on(self.qubits[2], self.ancilla[3])]),
                cirq.Moment([cirq.H.on(self.target_qubit)])
            ]

            moments = encoder

        elif self.decomp_type == ToffoliDecompType.ZERO_ANCILLA_TDEPTH_3_DEPTH_10:
            moments = [
                cirq.Moment([cirq.H(self.qubits[2])]),
                cirq.Moment([cirq.T(self.qubits[0]), cirq.T(self.qubits[1]), cirq.T(self.qubits[2])]),
                cirq.Moment([cirq.CNOT(self.qubits[1], self.qubits[0])]),
                cirq.Moment([cirq.CNOT(self.qubits[2], self.qubits[1])]),
                cirq.Moment([cirq.CNOT(self.qubits[0], self.qubits[2]), cirq.T(self.qubits[1])**-1]),
                cirq.Moment([cirq.CNOT(self.qubits[0], self.qubits[1])]),
                cirq.Moment([cirq.T(self.qubits[0])**-1, cirq.T(self.qubits[1])**-1, cirq.T(self.qubits[2])**-1]),
                cirq.Moment([cirq.CNOT(self.qubits[2], self.qubits[1])]),
                cirq.Moment([cirq.CNOT(self.qubits[0], self.qubits[2])]),
                cirq.Moment([cirq.CNOT(self.qubits[1], self.qubits[0]), cirq.H(self.qubits[2])])

            ]

        elif self.decomp_type == ToffoliDecompType.ZERO_ANCILLA_TDEPTH_2_COMPUTE:
            # upper part Figure 3 from 1709.06648
            moments = [
                # TODO: H and T in order to emulate T-state initialisation
                # TODO: Correct depth of circuit, because this will increase by two each time
                cirq.Moment([cirq.H.on(self.qubits[2])]),
                cirq.Moment([cirq.T.on(self.qubits[2])]),
                cirq.Moment([cirq.CNOT.on(self.qubits[0], self.qubits[2])]),
                cirq.Moment([cirq.CNOT.on(self.qubits[1], self.qubits[2])]),
                # TODO: Replace following two with single control -multiple target CNOT
                cirq.Moment([cirq.CNOT.on(self.qubits[2], self.qubits[0])]),
                cirq.Moment([cirq.CNOT.on(self.qubits[2], self.qubits[1])]),
                cirq.Moment([
                    cirq.ops.T.on(self.qubits[0])**-1,
                    cirq.ops.T.on(self.qubits[1])**-1,
                    cirq.ops.T.on(self.qubits[2])
                ]),
                # TODO: Replace following two with single control -multiple target CNOT
                cirq.Moment([cirq.CNOT.on(self.qubits[2], self.qubits[0])]),
                cirq.Moment([cirq.CNOT.on(self.qubits[2], self.qubits[1])]),

                cirq.Moment([cirq.H.on(self.qubits[2])]),
                cirq.Moment([cirq.S.on(self.qubits[2])])
            ]

        elif self.decomp_type == ToffoliDecompType.ZERO_ANCILLA_TDEPTH_0_UNCOMPUTE:
            # lower part Figure 3 from 1709.06648
            # Measurements are implicit, and we assume worst case where all
            # the CZ have to be implemented
            moments = [
                cirq.Moment([cirq.H.on(self.qubits[2]), cirq.H.on(self.qubits[0])]),
                cirq.Moment([cirq.CX.on(self.qubits[1], self.qubits[0])]),
                cirq.Moment([cirq.H.on(self.qubits[0])]),
            ]
        elif self.decomp_type == ToffoliDecompType.FOUR_ANCILLA_TDEPTH_1_COMPUTE:
            # Figure 3 from https://arxiv.org/pdf/1212.5069.pdf
            # Figure 6 from from arxiv:1303.2042
            # TODO: replace [] with cirq.Moment
            encoder = [
                cirq.Moment([cirq.H.on(self.qubits[2])]),
                cirq.Moment([cirq.CNOT.on(self.qubits[0], self.ancilla[0])]),
                cirq.Moment([cirq.CNOT.on(self.qubits[0], self.ancilla[3])]),
                cirq.Moment([cirq.CNOT.on(self.qubits[1], self.ancilla[1])]),
                cirq.Moment([cirq.CNOT.on(self.qubits[1], self.ancilla[3])]),
                cirq.Moment([cirq.CNOT.on(self.qubits[2], self.ancilla[0])]),
                cirq.Moment([cirq.CNOT.on(self.qubits[2], self.ancilla[1])]),
                cirq.Moment([cirq.CNOT.on(self.qubits[2], self.ancilla[2])]),
                cirq.Moment([cirq.CNOT.on(self.qubits[2], self.ancilla[3])]),
            ]
            # in order to have parallel CNOTs
            moments += encoder

            moments += [
                cirq.Moment([cirq.T.on(self.ancilla[0])** -1,
                             cirq.T.on(self.ancilla[1]) ** -1,
                             cirq.T.on(self.ancilla[2]),
                             cirq.T.on(self.ancilla[3])])
            ]

            # in order to have parallel CNOTs
            # moments += encoder[::-1]
            moments += ctu.reverse_moments(encoder)

            moments += [ cirq.Moment([cirq.S.on(self.qubits[2])]) ]

        elif self.decomp_type == ToffoliDecompType.ONE_ANCILLA_TDEPTH_4:
            # This is a CCZ, and the Hadamard can be placed anywhere,
            # but by Cirq definition, the last qubit is the target

            moments = [
                cirq.Moment([cirq.H.on(self.target_qubit)]),

                cirq.Moment([cirq.T.on(self.qubits[0]),
                             cirq.T.on(self.qubits[1]),
                             cirq.T.on(self.qubits[2])]),

                cirq.Moment([cirq.CNOT(self.qubits[2], self.qubits[0])]),
                cirq.Moment([cirq.CNOT(self.qubits[2], self.ancilla[0])]),
                cirq.Moment([cirq.T.on(self.qubits[0]) ** -1]),

                cirq.Moment([cirq.CNOT(self.qubits[1], self.qubits[0])]),
                cirq.Moment([cirq.CNOT(self.qubits[1], self.ancilla[0])]),
                cirq.Moment([cirq.T.on(self.qubits[0]),
                             cirq.T.on(self.ancilla[0]) ** -1]),

                cirq.Moment([cirq.CNOT(self.qubits[2], self.qubits[0])]),
                cirq.Moment([cirq.CNOT(self.qubits[2], self.ancilla[0])]),
                cirq.Moment([cirq.T.on(self.qubits[0]) ** -1]),

                cirq.Moment([cirq.CNOT(self.qubits[1], self.qubits[0])]),
                cirq.Moment([cirq.CNOT(self.qubits[1], self.ancilla[0])]),

                cirq.Moment([cirq.H.on(self.target_qubit)])
            ]

            return moments
        elif self.decomp_type == ToffoliDecompType.ZERO_ANCILLA_TDEPTH_4:
            # This is a CCZ, and the Hadamard can be placed anywhere,
            # but by Cirq definition, the last qubit is the target

            moments = [
                cirq.Moment([cirq.H.on(self.target_qubit)]),

                cirq.Moment([cirq.T.on(self.qubits[0]),
                             cirq.T.on(self.qubits[1]),
                             cirq.T.on(self.qubits[2])]),

                cirq.Moment([cirq.CNOT(self.qubits[2], self.qubits[0])]),
                cirq.Moment([cirq.T.on(self.qubits[0]) ** -1]),

                cirq.Moment([cirq.CNOT(self.qubits[1], self.qubits[0])]),
                cirq.Moment([cirq.CNOT(self.qubits[1], self.qubits[2])]),
                cirq.Moment([cirq.T.on(self.qubits[0]),
                             cirq.T.on(self.qubits[2]) ** -1]),

                cirq.Moment([cirq.CNOT(self.qubits[1], self.qubits[2])]),

                cirq.Moment([cirq.CNOT(self.qubits[2], self.qubits[0])]),
                cirq.Moment([cirq.T.on(self.qubits[0]) ** -1]),

                cirq.Moment([cirq.CNOT(self.qubits[1], self.qubits[0])]),

                cirq.Moment([cirq.H.on(self.target_qubit)])
            ]

            return moments

        elif self.decomp_type == ToffoliDecompType.ZERO_ANCILLA_TDEPTH_4_COMPUTE:
            # This is a logical AND, and the Hadamard cannot be placed anywhere,
            # TODO: Check where this is placed

            moments = [
                cirq.Moment([cirq.H.on(self.target_qubit)]),

                cirq.Moment([cirq.T.on(self.qubits[2])]),

                cirq.Moment([cirq.CNOT(self.qubits[0], self.qubits[2])]),
                cirq.Moment([cirq.T.on(self.qubits[2]) ** -1]),

                cirq.Moment([cirq.CNOT(self.qubits[1], self.qubits[2])]),
                cirq.Moment([cirq.T.on(self.qubits[2])]),

                cirq.Moment([cirq.CNOT(self.qubits[0], self.qubits[2])]),
                cirq.Moment([cirq.T.on(self.qubits[2]) ** -1]),

                cirq.Moment([cirq.CNOT(self.qubits[1], self.qubits[2])]),

                cirq.Moment([cirq.H.on(self.target_qubit)])
            ]

            return moments

        elif self.decomp_type == ToffoliDecompType.ZERO_ANCILLA_CNOT_3:
            moments = [
                cirq.H(self.target_qubit),
                cirq.T(self.target_qubit),
                cirq.CNOT(self.qubits[1], self.target_qubit),
                cirq.T(self.target_qubit) ** -1,
                cirq.CNOT(self.qubits[0], self.target_qubit),
                cirq.T(self.target_qubit),
                cirq.CNOT(self.qubits[1], self.target_qubit),
                cirq.T(self.target_qubit) ** -1,
                cirq.H(self.target_qubit)
            ]

        elif self.decomp_type == ToffoliDecompType.ZERO_ANCILLA_CNOT_3_INV:
            moments = [
                cirq.H(self.target_qubit),
                cirq.T(self.target_qubit),
                cirq.CNOT(self.qubits[1], self.target_qubit),
                cirq.T(self.target_qubit) ** -1,
                cirq.CNOT(self.qubits[0], self.target_qubit),
                cirq.T(self.target_qubit),
                cirq.CNOT(self.qubits[1], self.target_qubit),
                cirq.T(self.target_qubit) ** -1,
                cirq.H(self.target_qubit)
            ]

            return moments

        elif self.decomp_type == ToffoliDecompType.ZERO_ANCILLA_CNOT_4:
            moments = [
                cirq.H(self.target_qubit),
                cirq.CNOT(self.qubits[1], self.target_qubit),
                cirq.T(self.target_qubit) ** -1,
                cirq.CNOT(self.qubits[0], self.target_qubit),
                cirq.T(self.target_qubit),
                cirq.CNOT(self.qubits[1], self.target_qubit),
                cirq.T(self.target_qubit) ** -1,
                cirq.CNOT(self.qubits[0], self.target_qubit),
                cirq.T(self.target_qubit),
                cirq.H(self.target_qubit)
            ]

        elif self.decomp_type == ToffoliDecompType.ZERO_ANCILLA_CNOT_4_INV:
            moments = [
                cirq.H(self.target_qubit),
                cirq.T(self.target_qubit) ** -1,
                cirq.CNOT(self.qubits[0], self.target_qubit),
                cirq.T(self.target_qubit),
                cirq.CNOT(self.qubits[1], self.target_qubit),
                cirq.T(self.target_qubit) ** -1,
                cirq.CNOT(self.qubits[0], self.target_qubit),
                cirq.T(self.target_qubit),
                cirq.CNOT(self.qubits[1], self.target_qubit),
                cirq.H(self.target_qubit)
            ]

            return moments
        else:
            print("decomposition type must be a valid ToffoliDecompType")

        return moments


    @property
    def number_of_cnots(self):
        nr_cnot = count_cnot_of_circuit(self.decomposition())
        return nr_cnot

    @property
    def number_of_hadamards(self):
        # it is always 2
        nr_h = count_h_of_circuit(self.decomposition())

        # assert (nr_h == 2)
        return nr_h

    @property
    def number_of_t(self):
        # it is always 2
        nr_t = count_t_of_circuit(self.decomposition())

        # assert (nr_t == 7)
        return nr_t

    @property
    def depth(self):
        # the depth is the number of moments
        return len(self.decomposition())

    @property
    def t_depth(self):
        t_depth = count_t_depth_of_circuit(self.decomposition())
        return t_depth

    def number_of_ancilla(self):
        if self.decomp_type in [
            ToffoliDecompType.NO_DECOMP,
            ToffoliDecompType.ZERO_ANCILLA_TDEPTH_3,
            ToffoliDecompType.ZERO_ANCILLA_TDEPTH_2_COMPUTE,
            ToffoliDecompType.ZERO_ANCILLA_TDEPTH_0_UNCOMPUTE,
            ToffoliDecompType.ZERO_ANCILLA_TDEPTH_4,
            ToffoliDecompType.ZERO_ANCILLA_TDEPTH_4_COMPUTE
        ]:
            return 0

        elif self.decomp_type in [
            ToffoliDecompType.ONE_ANCILLA_TDEPTH_2,
            ToffoliDecompType.ONE_ANCILLA_TDEPTH_4
        ]:
            return 1

        elif self.decomp_type in [
            ToffoliDecompType.FOUR_ANCILLA_TDEPTH_1_A,
            ToffoliDecompType.FOUR_ANCILLA_TDEPTH_1_B,
            ToffoliDecompType.FOUR_ANCILLA_TDEPTH_1_B_P,
            ToffoliDecompType.FOUR_ANCILLA_TDEPTH_1_B_PP,
            ToffoliDecompType.FOUR_ANCILLA_TDEPTH_1_COMPUTE
        ]:
            return 4