import cirq
import pyzx as zx

class CirqPyZX:
  def __init__(self, circuit):
    """
      params: circuit: Cirq circuit to be transformed
    """
    self.circuit = circuit
    self.circuit_zx = self.to_pzyx_circuit(circuit)
    self.matrix = self.circuit_zx.to_matrix()

  def to_pzyx_circuit(self, circuit):
    """
      transforms Cirq circuit into PyZX circuit
      params: circuit: Cirq circuit to be transformed
    """
    
    # The qubits used in the circuit
    qubits = self.circuit.all_qubits()

    # Instanciating a PyZX circuit that uses the same number of qubits
    self.circuit_zx = zx.Circuit(len(qubits))
    qubit_id_to_zx_id = {}

    # Identifying each cirq qubit with a PyZX qubit
    for i,key in enumerate(qubits):
      qubit_id_to_zx_id[key] = i
    
    # In each moment in the Cirq circuit identify the operations, the involved qubits 
    # and do the corresponding operation in PyZX
    # The supported operations are {T, X, Toffoli, CNOT, Z, CZ, H, S, CCZ and their inverse}
    for moment in circuit:
      for op in moment:
        if isinstance(op, cirq.GateOperation) and op.gate == cirq.T:
          qbts = op.qubits
          key = qbts[0]
          self.circuit_zx.add_gate(zx.gates.T(qubit_id_to_zx_id[key]))
        
        elif isinstance(op, cirq.GateOperation) and op.gate == cirq.T**-1:
          qbts = op.qubits
          key = qbts[0]
          self.circuit_zx.add_gate(zx.gates.T(qubit_id_to_zx_id[key], adjoint=True))

        elif isinstance(op, cirq.GateOperation) and op.gate == cirq.X:
          qbts = op.qubits
          key = qbts[0]
          self.circuit_zx.add_gate(zx.gates.NOT(qubit_id_to_zx_id[key]))
        
        elif isinstance(op, cirq.GateOperation) and op.gate == cirq.H:
          qbts = op.qubits
          key = qbts[0]
          self.circuit_zx.add_gate(zx.gates.HAD(qubit_id_to_zx_id[key]))

        elif isinstance(op, cirq.GateOperation) and op.gate == cirq.Z:
          qbts = op.qubits
          key = qbts[0]
          self.circuit_zx.add_gate(zx.gates.Z(qubit_id_to_zx_id[key]))

        elif isinstance(op, cirq.GateOperation) and op.gate == cirq.S:
          qbts = op.qubits
          key = qbts[0]
          self.circuit_zx.add_gate(zx.gates.S(qubit_id_to_zx_id[key]))

        elif isinstance(op, cirq.GateOperation) and op.gate == cirq.S**-1:
          qbts = op.qubits
          key = qbts[0]
          self.circuit_zx.add_gate(zx.gates.S(qubit_id_to_zx_id[key], adjoint=True))

        elif isinstance(op, cirq.GateOperation) and op.gate == cirq.CNOT:
          qbts = op.qubits
          ctrl, trgt = qbts[0], qbts[1]
          self.circuit_zx.add_gate(zx.gates.CNOT(control=qubit_id_to_zx_id[ctrl], 
                                                 target=qubit_id_to_zx_id[trgt]))
          
        elif isinstance(op, cirq.GateOperation) and op.gate == cirq.CCZ:
          qbts = op.qubits
          ctrl0, ctrl1, trgt = qbts[0], qbts[1], qbts[2]
          self.circuit_zx.add_gate(zx.gates.CCZ(ctrl1=qubit_id_to_zx_id[ctrl0], 
                                                 ctrl2=qubit_id_to_zx_id[ctrl1],
                                                 target=qubit_id_to_zx_id[trgt]))
          
        elif isinstance(op, cirq.GateOperation) and op.gate == cirq.TOFFOLI:
          qbts = op.qubits
          ctrl0, ctrl1, trgt = qbts[0], qbts[1], qbts[2]
          self.circuit_zx.add_gate(zx.gates.Tofolli(ctrl1=qubit_id_to_zx_id[ctrl0], 
                                                 ctrl2=qubit_id_to_zx_id[ctrl1],
                                                 target=qubit_id_to_zx_id[trgt]))
        
        elif not isinstance(op, cirq.GateOperation):
          raise TypeError("{!r} is not a gate operation.".format(op))

        else:
          raise TypeError("gate operation {!r} is not supported.".format(op))


    return self.circuit_zx

  def simulate(self, initial_state):
    """
      params: initial_state: a unitary vector of size 2**n_qubits
    """
    # Checking the norm of the initial state 
    if abs(np.linalg.norm(initial_state) - 1.0) > 10**-2:
      raise TypeError("the norme of the vecotr must be equal to one")
    
    return self.matrix.dot(initial_state)
    

  def optimize(self):
    """
      Optimize the circuit using PyZX full_reduce optimization function
    """
    # transforming the PyZX circuit to a graph
    graph = self.circuit_zx.to_graph()
    zx.full_reduce(graph, quiet=True) 
    
    # Optimizing the graph
    graph.normalize()

    # Extracting the circuit from the optimized graph
    self.circuit_zx = zx.extract_circuit(graph.copy())
    return self.circuit_zx


  def simulate_optimize(self, initial_state):
    """
      Simulate the optimized circuit
    """
    self.optimize()
    m = self.circuit_zx.to_matrix()
    return m.dot(initial_state)

    
