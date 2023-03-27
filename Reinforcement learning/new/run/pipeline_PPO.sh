# change dir to the working space
project_path="/home/tete/work/new"
cd $project_path || exit
curPath=$(pwd)

python -m run.ppo_ant_baselines
python -m run.ppo_halfche_baselines
python -m run.ppo_hopper_baselines
python -m run.ppo_humanoid_baselines
python -m run.ppo_swimmer_baselines
python -m run.ppo_walker_baselines