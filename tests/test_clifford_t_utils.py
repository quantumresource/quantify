import cirq

import utils.clifford_t_utils as ctu

def test_gate_types():
    a = cirq.NamedQubit("a")

    assert (ctu.is_t_or_s_gate(cirq.T(a)) == True)
    assert (ctu.is_t_or_s_gate(cirq.S(a)) == True)
    assert (ctu.is_t_or_s_gate(cirq.T(a)**-1) == True)
    assert (ctu.is_t_or_s_gate(cirq.S(a)**-1) == True)
    assert (ctu.is_t_or_s_gate(cirq.X(a)) == False)

def test_reverse_moments():

    a = cirq.NamedQubit("a")
    b = cirq.NamedQubit("b")
    c = cirq.NamedQubit("c")

    moments = [
        cirq.Moment([cirq.T(a), cirq.CNOT(b, c)]),
        cirq.Moment([cirq.CNOT(a, b), cirq.S(c)**-1])
    ]

    n_moments = ctu.reverse_moments(moments)

    assert(n_moments == [
        cirq.Moment([cirq.CNOT(a, b), cirq.S(c)]),
        cirq.Moment([cirq.T(a)**-1, cirq.CNOT(b, c)])
    ])