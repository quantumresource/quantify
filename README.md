# QUANTIFY

This software is alpha version of the tool used to generate the results from 
[https://arxiv.org/abs/2002.09340](https://arxiv.org/abs/2002.09340)

That paper generates QRAM circuits as presented in `arxiv:1902.01329`, it decomposes
the circuits into Clifford+T and parallelises the T gates.

QUANTIFY is based on Google Cirq and includes:
* a library of Toffoli decompositions
* novel optimisation strategies compatible with surface code layouts
* circuit structure analysis tools
* a work-in-progress library of arithmetic circuits


Documentation, code and examples are WIP.




To create the VENV

`bash construct_cirq_environment.sh`

To use the .venv

`source .venv/bin/activate`
