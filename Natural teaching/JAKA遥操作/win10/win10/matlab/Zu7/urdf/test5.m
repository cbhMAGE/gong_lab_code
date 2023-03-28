client2vs = tcpclient('localhost',5000);
while 1
    sendtxt = 'shackhand';
    write(client2vs, sendtxt);
    disp(client2vs.NumBytesWritten);
    while client2vs.NumBytesAvailable == 0
    end
    disp(client2vs.NumBytesAvailable);
    recvData = read(client2vs);
%     recvData = read(client2vs)
%     disp(length(recvData));
%     if length(recvData) ~= 32
%         continue
%     end
%     disp("Receive time: " + datestr(now,'mmmm dd,yyyy HH:MM:SS.FFF'))
%     recv1 = dec2hex(recvData);
%     recv2 = [];
%     for i = 1:length(recv1)
%         recv2 = [recv2,recv1(i,:)]; %小端模式
%     end
%     count = 0;
% %     motion = [0 0 0]; %转化成double
%     recvData = [0 0 0 0];
%     while count < length(recv1)/8
%         recvData(count+1) = hex2num(recv2(count*16+1:count*16+16));
%         count = count + 1;
%     end
%     disp(recvData);

end