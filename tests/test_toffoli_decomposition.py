import cirq
import qramcircuits.toffoli_decomposition as td
import numpy as np
import copy

def test_dec_NO_DECOMP():
    circuit = cirq.Circuit()
    qubits = [cirq.NamedQubit(str(i)) for i in range(3)]
    moments= td.ToffoliDecomposition(
        decomposition_type=td.ToffoliDecompType.NO_DECOMP,
        qubits=qubits).decomposition()
    circuit.append(moments)
    measurements = [cirq.measure(qubits[i]) for i in range(len(qubits))]
    circuit.append(measurements)
    simulator = cirq.Simulator()
    l = [0 for i in range(2**len(qubits))]
    initial_state = np.array(l,dtype=np.complex64)
    for i in range(8):
        initial_state[i]=1
        result=simulator.simulate(circuit,qubit_order=qubits,initial_state=initial_state)
        temp = copy.deepcopy(initial_state) # temp is supposed to have the expected result of a tofjoli
        if i in [6,7]:
            temp[6]=(1-temp[6])
            temp[-1] = (1 - temp[-1])
        assert (np.array_equal(np.array(result.final_state), temp))

        initial_state[i] = 0

def test_dec_ZERO_ANCILLA_TDEPTH_3():
    circuit = cirq.Circuit()
    qubits = [cirq.NamedQubit(str(i)) for i in range(3)]
    moments= td.ToffoliDecomposition(
        decomposition_type=td.ToffoliDecompType.ZERO_ANCILLA_TDEPTH_3,
        qubits=qubits).decomposition()
    circuit.append(moments)
    measurements = [cirq.measure(qubits[i]) for i in range(len(qubits))]
    circuit.append(measurements)
    simulator = cirq.Simulator()
    l = [0 for i in range(2**len(qubits))]
    initial_state = np.array(l,dtype=np.complex64)
    for i in range(8):
        initial_state[i]=1
        result=simulator.simulate(circuit,qubit_order=qubits,initial_state=initial_state)
        temp = copy.deepcopy(initial_state) # temp is supposed to have the expected result of a tofjoli
        if i in [6,7]:
            temp[6]=(1-temp[6])
            temp[-1] = (1 - temp[-1])
        assert (np.array_equal(np.array(np.around(result.final_state)), temp))

        initial_state[i] = 0

def test_dec_ONE_ANCILLA_TDEPTH_2():
    circuit = cirq.Circuit()
    qubits = [cirq.NamedQubit(str(i)) for i in range(3)]
    dec = td.ToffoliDecomposition(
        decomposition_type=td.ToffoliDecompType.ONE_ANCILLA_TDEPTH_2,
        qubits=qubits)
    moments=dec.decomposition()
    circuit.append(moments)
    simulator = cirq.Simulator()
    all_qubits = [dec.ancilla[0]]+qubits
    l = [0 for i in range(2**len(all_qubits))]
    initial_state = np.array(l, dtype=np.complex64)
    for i in range(8):
        initial_state[i]=1
        result=simulator.simulate(circuit,qubit_order=all_qubits,initial_state=initial_state)
        temp = copy.deepcopy(initial_state) # temp is supposed to have the expected result of a tofjoli
        if i in [6,7]:
            temp[6]=(1-temp[6])
            temp[7] = (1 - temp[7])
        assert (np.array_equal(np.array(np.around(result.final_state)), temp))
        initial_state[i] = 0

