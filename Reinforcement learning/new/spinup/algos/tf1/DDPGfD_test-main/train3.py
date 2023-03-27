# E. Culurciello
# November 2020

# DDPGfd test from: https://github.com/MrSyee/pg-is-all-you-need/blob/master/06.DDPGfD.ipynb

import os
import pickle
import gym
import argparse
import numpy as np
from rl_modules.ddpg_agent import DDPGfDAgent
from rl_modules.utils import ActionNormalizer


def get_args():
    parser = argparse.ArgumentParser(description='DDPGfD test on Pendulum-v0')
    arg = parser.add_argument
    # env:
    #arg('--env_name', type=str, default='Pendulum-v0', help='environment name')
    arg('--env_name', type=str, default='Humanoid-v2', help='environment name')
    # train:
    arg('--seed', type=int, default=0, help='')
    arg('--num_frames', type=int, default=50000, help='')
    arg('--memory_size', type=int, default=100000, help='')
    arg('--batch_size', type=int, default=64, help='')
    #arg('--batch_size', type=int, default=128, help='')
    arg('--ou_noise_theta', type=float, default=1.0, help='')
    arg('--ou_noise_sigma', type=float, default=0.1, help='')
    arg('--initial_random_steps', type=int, default=10000, help='')
    arg('--n_step', type=int, default=3, help='')
    arg('--pretrain_step', type=int, default=5000, help='')
    arg('--save_dir', type=str, default='saved_models/', help='path to save the models')

    args = parser.parse_args()
    return args

args = get_args() # Holds all the input arguments
print(args)


def main():
  for args.seed in range(500,505):
    title = 'DDPGfD test'
    print('Environment name:', args.env_name)

    # create the dict for store the model
    if not os.path.exists(args.save_dir):
        os.mkdir(args.save_dir)

    env = gym.make(args.env_name)
    env = ActionNormalizer(env)
    env.seed(args.seed)

    #demo_path = "demo.pkl"
    demo_path = "HalfCheetah100.pickle"
    with open(demo_path, "rb") as f:
        alldata = pickle.load(f)
    new_data=[]
    for m in range(1,5):
      for j in range(1,len(alldata[m]['act_buf'])):
       transition=(alldata[m]['obs_buf'][j],alldata[m]['act_buf'][j],alldata[m]['rew_buf'][j],alldata[m]['obs2_buf'][j],alldata[m]['done_buf'][j])
       new_data.append(transition)
    #print(new_data)
   # args.demo=new_data
    args.demo=None
    # DDPGfD agent:
    agent = DDPGfDAgent(
        args,
        env,
    )
    agent.train(args.num_frames)
    agent.df.to_csv("Progress/Humanoid_progress_s%d.csv" % args.seed)


if __name__ == '__main__':
    main()
