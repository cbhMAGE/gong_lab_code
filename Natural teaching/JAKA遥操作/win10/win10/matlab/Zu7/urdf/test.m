% filepath = 'D:\00 SJTU Master Course\Spring 2021\Mechatronics\Collision Detect\Zu7';
% global robot
% robot = JAKAzu7TreeModel(filepath);
% %% 
% [outputArg1,outputArg2] = test2(1,2);
% rbt = JAKAzu7().SerialRobot;
q_tar = [0 0 0 0 0 0];
T = [[1 0 0; 0 0 1; 0 -1 0], [0.4156    0.6424    0.4660].'; 0 0 0 1];
JAKAzu7.ikine(T)
%%
figure(1)
view(3)
rbt.plot(q_tar);