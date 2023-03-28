%%
clear
clc
close all
warning off all
%% 设置连接参数，要连接的地址为127.0.0.1(即本地主机)，端口号为5000，作为客户机连接。
Client=tcpip('127.0.0.1',5000,'NetworkRole','client');
% Client.set(
Client.BytesAvailable;
%%
RbtC8 = QinzheC8().SerialRobot;
%% 建立连接，建立完成后进行下一步，否则报错
tic
time = 5;
delay = 0.5; % 触发延迟
figure(1)
view(3)

% for t = 0:delay:40
%     while toc < t
%     end
while 1
    fopen(Client);%与一个服务器建立连接，直到建立完成返回，否则报错。
    disp("--- Client ---")
    disp('Connected ')
    % 发送字符串
    sendtxt = 'shackhand';
    fprintf(Client,sendtxt);
    % 接收字符串
    while(1)
        nBytes = get(Client,'BytesAvailable');
        if nBytes>0
            break;
        end
    end
    recv=fread(Client,Client.BytesAvailable,'char');
    
    disp("Receive time: " + datestr(now,'mmmm dd,yyyy HH:MM:SS.FFF'))
    recv1 = dec2hex(recv);
    recv2 = [];
    for i = 1:length(recv1)
        recv2 = [recv2,recv1(i,:)]; %小端模式
    end
    
    count = 0;
    motion = []; %转化成double
    
    while count < length(recv1)/8
        motion = [motion,hex2num(recv2(count*16+1:count*16+16))];
        count = count + 1;
    end
     if size(motion,2) == 6
       RbtC8.plot(motion);
     end
    
    
%     motion = motion * [];
    disp("Finish time: " + datestr(now,'mmmm dd,yyyy HH:MM:SS.FFF'))
    disp(motion)
    % 关闭客户端
    fclose(Client);
end
toc