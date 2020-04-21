import cirq


def lookahead(circuit, window_size, function):

    """

    :param circuit:
    :param window_size:
    :param function:
    :return:  the result will be in the form of key-value where the key is
              in the dictionnary are the starting moment indice and the value
              is the value returned by the function applied on the subcircuit
              of depth = window size
    """

    result = dict()
    for i in range(len(circuit) - window_size+1):
        result[i] = function(circuit[i:i + window_size])

    result[i + 1] = function(circuit[i + 1:])

    return result


"""
    sample function that return the number of T-gates in a subcircuit/circuit
"""
def find_T_gates(circuit):
    op_count=0
    for moment in circuit:
        for operation in moment:
            # if a gate is found in this moment,
            #  then increase depth and break to the next moment
            if isinstance(operation, cirq.GateOperation) \
                    and operation.gate in [cirq.T]:
                op_count += 1
    return op_count



"""
    sample function which return the parallel Toffolis in a subcircuit/circuit
"""
def find_parallel_Toffolis(circuit):

    """

    :param circuit:
    :return: a dictionnary where the keys are the indice of the moment which contain Toffolis and the values are
             the list of toffolis which are parallel to the first Toffoli moment in circuit/subcircuit
    """
    result=dict()
    i=0
    #the idea is as long as a Toffoli controls is not in the same wire the target of one of the previous
    #Toffolis is or vice versa  then it's parallel with the previous Toffolis otherwise it's not and the following
    #Toffolis are checked against this Toffoli
    for moment in circuit:
        result[i]=[]
        for operation in moment:

            if isinstance(operation, cirq.GateOperation) \
                    and operation.gate in [cirq.TOFFOLI]:
                temp = True

                for j in range(i):
                    for x in result[j]:
                        if operation.qubits[2] in x.qubits[:2] or (operation.qubits[0] == x.qubits[2] or operation.qubits[1] == x.qubits[2]):
                            temp=False
                if temp:
                    result[i].append(operation)
                else:
                    return result
        i+=1
    return result

a = cirq.NamedQubit('a')
b = cirq.NamedQubit('b')
c = cirq.NamedQubit('c')
d = cirq.NamedQubit('d')
e = cirq.NamedQubit('e')
f = cirq.NamedQubit('f')
m=cirq.T(a)
circuit=cirq.Circuit()

circuit.append(cirq.TOFFOLI(a,b,c))
circuit.append(cirq.TOFFOLI(d,e,f))
circuit.append(cirq.TOFFOLI(a,e,d))
circuit.append(cirq.TOFFOLI(d,e,f))
circuit.append(cirq.TOFFOLI(a,c,d))
circuit.append(cirq.TOFFOLI(a,c,d))

print(circuit)
print(len(circuit))

print(lookahead(circuit, 3, find_parallel_Toffolis))
