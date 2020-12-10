# TODO: Document the code !!
"""
  Implementation of the carry lookahead adder 
  arxiv preprint 0406142
"""
import cirq
import math as mt
from qramcircuits.toffoli_decomposition import ToffoliDecomposition, ToffoliDecompType

class CarryLookaheadAdder:
  def __init__(self, A, B, decompositon_strategy = [(ToffoliDecompType.NO_DECOMP, ToffoliDecompType.NO_DECOMP)]*2):
    """
      params: A: quantum register holding the first integer operand
      params: B: quantum register holding the second integer operand
      params: decompositon_strategy: Toffoli decomposition to use in the p-round and the other rounds

    """
    self.A, self.B = A, B
    self.rounds = self.construct_rounds()
    self.decompositon_strategy = decompositon_strategy
    self.circuit = self.construct_circuit()
    
  def construct_rounds(self):
    """
      return the init, p-round, g-round and the c-round of the carry lookahead adder
    """
    n = len(self.A)
    init = []
    p_round = []
    g_round = []
    c_round = []
    l = mt.floor(mt.log2(n))
    w = [i=="1" for i in bin(n)[2:]].count(True)
    l2 = n-w-l
    ancillae1 = [cirq.NamedQubit("a"+str(i)) for i in range(n)]
    ancillae2 = [cirq.NamedQubit("b"+str(i)) for i in range(l2)]
    
    # Init round
    for i in range(n):
      init.append(cirq.TOFFOLI(self.A[i], self.B[i], ancillae1[i]))
      init.append(cirq.CNOT(self.A[i], self.B[i]))

    # P-round
    # First moment
    for i in range(2,n-1, 2):
      p_round.append(cirq.TOFFOLI(self.B[i], self.B[i+1], ancillae2[i//2-1]))
    start = 0
    index = (n-2)
    end1 = (n-2)//2 
    # print(index, end1)
    for i in range(1, l-1):
      index = index//2
      start += index
      end = start + index//2 
      if end > l2:
        end = l2
      s = 0
      # print(index, start, end)
      k = 1
      for j in range(start,end):
        i1 = j-end1+k
        i2 = j-end1+k+1
        # print(j, i1, i2)
        p_round.append(cirq.TOFFOLI(ancillae2[i1], ancillae2[i2], ancillae2[j]))
        s+=1
        k += 1
      end1 -= s

    # G-round
    # First moment
    for i in range(1, n, 2):
      g_round.append(cirq.TOFFOLI(ancillae1[i-1], self.B[i], ancillae1[i]))

    start = 0
    k = 0
    temp = n-1
    
    for i in range(l-1):
      index = 2**i
      start += index
      
      step = 2**(i+2)
      end = start+(n-start)//step*(step)+1
      # print("###################################")
      # print(index, start, end)
      # print("###################################")
      k_anc = k
      for j in range(start,end, step):
        i1 = j
        i2 = k
        target = j+step//2
        if target > n:
          pass
        else:
          # print(i1, i2, target)
          # print(i1, i2, target)
          g_round.append(cirq.TOFFOLI(ancillae1[i1], ancillae2[i2], ancillae1[target]))
          k += 2
      k = k_anc + temp//2
      temp = (temp//2-1)
    # C-round
    # First moment of C-round
    for i in range(1, n-1, 2):
      c_round.append(cirq.TOFFOLI(ancillae1[i], self.B[i+1], ancillae1[i+1]))

    o1 = 1
    o2 = (n-2)//2
    for k in range(2,l):
      start = 2**k-1
      step = 2**k
      span = 2**(k-1)
      # print("#############c-round##########")
      # print(start, step, span)
      # print("############################")
      for p in range(start, n, step):
        # print(p)
        if p+span>n:
          pass
        else:
          c_round.append(cirq.TOFFOLI(ancillae1[p], ancillae2[o1], ancillae1[p+span]))
          o1 += 2
      o1 = o2
      o2 += (o2-1)//2

    # Last round 
    last_round = [cirq.CNOT(ancillae1[i], self.B[i+1]) for i in range(n-1)]
    last_round += [cirq.X(self.B[i]) for i in range(n-1)]
    last_round += [cirq.CNOT(self.A[i], self.B[i]) for i in range(1,n-1)]
    
    
    return init, p_round, g_round, c_round[::-1], last_round

 
  def construct_circuit(self):
    """
      returns the CLA circuit
    """
    
    """
      Computation part of the circuit
    """
    init_comp, p_round_comp, g_round_comp, c_round_comp, last_round = self.construct_rounds()
    
    # Init 
    circuit = cirq.Circuit(
        ToffoliDecomposition.
            construct_decomposed_moments(cirq.Circuit(init_comp),
                                          self.decompositon_strategy[1][0])
    )

    # P-round
    circuit += cirq.Circuit(
        ToffoliDecomposition.
            construct_decomposed_moments(cirq.Circuit(p_round_comp),
                                          self.decompositon_strategy[0][0])
    )

    # G-round
    circuit += cirq.Circuit(
        ToffoliDecomposition.
            construct_decomposed_moments(cirq.Circuit(g_round_comp),
                                          self.decompositon_strategy[1][0])
    )

    # C-round
    circuit += cirq.Circuit(
        ToffoliDecomposition.
            construct_decomposed_moments(cirq.Circuit(c_round_comp),
                                          self.decompositon_strategy[1][0])
    )

    # P-inverse
    circuit += cirq.Circuit(
        ToffoliDecomposition.
            construct_decomposed_moments(cirq.Circuit(p_round_comp[::-1]),
                                          self.decompositon_strategy[0][1])
    )

    # Last round
    circuit += cirq.Circuit(
        ToffoliDecomposition.
            construct_decomposed_moments(cirq.Circuit(last_round),
                                          self.decompositon_strategy[0][0])
    )

    """
      Uncomputation part of the circuit
    """
    n = len(self.A)
    index = (n-2)//2

    p_round_uncom = p_round_comp[:index-1] + p_round_comp[index:]
    circuit += cirq.Circuit(
        ToffoliDecomposition.
            construct_decomposed_moments(cirq.Circuit(p_round_uncom),
                                          self.decompositon_strategy[0][0])
    )

    # C-round uncomputation
    c_round_uncomp = c_round_comp[::-1][:-1]
    circuit += cirq.Circuit(
        ToffoliDecomposition.
            construct_decomposed_moments(cirq.Circuit(c_round_uncomp),
                                          self.decompositon_strategy[1][1])
    )

    # G-round uncomputation
    g_round_uncomp = g_round_comp[:index] + g_round_comp[index+1:]
    g_round_uncomp = g_round_uncomp[::-1]

    circuit += cirq.Circuit(
        ToffoliDecomposition.
            construct_decomposed_moments(cirq.Circuit(g_round_uncomp),
                                          self.decompositon_strategy[1][1])
    )

    # P-round uncomputation inverse
    p_round_uncom = p_round_comp[:index-1] + p_round_comp[index:]
    circuit += cirq.Circuit(
        ToffoliDecomposition.
            construct_decomposed_moments(cirq.Circuit(p_round_uncom[::-1]),
                                          self.decompositon_strategy[0][1])
    )
    
    # last moment of X gates
    x_moment = [cirq.X(self.B[i]) for i in range(n-1)]

    circuit.append(x_moment)
    return circuit

