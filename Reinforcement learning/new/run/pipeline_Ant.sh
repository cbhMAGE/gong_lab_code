# change dir to the working space
project_path="/home/tete/work/new"
cd $project_path || exit
curPath=$(pwd)

declare  -i train_epochs=1000
declare -i demo_episode=1000
declare -i pi_pretrain_epochs=60
declare -i vf_pretrain_epochs=60
declare -i seed=0
pi_itr=1
vf_itr=1
env="Ant"
root_dir="data/"$env"/"

mkdir $root_dir


pretrain_name=$env"Pretrain"
#pretrain_model_path=$root_dir$pretrain_name"/"$pretrain_name"_s"$seed"/"
# Parameters:
#echo "--------------------------------------------------------"
#echo "--------------------------------------------------------"
#echo "Current path"$curPath
#echo "Expert model path: "$exp_file
#echo "Output dir for demo data: "$demo_output_file
#echo "Pretrain model path: "$pretrain_model_path
#echo "--------------------------------------------------------"
#echo "--------------------------------------------------------"
#
#python -m spinup.algos.pytorch.sac.sac --env $env"-v2" --epochs $train_epochs --exp_name $env"SAC" --seed 0
#python -m spinup.algos.pytorch.sac.sac --env $env"-v2" --epochs $train_epochs --exp_name $env"SAC" --seed 1
#python -m spinup.algos.pytorch.sac.sac --env $env"-v2" --epochs $train_epochs --exp_name $env"SAC" --seed 2
#python -m spinup.algos.pytorch.sac.sac --env $env"-v2" --epochs $train_epochs --exp_name $env"SAC" --seed 3
#python -m spinup.algos.pytorch.sac.sac --env $env"-v2" --epochs $train_epochs --exp_name $env"SAC" --seed 4

exp_file="data/"$env"SAC/"$env"SAC_s0/"
# create demo dataset
demo_output_file=$root_dir$env$demo_episode".pickle"
#python -m spinup.utils.test_policy $exp_file --episodes $demo_episode --demo-file $demo_output_file
# screen -S halfcheetah
# bash run/pipeline_HalfCheetah.sh
## pretrain the model
for s in {5..10};do
  python -m spinup.algos.pytorch.acdf_cuda.pretrain  --seed $s --pi-epochs $pi_pretrain_epochs --vf-epochs $vf_pretrain_epochs --demo-file $demo_output_file --exp_name $pretrain_name  --cpu 4 --env $env"-v2" 2>&1 |tee $env"Pretrain.txt"
done
#
#python -m spinup.algos.pytorch.acdf_cuda.pretrain  --pi-epochs $pi_pretrain_epochs --vf-epochs $vf_pretrain_epochs --demo-file $demo_output_file --exp_name $pretrain_name  --cpu 4 --env $env"-v2" 2>&1 |tee $env"Pretrain.txt"
#python -m spinup.algos.pytorch.acdf_cuda.pretrain  --pi-epochs $pi_pretrain_epochs --vf-epochs $vf_pretrain_epochs --demo-file $demo_output_file --exp_name $pretrain_name  --cpu 4 --env $env"-v2" 2>&1 |tee $env"Pretrain.txt"
#python -m spinup.algos.pytorch.acdf_cuda.pretrain  --pi-epochs $pi_pretrain_epochs --vf-epochs $vf_pretrain_epochs --demo-file $demo_output_file --exp_name $pretrain_name  --cpu 4 --env $env"-v2" 2>&1 |tee $env"Pretrain.txt"
#mv "data/"$pretrain_name $root_dir"/"
# path to pretrain model:
for s in {5..10};do
  pretrain_model_path="data/"$env"Pretrain/"$env"Pretrain_s"$s"/pyt_save/"
  for itr in {20,50};do
    pi_itr=$itr
    vf_itr=$itr
    python -m spinup.algos.pytorch.acdf_cuda.acdf  --seed $s --exp_name $env"ACDF_pi"$pi_itr"_vf"$vf_itr --pi-itr $pi_itr --vf-itr $vf_itr --epochs $train_epochs --pretrain-model $pretrain_model_path --cpu 4 --env $env"-v2"
  done
