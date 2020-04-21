import cirq

class RecycledGate(cirq.ops.SingleQubitGate):
    """
        This is a gate that is used as a placeholder in the diagrams
    """

    def __init__(self, name = "NoName"):
        self.name = name

    def __str__(self):
        return self.name