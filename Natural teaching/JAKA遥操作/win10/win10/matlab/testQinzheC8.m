RbtC8 = QinzheC8().SerialRobot;
T =  [-1         0         0         0;
         0         0        -1     0.354;
         0        -1         0     1.215;
         0         0         0         1];
T(1:3,4) = [0.2681   -0.4219    0.5701].';
q = RbtC8.ikine(T)