@echo off
echo ---------------------------
echo = FANTASY DEMO UNIT TESTS =
echo ---------------------------

cd ..
python testing/common_inventory.py 1> NULL

python testing/client_avatar.py 1> NULL
python testing/cell_avatar.py   1> NULL
python testing/base_avatar.py   1> NULL

python testing/base_tradingsupervisor.py   1> NULL

cd testing
