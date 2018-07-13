%% extract data
folder_name = uigetdir('','Select the folder containing all sensor data')
% extract accel data 
accel = extractUpRiteData([folder_name, filesep,'accel.txt']);
% extract gyro data
gyro = extractUpRiteData([folder_name, filesep,'gyro.txt']);
% extract mag data
mag = extractUpRiteData([folder_name, filesep,'mag.txt']);
% extract altitude data
baro = extractUpRiteData([folder_name, filesep,'baro.txt']);
disp('extraction complete')

%% low pass filter 2.5 Hz

accel.filterData.lpf_2_5Hz = accel.data;
gyro.filterData.lpf_2_5Hz = gyro.data;

fcuts = [2.5 3.0];

accel.filterData.lpf_2_5Hz.x = lowPassfilter(accel.data.x, fcuts, accel.sampRate);
accel.filterData.lpf_2_5Hz.y = lowPassfilter(accel.data.y, fcuts, accel.sampRate);
accel.filterData.lpf_2_5Hz.z = lowPassfilter(accel.data.z, fcuts, accel.sampRate);

gyro.filterData.lpf_2_5Hz.x = lowPassfilter(gyro.data.x, fcuts, gyro.sampRate);
gyro.filterData.lpf_2_5Hz.y = lowPassfilter(gyro.data.y, fcuts, gyro.sampRate);
gyro.filterData.lpf_2_5Hz.z = lowPassfilter(gyro.data.z, fcuts, gyro.sampRate);


%% low pass filter 5 Hz
accel.filterData.lpf_5Hz = accel.data;
gyro.filterData.lpf_5Hz = gyro.data;

fcuts = [5 6];

accel.filterData.lpf_5Hz.x = lowPassfilter(accel.data.x, fcuts, accel.sampRate);
accel.filterData.lpf_5Hz.y = lowPassfilter(accel.data.y, fcuts, accel.sampRate);
accel.filterData.lpf_5Hz.z = lowPassfilter(accel.data.z, fcuts, accel.sampRate);

gyro.filterData.lpf_5Hz.x = lowPassfilter(gyro.data.x, fcuts, gyro.sampRate);
gyro.filterData.lpf_5Hz.y = lowPassfilter(gyro.data.y, fcuts, gyro.sampRate);
gyro.filterData.lpf_5Hz.z = lowPassfilter(gyro.data.z, fcuts, gyro.sampRate);


%% low pass filter 10 Hz

accel.filterData.lpf_10Hz = accel.data;
gyro.filterData.lpf_10Hz = gyro.data;

fcuts = [10 11];

accel.filterData.lpf_10Hz.x = lowPassfilter(accel.data.x, fcuts, accel.sampRate);
accel.filterData.lpf_10Hz.y = lowPassfilter(accel.data.y, fcuts, accel.sampRate);
accel.filterData.lpf_10Hz.z = lowPassfilter(accel.data.z, fcuts, accel.sampRate);

gyro.filterData.lpf_10Hz.x = lowPassfilter(gyro.data.x, fcuts, gyro.sampRate);
gyro.filterData.lpf_10Hz.y = lowPassfilter(gyro.data.y, fcuts, gyro.sampRate);
gyro.filterData.lpf_10Hz.z = lowPassfilter(gyro.data.z, fcuts, gyro.sampRate);

%% save data to csv
saveSensorStructToCsv(accel, [folder_name,filesep,'accel.csv']);
saveSensorStructToCsv(gyro, [folder_name,filesep,'gyro.csv']);
saveSensorStructToCsv(mag, [folder_name,filesep,'mag.csv']);
saveSensorStructToCsv(baro, [folder_name,filesep,'baro.csv']);
disp('saved data to CSV')

%% save struct data in .mat file
%save .mat file containing data of this session
save([folder_name ,filesep,'imuData.mat'],'gyro', 'accel', 'baro','mag');

%% plot data
figure;
plot(accel.data.seconds, accel.data.x);
hold on
plot(accel.data.seconds, accel.data.y);
plot(accel.data.seconds, accel.data.z);
legend('x', 'y','z');
xlabel('seconds');
ylabel('g')
title('accelerometer')

figure;
plot(gyro.data.seconds, gyro.data.x);
hold on
plot(gyro.data.seconds, gyro.data.y);
plot(gyro.data.seconds, gyro.data.z);
legend('x', 'y','z');
xlabel('seconds');
ylabel('dps')
title('gyroscope');

figure;
plot(mag.data.seconds, mag.data.x);
hold on
plot(mag.data.seconds, mag.data.y);
plot(mag.data.seconds, mag.data.z);
legend('x', 'y','z');
xlabel('seconds');
ylabel('uT')
title('magnetometer');

figure;
plot(baro.data.seconds, baro.data.values);
legend('altitude');
xlabel('seconds');
ylabel('meters')
title('barometer');

figure;
subplot(4,1,1);
plot(accel.data.seconds, accel.data.x);
hold on
plot(accel.data.seconds, accel.data.y);
plot(accel.data.seconds, accel.data.z);
legend('x', 'y','z');
xlabel('seconds');
ylabel('g')
title('accelerometer');

subplot(4,1,2)
plot(gyro.data.seconds, gyro.data.x);
hold on
plot(gyro.data.seconds, gyro.data.y);
plot(gyro.data.seconds, gyro.data.z);
legend('x', 'y','z');
xlabel('seconds');
ylabel('dps')
title('gyroscope');

subplot(4,1,3);
plot(mag.data.seconds, mag.data.x);
hold on
plot(mag.data.seconds, mag.data.y);
plot(mag.data.seconds, mag.data.z);
legend('x', 'y','z');
xlabel('seconds');
ylabel('uT')
title('magnetometer')

subplot(4,1,4)
plot(baro.data.seconds, baro.data.values);
legend('altitude');
xlabel('seconds');
ylabel('meters')
title('altitude');
