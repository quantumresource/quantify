import cirq

import utils.misc_utils as mu

from .transfer_flag_optimizer import TransferFlagOptimizer

class CancelNghHadamards(TransferFlagOptimizer):

    def optimization_at(self, circuit, index, op):

        if not (isinstance(op, cirq.GateOperation) and (op.gate == cirq.H)):
            return None

        if self.transfer_flag and (not mu.has_flag(op)):
            # Optimize only flagged operations
            return None

        n_idx = circuit.next_moment_operating_on(op.qubits, index + 1)
        if n_idx is None:
            return None

        next_op = circuit.operation_at(op.qubits[0], n_idx)

        if next_op.gate == cirq.H:

            if self.transfer_flag and (not mu.has_flag(next_op)):
                # Optimize only flagged operations
                return None

            if self.transfer_flag:
                mu.transfer_flags(circuit, op.qubits[0], index, n_idx)

            return cirq.PointOptimizationSummary(clear_span= n_idx - index + 1,
                                            clear_qubits=op.qubits,
                                            new_operations=[])

        return None