done



#pi_itr=5
#vf_itr=5
#python -m spinup.algos.pytorch.acdf_cuda.acdf  --seed 0 --exp_name $env"ACDF_pi"$pi_itr"_vf"$vf_itr --pi-itr $pi_itr --vf-itr $vf_itr --epochs $train_epochs --pretrain-model $pretrain_model_path --cpu 1 --env $env"-v2"
#python -m spinup.algos.pytorch.acdf_cuda.acdf  --seed 1 --exp_name $env"ACDF_pi"$pi_itr"_vf"$vf_itr --pi-itr $pi_itr --vf-itr $vf_itr --epochs $train_epochs --pretrain-model $pretrain_model_path --cpu 1 --env $env"-v2"
#python -m spinup.algos.pytorch.acdf_cuda.acdf  --seed 2 --exp_name $env"ACDF_pi"$pi_itr"_vf"$vf_itr --pi-itr $pi_itr --vf-itr $vf_itr --epochs $train_epochs --pretrain-model $pretrain_model_path --cpu 1 --env $env"-v2"
##python -m spinup.algos.pytorch.acdf_cuda.acdf  --seed 3 --exp_name $env"ACDF_pi"$pi_itr"_vf"$vf_itr --pi-itr $pi_itr --vf-itr $vf_itr --epochs $train_epochs --pretrain-model $pretrain_model_path --cpu 1 --env $env"-v2"
##python -m spinup.algos.pytorch.acdf_cuda.acdf  --seed 4 --exp_name $env"ACDF_pi"$pi_itr"_vf"$vf_itr --pi-itr $pi_itr --vf-itr $vf_itr --epochs $train_epochs --pretrain-model $pretrain_model_path --cpu 1 --env $env"-v2"
#
#pi_itr=10
#vf_itr=10
#python -m spinup.algos.pytorch.acdf_cuda.acdf  --seed 0 --exp_name $env"ACDF_pi"$pi_itr"_vf"$vf_itr --pi-itr $pi_itr --vf-itr $vf_itr --epochs $train_epochs --pretrain-model $pretrain_model_path --cpu 1 --env $env"-v2"
#python -m spinup.algos.pytorch.acdf_cuda.acdf  --seed 1 --exp_name $env"ACDF_pi"$pi_itr"_vf"$vf_itr --pi-itr $pi_itr --vf-itr $vf_itr --epochs $train_epochs --pretrain-model $pretrain_model_path --cpu 1 --env $env"-v2"
#python -m spinup.algos.pytorch.acdf_cuda.acdf  --seed 2 --exp_name $env"ACDF_pi"$pi_itr"_vf"$vf_itr --pi-itr $pi_itr --vf-itr $vf_itr --epochs $train_epochs --pretrain-model $pretrain_model_path --cpu 1 --env $env"-v2"
##python -m spinup.algos.pytorch.acdf_cuda.acdf  --seed 3 --exp_name $env"ACDF_pi"$pi_itr"_vf"$vf_itr --pi-itr $pi_itr --vf-itr $vf_itr --epochs $train_epochs --pretrain-model $pretrain_model_path --cpu 1 --env $env"-v2"
##python -m spinup.algos.pytorch.acdf_cuda.acdf  --seed 4 --exp_name $env"ACDF_pi"$pi_itr"_vf"$vf_itr --pi-itr $pi_itr --vf-itr $vf_itr --epochs $train_epochs --pretrain-model $pretrain_model_path --cpu 1 --env $env"-v2"
#
#pi_itr=20
#vf_itr=20
#python -m spinup.algos.pytorch.acdf_cuda.acdf  --seed 0 --exp_name $env"ACDF_pi"$pi_itr"_vf"$vf_itr --pi-itr $pi_itr --vf-itr $vf_itr --epochs $train_epochs --pretrain-model $pretrain_model_path --cpu 1 --env $env"-v2"
#python -m spinup.algos.pytorch.acdf_cuda.acdf  --seed 1 --exp_name $env"ACDF_pi"$pi_itr"_vf"$vf_itr --pi-itr $pi_itr --vf-itr $vf_itr --epochs $train_epochs --pretrain-model $pretrain_model_path --cpu 1 --env $env"-v2"
#python -m spinup.algos.pytorch.acdf_cuda.acdf  --seed 2 --exp_name $env"ACDF_pi"$pi_itr"_vf"$vf_itr --pi-itr $pi_itr --vf-itr $vf_itr --epochs $train_epochs --pretrain-model $pretrain_model_path --cpu 1 --env $env"-v2"
##python -m spinup.algos.pytorch.acdf_cuda.acdf  --seed 3 --exp_name $env"ACDF_pi"$pi_itr"_vf"$vf_itr --pi-itr $pi_itr --vf-itr $vf_itr --epochs $train_epochs --pretrain-model $pretrain_model_path --cpu 1 --env $env"-v2"
##python -m spinup.algos.pytorch.acdf_cuda.acdf  --seed 4 --exp_name $env"ACDF_pi"$pi_itr"_vf"$vf_itr --pi-itr $pi_itr --vf-itr $vf_itr --epochs $train_epochs --pretrain-model $pretrain_model_path --cpu 1 --env $env"-v2"
#
#pi_itr=50
#vf_itr=50
#python -m spinup.algos.pytorch.acdf_cuda.acdf  --seed 0 --exp_name $env"ACDF_pi"$pi_itr"_vf"$vf_itr --pi-itr $pi_itr --vf-itr $vf_itr --epochs $train_epochs --pretrain-model $pretrain_model_path --cpu 1 --env $env"-v2"
#python -m spinup.algos.pytorch.acdf_cuda.acdf  --seed 1 --exp_name $env"ACDF_pi"$pi_itr"_vf"$vf_itr --pi-itr $pi_itr --vf-itr $vf_itr --epochs $train_epochs --pretrain-model $pretrain_model_path --cpu 1 --env $env"-v2"
#python -m spinup.algos.pytorch.acdf_cuda.acdf  --seed 2 --exp_name $env"ACDF_pi"$pi_itr"_vf"$vf_itr --pi-itr $pi_itr --vf-itr $vf_itr --epochs $train_epochs --pretrain-model $pretrain_model_path --cpu 1 --env $env"-v2"
##python -m spinup.algos.pytorch.acdf_cuda.acdf  --seed 3 --exp_name $env"ACDF_pi"$pi_itr"_vf"$vf_itr --pi-itr $pi_itr --vf-itr $vf_itr --epochs $train_epochs --pretrain-model $pretrain_model_path --cpu 1 --env $env"-v2"
##python -m spinup.algos.pytorch.acdf_cuda.acdf  --seed 4 --exp_name $env"ACDF_pi"$pi_itr"_vf"$vf_itr --pi-itr $pi_itr --vf-itr $vf_itr --epochs $train_epochs --pretrain-model $pretrain_model_path --cpu 1 --env $env"-v2"
#
#pi_itr=100
#vf_itr=100
#python -m spinup.algos.pytorch.acdf_cuda.acdf  --seed 0 --exp_name $env"ACDF_pi"$pi_itr"_vf"$vf_itr --pi-itr $pi_itr --vf-itr $vf_itr --epochs $train_epochs --pretrain-model $pretrain_model_path --cpu 1 --env $env"-v2"
#python -m spinup.algos.pytorch.acdf_cuda.acdf  --seed 1 --exp_name $env"ACDF_pi"$pi_itr"_vf"$vf_itr --pi-itr $pi_itr --vf-itr $vf_itr --epochs $train_epochs --pretrain-model $pretrain_model_path --cpu 1 --env $env"-v2"
#python -m spinup.algos.pytorch.acdf_cuda.acdf  --seed 2 --exp_name $env"ACDF_pi"$pi_itr"_vf"$vf_itr --pi-itr $pi_itr --vf-itr $vf_itr --epochs $train_epochs --pretrain-model $pretrain_model_path --cpu 1 --env $env"-v2"
##python -m spinup.algos.pytorch.acdf_cuda.acdf  --seed 3 --exp_name $env"ACDF_pi"$pi_itr"_vf"$vf_itr --pi-itr $pi_itr --vf-itr $vf_itr --epochs $train_epochs --pretrain-model $pretrain_model_path --cpu 1 --env $env"-v2"
##python -m spinup.algos.pytorch.acdf_cuda.acdf  --seed 4 --exp_name $env"ACDF_pi"$pi_itr"_vf"$vf_itr --pi-itr $pi_itr --vf-itr $vf_itr --epochs $train_epochs --pretrain-model $pretrain_model_path --cpu 1 --env $env"-v2"
#
#pi_itr=200
#vf_itr=200
#python -m spinup.algos.pytorch.acdf_cuda.acdf  --seed 0 --exp_name $env"ACDF_pi"$pi_itr"_vf"$vf_itr --pi-itr $pi_itr --vf-itr $vf_itr --epochs $train_epochs --pretrain-model $pretrain_model_path --cpu 1 --env $env"-v2"
#python -m spinup.algos.pytorch.acdf_cuda.acdf  --seed 1 --exp_name $env"ACDF_pi"$pi_itr"_vf"$vf_itr --pi-itr $pi_itr --vf-itr $vf_itr --epochs $train_epochs --pretrain-model $pretrain_model_path --cpu 1 --env $env"-v2"
#python -m spinup.algos.pytorch.acdf_cuda.acdf  --seed 2 --exp_name $env"ACDF_pi"$pi_itr"_vf"$vf_itr --pi-itr $pi_itr --vf-itr $vf_itr --epochs $train_epochs --pretrain-model $pretrain_model_path --cpu 1 --env $env"-v2"
##python -m spinup.algos.pytorch.acdf_cuda.acdf  --seed 3 --exp_name $env"ACDF_pi"$pi_itr"_vf"$vf_itr --pi-itr $pi_itr --vf-itr $vf_itr --epochs $train_epochs --pretrain-model $pretrain_model_path --cpu 1 --env $env"-v2"
##python -m spinup.algos.pytorch.acdf_cuda.acdf  --seed 4 --exp_name $env"ACDF_pi"$pi_itr"_vf"$vf_itr --pi-itr $pi_itr --vf-itr $vf_itr --epochs $train_epochs --pretrain-model $pretrain_model_path --cpu 1 --env $env"-v2"
#
#pi_itr=0
#vf_itr=0
#python -m spinup.algos.pytorch.acdf_cuda.acdf  --seed 0 --exp_name $env"ACDF_pi"$pi_itr"_vf"$vf_itr --pi-itr $pi_itr --vf-itr $vf_itr --epochs $train_epochs --pretrain-model $pretrain_model_path --cpu 1 --env $env"-v2"
#python -m spinup.algos.pytorch.acdf_cuda.acdf  --seed 1 --exp_name $env"ACDF_pi"$pi_itr"_vf"$vf_itr --pi-itr $pi_itr --vf-itr $vf_itr --epochs $train_epochs --pretrain-model $pretrain_model_path --cpu 1 --env $env"-v2"
#python -m spinup.algos.pytorch.acdf_cuda.acdf  --seed 2 --exp_name $env"ACDF_pi"$pi_itr"_vf"$vf_itr --pi-itr $pi_itr --vf-itr $vf_itr --epochs $train_epochs --pretrain-model $pretrain_model_path --cpu 1 --env $env"-v2"
##python -m spinup.algos.pytorch.acdf_cuda.acdf  --seed 3 --exp_name $env"ACDF_pi"$pi_itr"_vf"$vf_itr --pi-itr $pi_itr --vf-itr $vf_itr --epochs $train_epochs --pretrain-model $pretrain_model_path --cpu 1 --env $env"-v2"
##python -m spinup.algos.pytorch.acdf_cuda.acdf  --seed 4 --exp_name $env"ACDF_pi"$pi_itr"_vf"$vf_itr --pi-itr $pi_itr --vf-itr $vf_itr --epochs $train_epochs --pretrain-model $pretrain_model_path --cpu 1 --env $env"-v2"
