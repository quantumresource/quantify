from optimizers.lookahead_analysis import LookAheadAnalysis as ma
import cirq

qubits = [cirq.NamedQubit(str(i)) for i in range(3)]
moment = [cirq.T(i) for i in qubits]
circuit = cirq.Circuit(cirq.decompose_multi_controlled_x())
circuit.append(moment)
circuit.append(moment)
circuit.append(moment)
circuit.append(moment)

print(circuit)
result = ma(circuit)
k = result.lookahead(2, result.find_T_gates)
result.plot_data(k)
print(k)
# ma(circuit).plot_data(window_size=3)

# 0+n(2-2)+n-(3-2)+n-(4-2).. = (n+n-(p-2))(p-1)/2