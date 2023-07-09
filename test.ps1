mkdir record
python main.py -i .\examples\and1.cnf > .\record\and1.txt
echo "and1 Done"
python main.py -i .\examples\and2.cnf > .\record\and2.txt
echo "and2 Done"
python main.py -i .\examples\bmc-2.cnf > .\record\bmc-2.txt
echo "bmc-2 Done"
python main.py -i .\examples\bmc-7.cnf > .\record\bmc-7.txt
echo "bmc-7 Done"
python main.py -i .\examples\bmc-1.cnf > .\record\bmc-1.txt
echo "bmc-1 Done"