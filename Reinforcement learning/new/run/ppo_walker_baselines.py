import subprocess


def main():
    message = 'python -m spinup.algos.pytorch.ppo.ppo --exp_name Walker2dPPO --cpu 4 --epochs 1000'
    python_command = message.split(" ")
    for i in range(3, 10):
        local_command = python_command + ['--seed', str(i), '--env', 'Walker2d-v2']
        print(local_command)
        ok = subprocess.call(local_command)

if __name__ == "__main__":
    main()