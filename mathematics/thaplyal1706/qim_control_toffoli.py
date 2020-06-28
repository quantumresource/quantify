import cirq


class QimControlToffoli:
    def __init__(self, ctrl, B, A):
        self.ctrl = ctrl
        self.B = B
        self.A = A

    def construct_moments(self):
        moments = [cirq.TOFFOLI(self.ctrl, self.B[i], self.A[i]) for i in range(len(self.A))]
        return moments
