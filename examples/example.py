from qramcircuits.mpmct_decomposition import *
import cirq
import optimizers as qopt
import utils.misc_utils as miscutils
from utils.counting_utils import *
from qramcircuits.toffoli_decomposition import *



# qubits = [cirq.NamedQubit("a"+str(i)) for i in range(3)]
# target = cirq.NamedQubit("t")
# cir1=cirq.Circuit()
# cir=cirq.Circuit()
# cir1.append(cirq.TOFFOLI(qubits[0], qubits[1], target))
# cir1.append((cirq.CNOT(qubits[0], cirq.NamedQubit('toff_a0'))))
# cir1.append((cirq.CNOT(qubits[1], cirq.NamedQubit('toff_a2'))))
#
# cir1.append((cirq.H(target)))
#
# # cir1.append(cirq.TOFFOLI(qubits[0], qubits[1], target))
# # m=MPMCTDecomposition(qubits, MPMCTDecompType.ALLOW_DECOMP, 3,target).decompose()
# m=ToffoliDecomposition(decomposition_type=ToffoliDecompType.FOUR_ANCILLA_TDEPTH_1_A, qubits=qubits,target_qubit=target)
# l=m.construct_decomposed_moments(cir1, ToffoliDecompType.FOUR_ANCILLA_TDEPTH_1_A)
# l=m.decomposition()
# cir.append(m)
# cir.append(m[::-1])
# miscutils.flag_operations(cir, [cirq.ops.H])
# qopt.CancelNghHadamards(transfer_flag=False).optimize_circuit(cir)
# qopt.CancelNghCNOTs(transfer_flag=False) \
#             .apply_until_nothing_changes(cir, count_cnot_of_circuit)
# # qopt.CommuteTGatesToStart().optimize_circuit(cir)
# # qopt.CommuteTGatesToStart().optimize_circuit(cir)
#
# #
# print(cir1)
# cir.append(l)
# # cir.append(l[::-1])
# print(cir)
# print(count_t_depth_of_circuit(cir),
# count_cnot_of_circuit(cir),
# count_h_of_circuit(cir),
# count_t_of_circuit(cir))
# qopt.CancelNghHadamards(transfer_flag=False).optimize_circuit(cir)
# qopt.CancelNghCNOTs(transfer_flag=False) \
#             .apply_until_nothing_changes(cir, count_cnot_of_circuit)
# # qopt.CommuteTGatesToStart().optimize_circuit(cir)
# cirq.optimizers.DropEmptyMoments().optimize_circuit(cir)
# print(cir)
# print(count_t_depth_of_circuit(cir),
# count_cnot_of_circuit(cir),
# count_h_of_circuit(cir),
# count_t_of_circuit(cir))
# # print(l)
# # print(count_t_of_circuit(cir))

qubits = [cirq.NamedQubit("a"+str(i)) for i in range(3)]
# cir=cirq.Circuit()
# cir.append(cirq.CNOT(qubits[0], qubits[1]))
# cir.append(cirq.T(qubits[0]))
# cir.append(cirq.H(qubits[1]))
# cir.append(cirq.H(qubits[1]))
# cir.append(cirq.CNOT(qubits[0], qubits[1]))
# cir.append(cirq.CNOT(qubits[0], qubits[1]))
# cir.append(cirq.CNOT(qubits[0], qubits[1]))
# qopt.CommuteTGatesToStart().optimize_circuit(cir)
# miscutils.flag_operations(cir, [cirq.ops.H])
# qopt.CancelNghHadamards(transfer_flag=True).optimize_circuit(cir)
# qopt.CancelNghCNOTs(transfer_flag=True) \
#             .apply_until_nothing_changes(cir, count_cnot_of_circuit)

mo=[cirq.Moment([cirq.TOFFOLI(qubits[0], qubits[1], qubits[2])])]
cir = cirq.Circuit(ToffoliDecomposition.construct_decomposed_moments(mo, ToffoliDecompType.ZERO_ANCILLA_TDEPTH_3))
# m=ToffoliDecomposition(decomposition_type=ToffoliDecompType.FOUR_ANCILLA_TDEPTH_1_A, qubits=qubits,target_qubit=qubits[2])
# m.construct_decomposed_moments(cir, ToffoliDecompType.FOUR_ANCILLA_TDEPTH_1_A)
print(cir)