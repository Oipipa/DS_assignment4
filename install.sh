set -e
python -m venv env
source env/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo "Run:  env/bin/python -m queue_daemon"
