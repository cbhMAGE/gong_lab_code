% server1 = tcpserver(6666);

%% 设置连接参数，要连接的地址为127.0.0.1(即本地主机)，端口号为5000，作为客户机连接。
Client=tcpip('10.161.117.190',6666,'NetworkRole','client');
% Client=tcpip('127.0.0.1',6666,'NetworkRole','client');

% Client.set(
% Client.BytesAvailable;
tic
fopen(Client);%与一个服务器建立连接，直到建立完成返回，否则报错。
% sprintf("成功建立连接")
for t = 0:0.052:20
    while toc < t
    end
%     fopen(Client);%与一个服务器建立连接，直到建立完成返回，否则报错。
    disp("--- Client ---")
    
    disp('Connected ')
    % 发送字符串
    sendtxt = 'I love you';
    fprintf(Client,sendtxt);
    % 接收字符串
%     Client.BytesAvailable;
%     pause(0.02);
%     disp(Client.BytesAvailable);
%     while(1)
%         nBytes = get(Client,'BytesAvailable');
%         if nBytes>0
%             break;
%         end
%     end
%     recv=fread(Client,Client.BytesAvailable,'char');
%     
%     disp("Receive time: " + datestr(now,'mmmm dd,yyyy HH:MM:SS.FFF'))
%     recv1 = dec2hex(recv);
%     recv2 = [];
%     for i = 1:length(recv1)
%         recv2 = [recv2,recv1(i,:)]; %小端模式
%     end
%     count = 0;
%     motion = []; %转化成double
%     while count < length(recv1)/8
%         motion = [motion,hex2num(recv2(count*16+1:count*16+16))];
%         count = count + 1;
%     end
%     if size(motion,2) == 6
%        RbtC8.plot(motion);
%     end
%     
%     
% %     motion = motion * [];
    disp("Finish time: " + datestr(now,'mmmm dd,yyyy HH:MM:SS.FFF'))
%     if(server1.NumBytesAvailable())
%         msg = readline(server1);
%         disp(msg);
%     end
end
% 关闭客户端

fclose(Client);

toc

% sendtxt = 'shackhand';
% fprintf(Client,sendtxt);
% fclose(Client);