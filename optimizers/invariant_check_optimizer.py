from typing import (Dict, Callable, Iterable, Optional, Sequence, TYPE_CHECKING,
                    Tuple, cast)

from collections import defaultdict

import cirq

class InvariantCheckOptimizer(cirq.PointOptimizer):

    def __init__(self, invariant_function):
        # Call the super constructor
        super().__init__()
        # should this operate only on flagged operations?
        self.invariant_function = invariant_function

        self.const_val = None


    """
        For the sake of implementation simplicity - Copy/Paste with edits
    """
    def optimize_circuit(self, circuit: cirq.Circuit):
        frontier: Dict['Qid', int] = defaultdict(lambda: 0)
        i = 0

        # Store the value before optimization starts
        self.const_val = self.invariant_function(circuit)

        while i < len(circuit):  # Note: circuit may mutate as we go.
            for op in circuit[i].operations:
                # Don't touch stuff inserted by previous optimizations.
                if any(frontier[q] > i for q in op.qubits):
                    continue

                # Skip if an optimization removed the circuit underneath us.
                if i >= len(circuit):
                    continue
                # Skip if an optimization removed the op we're considering.
                if op not in circuit[i].operations:
                    continue
                opt = self.optimization_at(circuit, i, op)
                # Skip if the optimization did nothing.
                if opt is None:
                    continue

                # Clear target area, and insert new operations.
                circuit.clear_operations_touching(
                    opt.clear_qubits,
                    [e for e in range(i, i + opt.clear_span)])
                new_operations = self.post_clean_up(
                    cast(Tuple[cirq.ops.Operation], opt.new_operations))
                circuit.insert_at_frontier(new_operations, i, frontier)

                self.check_invariant(circuit)

            i += 1

    def check_invariant(self, circuit):
        """
            Add invariant check
        """
        current_val = self.invariant_function(circuit)
        # print("  invariant check -------> ", self.const_val, current_val)
        if self.const_val != current_val:
            raise ValueError("Something went wrong during optimisation. "
                         "Invariant {} changed from {} to {}"
                         .format(self.invariant_function,
                                 self.const_val, current_val))