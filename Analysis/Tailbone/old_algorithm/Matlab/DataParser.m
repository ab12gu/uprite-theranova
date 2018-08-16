%% extract accel data
[fileName, pathName, ~] = uigetfile('*.txt'); 
accel = extractUpRiteData([pathName, fileName]);
%% extract gyro data
[fileName, pathName, ~] = uigetfile('*.txt'); 
gyro = extractUpRiteData([pathName, fileName]);
%% extract mag data
[fileName, pathName, ~] = uigetfile('*.txt'); 
mag = extractUpRiteData([pathName, fileName]);
%% extract altitude data
[fileName, pathName, ~] = uigetfile('*.txt'); 
altitude = extractUpRiteData([pathName, fileName]);
