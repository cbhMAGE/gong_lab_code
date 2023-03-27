#LOG = "logs.txt"
#ls  2>&1 |tee $LOG
project_path="/home/tete/work/new"
cd $project_path || exit
curPath=$(pwd)
echo "Current path"$curPath
#
log_name="logs/acdf_train_log_p100_v50_s0.txt"
python -m spinup.algos.pytorch.acdf.acdf --exp_name AntACDF_p100_v50 -s 0 --epochs 1000 --pi-epochs 100 --vf-epochs 50 --cpu 1 2>&1 |tee $log_name
log_name="logs/acdf_train_log_p100_v50_s1.txt"
python -m spinup.algos.pytorch.acdf.acdf --exp_name AntACDF_p100_v50 -s 1 --epochs 1000 --pi-epochs 100 --vf-epochs 50 --cpu 1 2>&1 |tee $log_name
log_name="logs/acdf_train_log_p100_v50_s2.txt"
python -m spinup.algos.pytorch.acdf.acdf --exp_name AntACDF_p100_v50 -s 2 --epochs 1000 --pi-epochs 100 --vf-epochs 50 --cpu 1 2>&1 |tee $log_name