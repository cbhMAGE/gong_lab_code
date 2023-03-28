clear
clc
close all
warning off all
filepath = 'D:\OneDrive@sjtu.edu.cn\Courses\2021Spring\MechanicalAndElectricalSystems\DataReader\NeuronReader\NeuronReader\matlab\Zu7';
global JAKAzu7Tree
JAKAzu7Tree = JAKAzu7TreeModel(filepath); % Zu7 mesh model
JAKAzu7 = JAKAzu7().SerialRobot; % Zu7 robot model
%%
q = [ 1.2709
    0.9821
   -1.3894
   -2.3714+pi
   -1.2709
    0.0000];
q0 = [0.9717
   -0.7604
   -0.0991
    0.6613
    0.9717
   -0.0000].';
q0 = [pi/4 -pi/2 pi/4 pi/2 pi/7 0];
q1 = [-pi/4 pi/2 pi/4 -pi/2 -pi/7 0];
% q0=zeros(1,6);
% q1=q0;
% Joint1 相反; Joint2相反；Joint3相同；Joint4相反；Joint5相反；6无所谓
motion = [-0.0102    0.7563    0.1958];
T = [[-1 0 0; 0 0 -1; 0 -1 0], motion.'; 0 0 0 1];
% q0 = JAKAzu7.ikine(T);
figure(1)
view(3)
JAKAzu7.plot(q0);
figure(2)
show(JAKAzu7Tree,q1.','visual','off','collision','on');
checkCollision(JAKAzu7Tree,q1.','Exhaustive','on')