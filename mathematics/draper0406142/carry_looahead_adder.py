import cirq
import numpy as np

class CarryLookaheadAdder:
    def __init__(self, A, B):
        self.A, self.B = A, B
        self.circuit = self.construct_circuit()

    def construct_moments(self):
        n = len(self.A)
        p = {}
        g = {}
        g[(0,1)] = cirq.NamedQubit("g"+str((0, 1)))

        for i in range(1,n):
            p[(i, i+1)]=B[i]
            g[(i,i+1)] = cirq.NamedQubit("g"+str((i, i+1)))

        init = [cirq.TOFFOLI(A[i], B[i], g[(i, i+1)]) for i in range(n)]
        init += [cirq.CNOT(A[i], B[i]) for i in range(n)]

        # P-ROUND
        p_moments = []
        st = int(np.log2(n))
        for t in range(1, st):
            st1 = int(n/(2**t))
            for m in range(1, st1):
                i = 2**(t-1)*2*m
                j = 2**(t-1)*(2*m+1)
                k = 2**t*m
                p[(k, k+2**t)]=cirq.NamedQubit("p"+str((k, k+2**t)))
                p_moments += [cirq.TOFFOLI(p[(i, i+2**(t-1))], p[(j, j+2**(t-1))], p[(k, k+2**t)])]

        # G-ROUND
        g_moments = []
        g_moments_inv = []
        for t in range(1, st+1):
            st1 = int(n/(2**t))
            for m in range(st1):
                i = 2**t*m
                j = i+2**t
                k = 2**t*m+2**(t-1)
                g[(i,j)] = g[(j-1,j)]
                g_moments += [cirq.TOFFOLI(g[(i,k)], p[k, j], g[i,j])]
                if j!=n:
                    g_moments_inv += [cirq.TOFFOLI(g[(i,k)], p[k, j], g[i,j])]

        # C-ROUND
        c_moments = []
        c_moments_inv = []
        st2 = int(np.log2(2*n/3))
        for t in range(st2,0,-1):
            st1 =  int((n-2**(t-1))/(2**t))
            for m in range(1,st1+1):
                j = 2**t*m+2**(t-1)
                k = 2**t*m
                c_moments += [cirq.TOFFOLI(g[(k-1,k)], p[(k,j)], g[(j-1,j)])]
                if j!=n:
                    c_moments_inv += [cirq.TOFFOLI(g[(k-1,k)], p[(k,j)], g[(j-1,j)])]

        last_round = [cirq.CNOT(g[(i,i+1)], B[i+1]) for i in range(n-1)]
        last_round += [cirq.X(B[i]) for i in range(n-1)]
        last_round += [cirq.CNOT(A[i], B[i]) for i in range(1,n-1)]

        p_moments_inv = p_moments[:int(n/2)-2]+p_moments[int(n/2)-1:]

        init_inv = init[::-1][1:n]+init[::-1][n+1:]

        return init, p_moments, g_moments, c_moments, last_round, p_moments_inv, c_moments_inv[::-1], g_moments_inv[::-1], init_inv

    def construct_circuit(self):

        init, p_round, g_round, c_round, last_round, p_round_inv, c_round_inv, g_round_inv, init_inv = self.construct_moments()

        circuit = cirq.Circuit(init)
        
        circuit.append(p_round)
        
        circuit.append(g_round)
        
        circuit.append(c_round)
        
        circuit.append(p_round[::-1])
        
        circuit.append(last_round)
        
        circuit.append(p_round_inv)
        
        circuit.append(c_round_inv)
        
        circuit.append(g_round_inv)
        
        circuit.append(p_round_inv[::-1])
        
        circuit.append(init_inv)
        
        for i in range(len(self.A)-1):
            circuit.append(cirq.X(self.B[i]))
        
        return circuit

