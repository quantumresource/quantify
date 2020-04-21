import cirq
import numpy as np
#######################HYBRID CIRCUIT####################################################

def hybrid_sequential(qubits, search, k):
    n = len(qubits)
    ancillae = qubits+[cirq.LineQubit(i) for i in range(n,n+2**k)]
    circuit = cirq.circuits.Circuit()
    target = cirq.NamedQubit("target")
    l = len(search)
    op = []
    for j in range(2**k):
        binary = list(bin(j)[2:].zfill(k))
        binary = [int(x) for x in binary]
        op.append(cirq.ops.ControlledOperation(ancillae[:k],cirq.ops.X(ancillae[n+j]),binary))

    for m in search:
        b = bin(m)[2:].zfill(n)
        binary = list(b)
        binary = [int(x) for x in binary]
        offset = int(b[0:k],2)
        op.append(cirq.ops.ControlledOperation([ancillae[n+offset]]+ancillae[k:n],cirq.ops.X(target),[1]+binary[k:]))
    circuit.append(op, strategy=cirq.InsertStrategy.NEW_THEN_INLINE)

    return circuit

def verify_qubits(circuit, input_qubits, first_k_qubits, decomposed=0):
    n = len(input_qubits)
    paper_qubits = n + 2 ** first_k_qubits + 1 + max(first_k_qubits - 1, n - first_k_qubits)
    nr_q = len(circuit.all_qubits())

    if decomposed==0:
        paper_qubits-=max(first_k_qubits - 1, n - first_k_qubits)

    return nr_q == paper_qubits