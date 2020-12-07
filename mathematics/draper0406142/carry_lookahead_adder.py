# TODO: Document the code !!

import cirq
import math as mt

class CarryLookaheadAdder:
  def __init__(self, A, B):
    self.A, self.B = A, B
    self.circuit = self.construct_circuit()

  def construct_circuit(self):
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
    # ancillae2 = {}
    # ancillae2[-1] = [cirq.NamedQubit(str(k)+str(i)) for i in range(n)]
    # for k in range(l-1):
    #   start = 2**k
    #   step = 2**(k+1)
    #   u = (n-start)//step
    #   ancillae2[k] = [cirq.NamedQubit(str(k)+str(i)) for i in range(u)]

    # Init

    for i in range(n):
      init.append(cirq.TOFFOLI(self.A[i], self.B[i], ancillae1[i]))
      init.append(cirq.CNOT(self.A[i], self.B[i]))

    # P-round
    # First moment
    for i in range(2,n-1, 2):
      p_round.append(cirq.TOFFOLI(self.B[i], self.B[i+1], ancillae2[i//2-1]))
    # Rest of the moments
    # m = mt.floor(mt.log2(len(ancillae2)))
    # l2 = (n-2)//2
    # l3 = mt.floor(mt.log2(l2))
    start = 0
    index = (n-2)
    end1 = (n-2)//2 
    print(index, end1)
    for i in range(1, l-1):
      index = index//2
      start += index
      end = start + index//2 
      if end > l2:
        end = l2
      s = 0
      print(index, start, end)
      k = 1
      for j in range(start,end):
        i1 = j-end1+k
        i2 = j-end1+k+1
        print(j, i1, i2)
        p_round.append(cirq.TOFFOLI(ancillae2[i1], ancillae2[i2], ancillae2[j]))
        s+=1
        k += 1
      end1 -= s

    # G-rounds
    # First moment
    for i in range(1, n, 2):
      g_round.append(cirq.TOFFOLI(ancillae1[i-1], self.B[i], ancillae1[i]))

    # start = 0
    # index = (n-2)
    # end1 = (n-2)//2 
    # print(index, end1)
    start = 0
    # range = n
    k = 0
    for i in range(l-1):
      index = 2**i
      start += index
      # range = range//2
      # end = start + range 
      # if end > l2:
      #   end = l2
      # s = 0
      # saut = (n-2)//2
      
      step = 2**(i+2)
      end = start+(n-start)//step*(step)+1
      # if end == 0:
      #   end = start+1
      print("###################################")
      print(index, start, end)
      print("###################################")
      k_anc = k
      for j in range(start,end, step):
        i1 = j
        i2 = k
        target = j+step//2
        if target > n:
          pass
        else:
          print(i1, i2, target)
          g_round.append(cirq.TOFFOLI(ancillae1[i1], ancillae2[i2], ancillae1[target]))
          # s+=1
          k += 2
      k = k_anc + (n-2)//(2**(i+1))

    ######## C-rounds
    # First moment

    for i in range(1, n-1, 2):
      c_round.append(cirq.TOFFOLI(ancillae1[i], self.B[i+1], ancillae1[i+1]))

    o1 = 1
    o2 = (n-2)//2
    for k in range(2,l):
      start = 2**k-1
      step = 2**k
      span = 2**(k-1)
      print("#############c-round##########")
      print(start, step, span)
      print("############################")
      for p in range(start, n, step):
        print(p)
        if p+span>n:
          pass
        else:
          c_round.append(cirq.TOFFOLI(ancillae1[p], ancillae2[o1], ancillae1[p+span]))
          o1 += 2
      o1 = o2
      o2 += (o2-1)//2

      circuit = cirq.Circuit(init, p_round, g_round, c_round)
      return circuit