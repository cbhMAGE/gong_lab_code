startTime = datestr(now,'yyyymmdd_HHMMSS_FFF');
frame = 1;

fid = fopen('d:\temp.txt','a');
fprintf(fid,'%s\n',startTime);
while frame < 10
    motion = [1.4153521 2.5848154 3.841562];
    angle = [1.4811 2.5871 3.5402 4.5487 5.5781 6.478];
    isCollide = 0;
    data2send = [frame motion angle isCollide];
    fprintf(fid,'%g ',data2send);
    fprintf(fid, '\n' );
    frame = frame + 1;
end
fclose(fid);
% fprintf(fid,'%s',a);