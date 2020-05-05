# QUANTIFY


QUANTIFY is an alpha tool based on Google Cirq. It includes:
* a library of Toffoli decompositions
* novel optimisation strategies compatible with surface code layouts
* circuit structure analysis tools
* a work-in-progress library of arithmetic circuits
* bucket brigade QRAM circuits

QUANTIFY was developed as part of 
[https://arxiv.org/abs/2002.09340](https://arxiv.org/abs/2002.09340), where
QRAM circuits were decomposed into Clifford+T and their T gates parallelised.


Documentation, code and examples are WIP.


To create the VENV

`bash construct_cirq_environment.sh`

To use the .venv

`source .venv/bin/activate`

Examples are in the `examples` and `tests` folder.
