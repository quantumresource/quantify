# QUANTIFY

QUANTIFY is a collection of tools used for the analysis and optimisation 
of quantum circuits. QUANTIFY is based on Google Cirq.

QUANTIFY includes:
* a library of arithmetic circuits
    - Shor's algorithm as formulated in [arXiv:1611.07995](https://arxiv.org/abs/1611.07995)
    - The T-count optimized integer multiplier from [arXiv:1706.05113](https://arxiv.org/pdf/1706.05113.pdf)
    - The quantum addition circuits from [arXiv:0910.2530](https://arxiv.org/abs/0910.2530)

* a library of Toffoli decompositions which probably covers all known Toffoli gate decompositions

* novel optimisation strategies compatible with surface code layouts

* circuit structure analysis tools
* bucket brigade QRAM circuits as used in 
[![arXiv](https://img.shields.io/badge/arXiv-2002.09340-b31b1b.svg)](https://arxiv.org/abs/2002.09340)
* an analysis of the scheduling of distillation procedures in surface
code layouts
[![arXiv](https://img.shields.io/badge/arXiv-1906.06400-b31b1b.svg)](https://arxiv.org/abs/1906.06400)


Documentation, code and examples are WIP.


To create the VENV

`bash construct_cirq_environment.sh`

To use the .venv

`source .venv/bin/activate`

Examples are in the `examples` and `tests` folder.
