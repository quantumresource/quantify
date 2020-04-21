echo "Create venv ..."
python3 -m venv .venv

echo "Activate venv ..."
source .venv/bin/activate

echo "Install Cirq in venv ..."
python3 -m pip install -r requirements.txt
