import cirq

import utils.misc_utils as mu

from .transfer_flag_optimizer import TransferFlagOptimizer

class CancelNghCNOTs(TransferFlagOptimizer):
    # Cancels two neighbouring CNOTs

    def optimization_at(self, circuit, index, op):

        if isinstance(op, cirq.GateOperation) and (op.gate == cirq.CNOT):

            if self.transfer_flag and (not mu.has_flag(op)):
                # Optimize only flagged operations
                return None

            """
            Checking for the CNOTs
            """
            control_qubit = op.qubits[0]
            target_qubit = op.qubits[1]

            # is the next gate a cnot?
            nxt_1 = circuit.next_moment_operating_on([control_qubit],
                                                     start_moment_index=index + 1)
            if nxt_1 is None:
                return None

            nxt_2 = circuit.next_moment_operating_on([target_qubit],
                                                     start_moment_index=index + 1)
            if nxt_2 is None:
                return None

            # Get the operation at the next index
            next_op_cnot1 = circuit.operation_at(control_qubit, nxt_1)
            next_op_cnot2 = circuit.operation_at(target_qubit, nxt_2)

            # print("next are ", next_op_h1, next_op_h2)

            # Are the operations Hadamards?
            if isinstance(next_op_cnot1, cirq.GateOperation) \
                and (next_op_cnot1.gate == cirq.CNOT) \
                and isinstance(next_op_cnot2, cirq.GateOperation) \
                and (next_op_cnot2.gate == cirq.CNOT) :

                # theoretically nxt_1 and nxt_2 should be equal
                if (nxt_1 != nxt_2):
                    return None

                if (next_op_cnot1 != next_op_cnot2):
                    return None

                if self.transfer_flag and (not mu.has_flag(next_op_cnot1)):
                    # Optimize only flagged operations
                    return None

                if self.transfer_flag:
                    mu.transfer_flags(circuit, op.qubits[0], index, nxt_1)

                return cirq.PointOptimizationSummary(
                    clear_span = nxt_1 - index + 1,  # Range of moments to affect.
                    clear_qubits = op.qubits,  # The set of qubits that should be cleared with each affected moment
                    new_operations = [] # The operations to replace
                )