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
% client2ros = tcpclient('192.168.2.112',6666);
% client2ros = tcpclient('192.168.67.41',6666);
client2ros = tcpclient('10.161.117.190',6666);
client2vs = tcpclient('localhost',5000);
%% 设置连接参数，要连接的地址为127.0.0.1(即本地主机)，端口号为5000，作为客户机连接。
% Client_sensor=tcpip('127.0.0.1',5000,'NetworkRole','client');
% Client_sensor.BytesAvailable;
% This is reserved for ros
% Client_ros=tcpip('127.0.0.1',4000,'NetworkRole','client');
% Client_ros.BytesAvailable;
%% 建立连接，建立完成后进行下一步，否则报错
tic
figure(1)

% While loop setup
T_dir = [-1 0 0 0 0 0;
         0 -1 0 0 0 0;
         0 0  1 0 0 0;
         0 0 0 -1 0 0;
         0 0 0 0 -1 0;
         0 0 0 0 0  1];
rcd = [0.5236   -0.8727   -0.5236   -2.7925   -2.0944    0.1745];
q_last = T_dir * rcd.';
v_last = zeros(6,1);
pose_mat = [0 0 1; 1 0 0; 0 1 0];
T0 = JAKAzu7.fkine(rcd);
q_tar_tmp = rcd;
% motion0 = T0(4,1:3).';
motion0 = T0.t;
motion0 = motion0.';
cnt = 0;
text_position = [0 0 0];

theta = -pi/3;
Rot = [cos(theta) -sin(theta) 0; sin(theta) cos(theta) 0; 0 0 1];
%% Data storage
isFirstInput = 1;
frame = 1;
fid = fopen('d:\temp.txt','w');
%%
while 1
    %---------------------Sensor Communication Start------------------% 
    disp("--- Client ---")
    disp('Connected ')

    % 发送字符串
    sendtxt = 'shackhand';
    writeline(client2vs, sendtxt);
    disp(client2vs.NumBytesAvailable);
    while client2vs.NumBytesAvailable == 0
    end
    recvData = read(client2vs);
%     recvData = read(client2vs)
%     disp(length(recvData));
    if length(recvData) ~= 32
        continue
    end
    disp("Receive time: " + datestr(now,'mmmm dd,yyyy HH:MM:SS.FFF'))
    recv1 = dec2hex(recvData);
    recv2 = [];
    for i = 1:length(recv1)
        recv2 = [recv2,recv1(i,:)]; %小端模式
    end
    count = 0;
%     motion = [0 0 0]; %转化成double
    recvData = [0 0 0 0];
    while count < length(recv1)/8
        recvData(count+1) = hex2num(recv2(count*16+1:count*16+16));
        count = count + 1;
    end
    
    isReady = recvData(1);
    motion = recvData(2:4);

    %--------------Joint Angle Calculation & Control Start--------------%
    if (isReady > 50.0) && (size(motion,2) == 3) % Is sensor msg complete?
        if isFirstInput
            startTime = datestr(now,'yyyymmdd_HHMMSS_FFF');
            fprintf(fid,'%s\n',startTime);
            isFirstInput = 0;
        end
        
        % Sensor pose revise
        motion =[-motion(1) motion(3) motion(2)];
        motionOri = motion;
            % Adjust offset
        motion = Rot * motion.';
        motion = motion.';
            disp(motion)
        motion = motion * 1.1;
%         motion = motion + [0 0 0.2];
        % Ignore first 10 msg
        if cnt >= 10
            motion = motion + bias;
            T = [pose_mat, motion.'; 0 0 0 1];
            q_tar_tmp = JAKAzu7.ikine(T,'q0',rcd);
            if size(q_tar_tmp,2) == 6
                % re-scale to joint angle range
                if (q_tar_tmp(2) > pi/2)
                    q_tar_tmp(2) = q_tar_tmp(2) - 2 * pi;
                end
                if (q_tar_tmp(4) > pi/2)
                    q_tar_tmp(4) = q_tar_tmp(4) - 2 * pi;
                end
                disp(q_tar_tmp);
                q_tar = T_dir * q_tar_tmp.';
                [isConfigInCollision, q_plan, v_plan] = Collision_Detect(q_last, v_last, q_tar);
                q_last = q_plan;
                v_last = v_plan;

                clf
                view(3)
                if (isConfigInCollision == 1)
                    text(0,0,0,'Collision','FontSize',50);
                elseif (isConfigInCollision == 2)
                    text(0,0,0,'Too Fast','FontSize',50);
                elseif (isConfigInCollision == -1)
                    text(0,0,0,'Danger','FontSize',50);
                else
                    text(0,0,0,'Safe','FontSize',50);
                end 
                q_plan_tmp = T_dir*q_plan;
%                 JAKAzu7.plot(q_plan_tmp.');
%               with collision detect
                data = [0 q_plan.'];
%               without collision detect
%                 data = [0 q_tar.'];
                write(client2ros, data);
    %             show(JAKAzu7Tree,q_tar,'visual','off','collision','on');
                data2save = [frame motionOri motionOri/2 q_plan.' isConfigInCollision];
                fprintf(fid,'%g ',data2save);
                fprintf(fid, '\n' );
            else
                clf
                view(3)
                text(0,0,0,'No Solution','FontSize',50);
            end
            frame = frame + 1;
        % Use the 10th to calculate bias
        elseif cnt < 10
            bias = motion0 - motion;
            motion = motion0;
            T = [pose_mat, motion.'; 0 0 0 1];
            q_tar_tmp = JAKAzu7.ikine(T,'q0',rcd);
            if size(q_tar_tmp,2) == 6
                disp(q_tar_tmp);
                % re-scale to joint angle range
                if (q_tar_tmp(2) > pi/2)
                    q_tar_tmp(2) = q_tar_tmp(2) - 2 * pi;
                end
                if (q_tar_tmp(4) > pi/2)
                    q_tar_tmp(4) = q_tar_tmp(4) - 2 * pi;
                end
                % joint angle direction revise
                q_tar = T_dir * q_tar_tmp.';
                q_last = q_tar;
                v_last = zeros(6,1);
                cnt = cnt + 1;
            end
        end
    else
        clf
        view(3)
        text(0,0,0,'Not Ready','FontSize',50);
    end
    disp("Finish time: " + datestr(now,'mmmm dd,yyyy HH:MM:SS.FFF'))
    disp(motion)
    % 关闭客户端
end
toc
clear client2ros
clear client2vs