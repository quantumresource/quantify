import cirq

from qramcircuits.toffoli_decomposition import ToffoliDecompType
import qramcircuits.bucket_brigade as bb

def test_decomp_one():

    for nr_qubits in range(3, 6):
        qubits = []
        for i in range(nr_qubits):
            qubits.append(cirq.NamedQubit("a" + str(i)))
        # bbcircuit = bb.BucketBrigade(qubits,
        #                              decomp_scenario=decomp_scenario)
        bbcircuit = bb.BucketBrigade(qubits, decomp_scenario=bb.BucketBrigadeDecompType(
                                         [ToffoliDecompType.NO_DECOMP,  # fan_in_decom
                                          ToffoliDecompType.NO_DECOMP,  # fan_out_decom
                                          ToffoliDecompType.NO_DECOMP], False))

        # #Verification
        assert (bbcircuit.verify_number_qubits() == True)
        assert (bbcircuit.verify_depth() == True)
        assert (bbcircuit.verify_T_count() == True)
        assert (bbcircuit.verify_T_depth() == True)
        assert (bbcircuit.verify_hadamard_count() == True)
        assert (bbcircuit.verify_cnot_count() == True)

def test_decomp_two():

    for nr_qubits in range(3, 6):
        qubits = []
        for i in range(nr_qubits):
            qubits.append(cirq.NamedQubit("a" + str(i)))

        bbcircuit = bb.BucketBrigade(qubits,
                                     decomp_scenario=bb.BucketBrigadeDecompType(
        [
            ToffoliDecompType.FOUR_ANCILLA_TDEPTH_1_A,    # fan_in_decomp
            ToffoliDecompType.FOUR_ANCILLA_TDEPTH_1_A,    # mem_decomp
            ToffoliDecompType.FOUR_ANCILLA_TDEPTH_1_A,    # fan_out_decomp
        ],
        False))

        # #Verification
        assert (bbcircuit.verify_number_qubits() == True)
        assert (bbcircuit.verify_depth() == True)
        assert (bbcircuit.verify_T_count() == True)
        assert (bbcircuit.verify_T_depth() == True)
        assert (bbcircuit.verify_hadamard_count() == True)
        assert (bbcircuit.verify_cnot_count() == True)

#
def test_decomp_three():

    for nr_qubits in range(2, 6):
        qubits = []
        for i in range(nr_qubits):
            qubits.append(cirq.NamedQubit("a" + str(i)))

        bbcircuit = bb.BucketBrigade(qubits,
                                     decomp_scenario=bb.BucketBrigadeDecompType(
                                         [
                                             ToffoliDecompType.ONE_ANCILLA_TDEPTH_2,  # fan_in_decomp
                                             ToffoliDecompType.ONE_ANCILLA_TDEPTH_2,  # mem_decomp
                                             ToffoliDecompType.ONE_ANCILLA_TDEPTH_2,  # fan_out_decomp
                                         ],
                                         False))

        # #Verification
        assert (bbcircuit.verify_number_qubits() == True)
        assert (bbcircuit.verify_depth() == True)
        assert (bbcircuit.verify_T_count() == True)
        assert (bbcircuit.verify_T_depth() == True)
        assert (bbcircuit.verify_hadamard_count() == True)
        assert (bbcircuit.verify_cnot_count() == True)

def test_decomp_five():

    for nr_qubits in range(2, 6):
        qubits = []
        for i in range(nr_qubits):
            qubits.append(cirq.NamedQubit("a" + str(i)))

        bbcircuit = bb.BucketBrigade(qubits,
                                     decomp_scenario=bb.BucketBrigadeDecompType(
                                         [
                                             ToffoliDecompType.FOUR_ANCILLA_TDEPTH_1_B,  # fan_in_decomp
                                             ToffoliDecompType.FOUR_ANCILLA_TDEPTH_1_B,  # mem_decomp
                                             ToffoliDecompType.FOUR_ANCILLA_TDEPTH_1_B,  # fan_out_decomp
                                         ],
                                         False))

        # #Verification
        assert (bbcircuit.verify_number_qubits() == True)
        assert (bbcircuit.verify_depth() == True)
        assert (bbcircuit.verify_T_count() == True)
        assert (bbcircuit.verify_T_depth() == True)
        assert (bbcircuit.verify_hadamard_count() == True)
        assert (bbcircuit.verify_cnot_count() == True)


def test_decomp_six():

    for nr_qubits in range(2, 6):
        qubits = []
        for i in range(nr_qubits):
            qubits.append(cirq.NamedQubit("a" + str(i)))

        bbcircuit = bb.BucketBrigade(qubits,
                                     decomp_scenario=bb.BucketBrigadeDecompType(
                                         [
                                             ToffoliDecompType.ZERO_ANCILLA_TDEPTH_3,  # fan_in_decomp
                                             ToffoliDecompType.ZERO_ANCILLA_TDEPTH_3,  # mem_decomp
                                             ToffoliDecompType.ZERO_ANCILLA_TDEPTH_3,  # fan_out_decomp
                                         ],
                                         False))

        # #Verification
        assert (bbcircuit.verify_number_qubits() == True)
        assert (bbcircuit.verify_depth() == True)
        assert (bbcircuit.verify_T_count() == True)
        assert (bbcircuit.verify_T_depth() == True)
        assert (bbcircuit.verify_hadamard_count() == True)
        assert (bbcircuit.verify_cnot_count() == True)

#
# def test_decomp_six():
#
#     for nr_qubits in range(2, 6):
#         qubits = []
#         for i in range(nr_qubits):
#             qubits.append(cirq.NamedQubit("a" + str(i)))
#
#         bbcircuit = bb.BucketBrigade(qubits,decomp_scenario=bb.BucketBrigadeDecompType(
#                                      [
#                                          ToffoliDecompType.ZERO_ANCILLA_TDEPTH_4_COMPUTE,  # fan_in_decomp
#                                          ToffoliDecompType.ZERO_ANCILLA_TDEPTH_4,  # mem_decomp
#                                          ToffoliDecompType.ZERO_ANCILLA_TDEPTH_0_UNCOMPUTE,  # fan_out_decomp
#                                      ],
#                                      True
#                                      ))
#
#         # #Verification
#         assert (bbcircuit.verify_number_qubits() == True)
#         # assert (bbcircuit.verify_depth(Alexandru_scenario=True) == True)
#         assert (bbcircuit.verify_T_count() == True)
#         # assert (bbcircuit.verify_T_depth() == True)
#         assert (bbcircuit.verify_hadamard_count(Alexandru_scenario=True) == True)
#         assert (bbcircuit.verify_cnot_count() == True)