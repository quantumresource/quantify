import cirq

from mathematics import CarryUsingDirtyAncilla

a = [cirq.NamedQubit("a" + str(i)) for i in range(4)]
g = [cirq.NamedQubit("g" + str(i)) for i in range(3)]
r = cirq.NamedQubit("r")

carry = CarryUsingDirtyAncilla(a, 11, g, r).construct_circuit()
print(carry)
