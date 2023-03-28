%% Clear all and close all
clear
clc
close all
warning off all
%% Setup file path
filepath = 'D:\OneDrive@sjtu.edu.cn\Courses\2021Spring\MechanicalAndElectricalSystems\DataReader\NeuronReader\NeuronReader\matlab\Zu7';
global JAKAzu7Tree
JAKAzu7Tree = JAKAzu7TreeModel(filepath); % Zu7 mesh model
JAKAzu7 = JAKAzu7().SerialRobot; % Zu7 robot model
%%
rcd = [0.5236   -0.8727   -0.5236   -2.7925   -2.0944    0.1745];
T = [    0         0         1    0.33
         1         0         0    0.57
         0         1         0    0.24
         0         0         0    1.0000];
T1 = [0.5721    0.4156    0.7071    0.5772
   -0.5721   -0.4156    0.7071   -0.2738
    0.5878   -0.8090         0    0.4193
         0         0         0         1];
q = [pi*18/19 -pi/5 pi/3 0 pi/7 0];
T2 = JAKAzu7.fkine(q);
q0 = JAKAzu7.ikine(T,'q0',rcd);
view(3)
JAKAzu7.plot(q0);
% JAKAzu7.plot([0 0 0 0 0 0]);
