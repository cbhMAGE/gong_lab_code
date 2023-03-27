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
env="Humanoid"
root_dir="data/"$env"/"

mkdir $root_dir


pretrain_name=$env"Pretrain"
#pretrain_model_path=$root_dir$pretrain_name"/"$pretrain_name"_s"$seed"/"

exp_file="data/"$env"SAC/"$env"SAC_s0/"
# create demo dataset
demo_output_file=$root_dir$env$demo_episode".pickle"
#python -m spinup.utils.test_policy $exp_file --episodes $demo_episode --demo-file $demo_output_file

# path to pretrain model:
for s in {5..10};do
  python -m spinup.algos.pytorch.acdf_cuda.pretrain  --seed $s --pi-epochs $pi_pretrain_epochs --vf-epochs $vf_pretrain_epochs --demo-file $demo_output_file --exp_name $pretrain_name  --cpu 4 --env $env"-v2" 2>&1 |tee $env"Pretrain.txt"
  pretrain_model_path="data/"$env"Pretrain/"$env"Pretrain_s"$s"/pyt_save/"
  for itr in {20,50};do
    pi_itr=$itr
    vf_itr=$itr
    python -m spinup.algos.pytorch.acdf_cuda.acdf  --seed $s --exp_name $env"ACDF_pi"$pi_itr"_vf"$vf_itr --pi-itr $pi_itr --vf-itr $vf_itr --epochs $train_epochs --pretrain-model $pretrain_model_path --cpu 4 --env $env"-v2"
  done
done