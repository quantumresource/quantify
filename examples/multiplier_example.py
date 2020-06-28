from mathematics.thaplyal1706 import QimMultiplier
from qramcircuits.toffoli_decomposition import *
import optimizers as qopt
from utils.counting_utils import *

A = [cirq.NamedQubit('A'+str(i)) for i in range(4)]
B = [cirq.NamedQubit('B'+str(i)) for i in range(4)]
control = cirq.NamedQubit('ctrl')
# ct = ControlAdder(A, B, control).construct_circuit()
ct = QimMultiplier(A, B).multiply()
print(ct.moments)
c=cirq.Circuit(ToffoliDecomposition.construct_decomposed_moments(ct.moments, ToffoliDecompType.FOUR_ANCILLA_TDEPTH_1_A))
# ct = multiplier(A,B).multiply()
print(ct)
print(c)
print(len(c), count_t_depth_of_circuit(c),
count_cnot_of_circuit(c),
count_h_of_circuit(c),
count_t_of_circuit(c))
# miscutils.flag_operations(c, [cirq.ops.H])
qopt.CancelNghHadamards(transfer_flag=False).optimize_circuit(c)
qopt.CancelNghCNOTs(transfer_flag=False) \
            .apply_until_nothing_changes(c, count_cnot_of_circuit)
qopt.CommuteTGatesToStart().optimize_circuit(c)
qopt.CommuteTGatesToStart().optimize_circuit(c)
cirq.optimizers.DropEmptyMoments().optimize_circuit(c)
print(len(c), count_t_depth_of_circuit(c),
count_cnot_of_circuit(c),
count_h_of_circuit(c),
count_t_of_circuit(c))