def test_dec_FOUR_ANCILLA_TDEPTH_1_A():
    circuit = cirq.Circuit()
    qubits = [cirq.NamedQubit(str(i)) for i in range(3)]
    dec = td.ToffoliDecomposition(
        decomposition_type=td.ToffoliDecompType.FOUR_ANCILLA_TDEPTH_1_A,
        qubits=qubits)
    moments=dec.decomposition()
    circuit.append(moments)
    simulator = cirq.Simulator()
    all_qubits = dec.ancilla + qubits
    l = [0 for i in range(2**len(all_qubits))] #+1 is for the additional ancilla
    initial_state = np.array(l,dtype=np.complex64)
    for i in range(8):
        initial_state[i]=1
        result=simulator.simulate(circuit,qubit_order=all_qubits,initial_state=initial_state)
        temp = copy.deepcopy(initial_state) # temp is supposed to have the expected result of a tofjoli
        if i in [6,7]:
            temp[6]=(1-temp[6])
            temp[7] = (1 - temp[7])
        assert (np.array_equal(np.array(np.around(result.final_state)), temp))
        initial_state[i] = 0

def test_dec_FOUR_ANCILLA_TDEPTH_1_B():
    circuit = cirq.Circuit()
    qubits = [cirq.NamedQubit(str(i)) for i in range(3)]
    dec = td.ToffoliDecomposition(
        decomposition_type=td.ToffoliDecompType.FOUR_ANCILLA_TDEPTH_1_B,
        qubits=qubits)
    moments=dec.decomposition()
    circuit.append(moments)
    simulator = cirq.Simulator()
    all_qubits = dec.ancilla + qubits
    l = [0 for i in range(2**len(all_qubits))] #+1 is for the additional ancilla
    initial_state = np.array(l,dtype=np.complex64)
    for i in range(8):
        initial_state[i]=1
        result=simulator.simulate(circuit,qubit_order=all_qubits,initial_state=initial_state)
        temp = copy.deepcopy(initial_state) # temp is supposed to have the expected result of a tofjoli
        if i in [6,7]:
            temp[6]=(1-temp[6])
            temp[7] = (1 - temp[7])
        assert (np.array_equal(np.array(np.around(result.final_state)), temp))
        initial_state[i] = 0


def test_dec_ZERO_ANCILLA_CNOT_3():
    circuit = cirq.Circuit()
    qubits = [cirq.NamedQubit(str(i)) for i in range(3)]
    moments= td.ToffoliDecomposition(
        decomposition_type=td.ToffoliDecompType.ZERO_ANCILLA_CNOT_3,
        qubits=qubits).decomposition()
    circuit.append(moments)
    measurements = [cirq.measure(qubits[i]) for i in range(len(qubits))]
    circuit.append(measurements)
    simulator = cirq.Simulator()
    l = [0 for i in range(2**len(qubits))]
    initial_state = np.array(l,dtype=np.complex64)
    for i in range(8):
        initial_state[i]=1
        result=simulator.simulate(circuit,qubit_order=qubits,initial_state=initial_state)
        temp = copy.deepcopy(initial_state) # temp is supposed to have the expected result of a tofjoli
        if i in [6,7]:
            temp[6]=(1-temp[6])
            temp[-1] = (1 - temp[-1])
        assert (np.array_equal(np.array(np.abs(np.around(result.final_state))), temp))
        initial_state[i] = 0



def test_dec_ZERO_ANCILLA_CNOT_4():
    circuit = cirq.Circuit()
    qubits = [cirq.NamedQubit(str(i)) for i in range(3)]
    moments= td.ToffoliDecomposition(
        decomposition_type=td.ToffoliDecompType.ZERO_ANCILLA_CNOT_4,
        qubits=qubits).decomposition()
    circuit.append(moments)
    measurements = [cirq.measure(qubits[i]) for i in range(len(qubits))]
    circuit.append(measurements)
    simulator = cirq.Simulator()
    l = [0 for i in range(2**len(qubits))]
    initial_state = np.array(l,dtype=np.complex64)
    for i in range(8):
        initial_state[i]=1
        result=simulator.simulate(circuit,qubit_order=qubits,initial_state=initial_state)
        temp = copy.deepcopy(initial_state) # temp is supposed to have the expected result of a tofjoli
        if i in [6,7]:
            temp[6]=(1-temp[6])
            temp[-1] = (1 - temp[-1])
        assert (np.array_equal(np.array(np.abs(np.around(result.final_state))), temp))
        initial_state[i] = 0

