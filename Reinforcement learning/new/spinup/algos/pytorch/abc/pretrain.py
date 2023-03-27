import inspect
from copy import deepcopy
import numpy as np
import torch
from torch.utils.data import DataLoader
from torch.optim import Adam
from torch.optim.rmsprop import RMSprop
import gym
import time

from ipdb import set_trace as tt

import spinup.algos.pytorch.abc.core as core
from spinup.utils.logx import EpochLogger
from spinup.utils.mpi_pytorch_cuda import setup_pytorch_for_mpi, sync_params, mpi_avg_grads
from spinup.utils.mpi_tools_cuda import mpi_fork, mpi_avg, proc_id, mpi_statistics_scalar, num_procs
from spinup.algos.pytorch.abc.demo_env import trainset

from spinup.algos.pytorch.abc.custom_saver import save_pi, save_vf
TOTAL_UPDATES = 750000

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

def Variable(var):
    return var.to(device)


SAVE_FREQ = [0, 1, 5, 10, 15, 20, 30, 40, 50, 100, 200, 500]

def pretrain(env_fn, actor_critic=core.MLPActorCritic, ac_kwargs=dict(), seed=0, epochs=50, batch_size=32,
             learning_rate=7e-4,
            logger_kwargs=dict(), save_freq=10, demo_file=""):

    setup_pytorch_for_mpi()
    logger = EpochLogger(**logger_kwargs)
    # locals() return all local variable
    logger.save_config(locals())
    # Random seed
    seed += 10000 * proc_id()
    torch.manual_seed(seed)
    np.random.seed(seed)
    env = env_fn()
    obs_dim = env.observation_space.shape
    act_dim = env.action_space.shape
    # demo environment
    training_set = trainset(demo_path=demo_file)
    training_loader = DataLoader(training_set, batch_size=batch_size, shuffle=True)

    model = actor_critic(env.observation_space, env.action_space, **ac_kwargs).to(device).pi
    model = model.to(device)
    optimizer = RMSprop(params=model.parameters(), lr=learning_rate, eps=1e-5, alpha=0.99, weight_decay=1e-4 )
    torch.nn.utils.clip_grad_norm(model.parameters(), max_norm=0.5, norm_type=2)
    MSE = True
    total_updates = 0
    for e in range(epochs):
        epoch_loss = 0
        for i, data in enumerate(training_loader):
            optimizer.zero_grad()
            obs, act = data
            pi = model._distribution(Variable(obs))
            if MSE:
                pred_act = pi.loc
                loss = ((pred_act - Variable(act)) ** 2).mean()

            epoch_loss += loss.item()
            loss.backward()
            optimizer.step()
            total_updates += 1
            if total_updates >= TOTAL_UPDATES:
                save_pi(output_dir=logger_kwargs.get('output_dir', "model"), itr=total_updates, paramenters=model)
                break
        print("Epoch {}, total_updates: {}, loss is: {}".format(e, total_updates, epoch_loss))
        if e % 10 == 0:
            save_pi(output_dir=logger_kwargs.get('output_dir', "model"), itr=total_updates, paramenters=model)


def get_default_args(func):
    signature = inspect.signature(func)
    return {
        k: v.default
        for k, v in signature.parameters.items()
        if v.default is not inspect.Parameter.empty
    }


def argprinter(**kwargs):
    for k in kwargs:
        print(k)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    # parser.add_argument('--env', type=str, default='CartPole-v0')
    parser.add_argument('--env', type=str, default='Ant-v2')
    parser.add_argument('--hid', type=int, default=64)
    parser.add_argument('--l', type=int, default=2)
    # parser.add_argument('--gamma', type=float, default=0.99)
    parser.add_argument('--seed', '-s', type=int, default=0)
    parser.add_argument('--cpu', type=int, default=1)
    parser.add_argument('--bs', type=int, default=64)
    parser.add_argument('--exp_name', type=str, default='test')
    parser.add_argument('--demo-file', type=str, default='data/Ant/Ant1000.pickle')
    parser.add_argument('--epochs', type=int, default=50)
    args = parser.parse_args()

    mpi_fork(args.cpu)  # run parallel code with mpi
    from spinup.utils.run_utils import setup_logger_kwargs
    logger_kwargs = setup_logger_kwargs(args.exp_name, args.seed)
    pretrain(lambda: gym.make(args.env), actor_critic=core.MLPActorCritic,
             ac_kwargs=dict(hidden_sizes=[args.hid] * args.l),
             seed=args.seed,
             epochs=args.epochs, batch_size = args.bs,
             logger_kwargs=logger_kwargs, demo_file=args.demo_file)
