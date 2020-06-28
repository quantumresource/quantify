import cirq

import optimizers as qopt
import mathematics


def main():

    print("Hello Mathematics circuits!")

    # print(mathematics.CarryRipple4TAdder(nr_qubits=4,
    #                                use_dual_ancilla=False))


    carry_ripple_4t = mathematics.CarryRipple4TAdder(nr_qubits = 4,
                                                     use_dual_ancilla = False)
    print(carry_ripple_4t)

    # n_c = cirq.Circuit(carry_ripple_4t.circuit.all_operations())
    # print(n_c.to_text_diagram(qubit_order=carry_ripple_4t.qubit_order,
    #                           use_unicode_characters=False))

    # carry_ripple_8t = mathematics.CarryRipple8TAdder(nr_qubits=4,
    #                                                  use_dual_ancilla=False)
    # print(carry_ripple_8t)

if __name__ == "__main__":
    main()