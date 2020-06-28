"""
    Implementation of Modular multiplier from Fig. 2 and 3 in arXiv:1611.07995v2
"""
import cirq

from mathematics.shor1611 import HybridModularAdder


def extended_euclidean_alg(a, b):
    """return (g, x, y) such that a*x + b*y = g = gcd(a, b)"""
    N = b
    x0, x1, y0, y1 = 0, 1, 1, 0
    while a != 0:
        (q, a), b = divmod(b, a), a
        y0, y1 = y1, y0 - q * y1
        x0, x1 = x1, x0 - q * x1
        if x0 < 0:
            x0 += N
    return b, x0, y0


class ShorModularMultiplier:
    def __init__(self, x, product_register, hardwired_constant, N, zero_qubit):
        """
        |x>|0n>|0> -->|a*x % N>|0n>|0>
        :param x: input register
        :param product_register: register initialized with |00..0> and
        holding the result at the end
        :param hardwired_constant: hardwired constant a
        :param N: size of the ring/Field
        :param zero_qubit: qubit initialized with zero
        """
        self.x, self.product_register, self.hardwired_constant, self.N = x, product_register, hardwired_constant, N
        self.zero_qubit = zero_qubit

    # def multiplier(self):
    #     n = len(self.x)
    #     moments = []
    #     # Addition and shift Algorithm
    #     for i in range(n-1):
    #         constant = 2**i*self.hardwired_constant%self.N
    #         moments += HybridModularAdder(sum_register=self.product_register,
    #                                       control=self.zero_qubit,
    #                                       N=self.N,
    #                                       hardwired_constant=constant,
    #                                       garbage_qubit=self.x[i+1])\
    #             .construct_controlled_circuit(self.x[i]).moments
    #     constant = 2 ** (n-1) * self.hardwired_constant % self.N
    #     moments += HybridModularAdder(sum_register=self.product_register,
    #                                   control=self.zero_qubit,
    #                                   N=self.N,
    #                                   hardwired_constant=constant,
    #                                   garbage_qubit=self.x[0]) \
    #         .construct_controlled_circuit(self.x[n-1]).moments
    #     circuit = cirq.Circuit(moments)
    #     return circuit
    def multiplier(self, control=None):
        """

        :param control: qubit controlling the operation
        :return: |x>|b+ax%N>|0> if control is 1
                 |x>|b>|0> otherwise
        """
        n = len(self.x)
        moments = []
        # Addition and shift Algorithm
        for i in range(n - 1):
            constant = 2 ** i * self.hardwired_constant % self.N
            # Non-controlled version
            if control is None:
                moments += HybridModularAdder(sum_register=self.product_register,
                                              control=self.zero_qubit,
                                              N=self.N,
                                              hardwired_constant=constant,
                                              garbage_qubit=self.x[i + 1]) \
                    .construct_controlled_circuit([self.x[i]]).moments
                # Controlled version
            else:
                moments += HybridModularAdder(sum_register=self.product_register,
                                              control=self.zero_qubit,
                                              N=self.N,
                                              hardwired_constant=constant,
                                              garbage_qubit=self.x[i + 1]) \
                    .construct_controlled_circuit(control + [self.x[i]]).moments
        constant = 2 ** (n - 1) * self.hardwired_constant % self.N
        if control is None:
            moments += HybridModularAdder(sum_register=self.product_register,
                                          control=self.zero_qubit,
                                          N=self.N,
                                          hardwired_constant=constant,
                                          garbage_qubit=self.x[0]) \
                .construct_controlled_circuit([self.x[n - 1]]).moments
        else:
            moments += HybridModularAdder(sum_register=self.product_register,
                                          control=self.zero_qubit,
                                          N=self.N,
                                          hardwired_constant=constant,
                                          garbage_qubit=self.x[0]).construct_controlled_circuit(
                control + [self.x[n - 1]]).moments

        circuit = cirq.Circuit(moments)
        return circuit

    def construct_circuit(self, control=None):
        """

        :param control: qubit controlling the operation
        :return: |ax%N>|0n>|0> if control is 1
                 |x>|0n>|0> otherwise
                 Note that in case a = 0 the result will be |x>|0n>|0>
        """
        # Size of x
        n = len(self.x)

        # | x > | b + ax % N > | 0 > if control is 1
        # | x > | b > | 0 > otherwise
        moments = self.multiplier(control).moments

        # SWAP operation
        if control is None:
            moments += [cirq.SWAP(self.x[i], self.product_register[i]) for i in range(n)]
        # Controlled SWAP
        else:
            moments += [cirq.CSWAP(control[0], self.x[i], self.product_register[i]) for i in range(n)]

        # Determining the inverse of x
        t1, x_inverse, t2 = extended_euclidean_alg(self.hardwired_constant, self.N)

        # Resetting the middle register to | 0n >
        moments += ShorModularMultiplier(x=self.x,
                                         product_register=self.product_register,
                                         hardwired_constant=x_inverse,
                                         N=self.N,
                                         zero_qubit=self.zero_qubit).multiplier(control).moments[::-1]
        circuit = cirq.Circuit(moments)
        return circuit

    # def construct_controlled_circuit(self, control_qubit):
    #     n = len(self.x)
    #     moments = self.multiplier(control=control_qubit).moments
    #     moments += [cirq.CSWAP(control_qubit[0], self.x[i], self.product_register[i]) for i in range(n)]
    #     t1, x_inverse, t2 = xgcd(self.hardwired_constant, self.N)
    #     # print(x_inverse)
    #     moments += ShorModularMultiplier(x=self.x,
    #                                      product_register=self.product_register,
    #                                      hardwired_constant=x_inverse,
    #                                      N=self.N,
    #                                      zero_qubit=self.zero_qubit).multiplier(control=control_qubit).moments[::-1]
    #     circuit = cirq.Circuit(moments)
    #     return circuit
