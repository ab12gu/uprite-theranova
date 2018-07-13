%% load the data


%load imuData.mat
close all
usedAccelData = accel.data; %accel.filterData.lpf_10Hz;
accelSampRate = accel.sampRate;
%usedAccelData.x = usedAccelData.x(5:end);
%usedAccelData.y = usedAccelData.y(5:end);
%usedAccelData.z = usedAccelData.z(5:end);
usedGyroData = gyro.data; %gyro.filterData.lpf_10Hz;
gyroSampRate = gyro.sampRate;
%usedGyroData.x = usedGyroData.x(5:end);
%usedGyroData.y= usedGyroData.y(5:end);
%usedGyroData.z = usedGyroData.z(5:end);

%% specify a region of data to analyze
startIndex = 400;
endIndex = min(length(usedAccelData.seconds), length(usedGyroData.seconds))-5;

%% identify a region of data to calculate an initial gravity vector
gravityCalculationStart = 100;
gravityCalculationEnd = 450;
meanAccelx = mean(usedAccelData.x(gravityCalculationStart:gravityCalculationEnd));
meanAccely = mean(usedAccelData.y(gravityCalculationStart:gravityCalculationEnd));
meanAccelz = mean(usedAccelData.z(gravityCalculationStart:gravityCalculationEnd));

upDatedravityStrength = sqrt( meanAccelx.^2 + meanAccely.^2 + meanAccelz.^2);

normalizedMeanAccelX = meanAccelx/upDatedravityStrength;
normalizedMeanAccelY = meanAccely/upDatedravityStrength;
normalizedMeanAccelZ = meanAccelz/upDatedravityStrength;

normalizedGravityVector = [normalizedMeanAccelX; normalizedMeanAccelY; normalizedMeanAccelZ];

%% identify the initial roll pitch and yaw of the sensor relative to gravity.
% Key assumption here is that the gravity vector is [-1; 0; 0], so the x
% axis is upwards and downwards
%R_yzx
roll = 0; %atan(meanAccely/meanAccelz);
pitch = atan(normalizedMeanAccelZ/normalizedMeanAccelX);  %atan(-meanAccelx/sqrt(meanAccely.^2 + meanAccelz.^2));
yaw = atan(normalizedMeanAccelY/sqrt(normalizedMeanAccelX.^2 + normalizedMeanAccelZ.^2));

%roll = asin(-(normalizedMeanAccelY + normalizedMeanAccelZ)/(cos(yaw).^2.*sin(pitch).^2 + sin(yaw).^2));

%% get the section of data to analyze
accelSec = usedAccelData.seconds(startIndex:endIndex);
accelX = usedAccelData.x(startIndex:endIndex);
accelY = usedAccelData.y(startIndex:endIndex);
accelZ = usedAccelData.z(startIndex:endIndex);

%if the data is prety steady, the gravity vector can be calculated as a DC
%value of the data.
gravityAccelX = lowPassfilter(usedAccelData.x, [0.1 0.7], accelSampRate);
gravityAccelY = lowPassfilter(usedAccelData.y, [0.1 0.7], accelSampRate);
gravityAccelZ = lowPassfilter(usedAccelData.z, [0.1 0.7], accelSampRate);

gravityAccelX = gravityAccelX(startIndex:endIndex); %ones(1,endIndex-startIndex+1)*meanAccelx; %
gravityAccelY =gravityAccelY(startIndex:endIndex); % ones(1,endIndex-startIndex+1)*meanAccely; % 
gravityAccelZ = gravityAccelZ(startIndex:endIndex); %  ones(1,endIndex-startIndex+1)*meanAccelz; %


meanGyroX = [];
meanGyroY = [];
meanGyroZ = [];

gyroSec = usedGyroData.seconds(startIndex:endIndex);
gyroX = usedGyroData.x(startIndex:endIndex);
gyroY = usedGyroData.y(startIndex:endIndex);
gyroZ = usedGyroData.z(startIndex:endIndex);

earthGyroVectorHolder = zeros(3,length(gyroSec));

gyroXHpf = gyroX; %highPassFilter(gyroX,100, 0.01);
gyroYHpf = gyroY;%highPassFilter(gyroY,100, 0.01);
gyroZHpf = gyroZ; %highPassFilter(gyroZ,100, 0.01);

angularPosX = integrateIMU(gyroSec, gyroXHpf).*pi/180;% + roll;
angularPosY = integrateIMU(gyroSec, gyroYHpf).*pi/180;% + pitch;
angularPosZ = integrateIMU(gyroSec, gyroZHpf).*pi/180;% + yaw;

gravityVector = [meanAccelx; meanAccely; meanAccelz]; 
gravityVectorHolder= zeros(3,length(accelSec));

%% initialize variables to store values
accelDeltaX = zeros(1,length(accelSec));
accelDeltaY = zeros(1,length(accelSec));
accelDeltaZ = zeros(1,length(accelSec));
accelDeltaVectorHolder= zeros(3,length(accelSec));

accel2DeltaX = zeros(1,length(accelSec));
accel2DeltaY = zeros(1,length(accelSec));
accel2DeltaZ = zeros(1,length(accelSec));
accel2DeltaVectorHolder= zeros(3,length(accelSec));
earth2AccelDeltaVectorHolder = zeros(3,length(accelSec));

earthAccelDeltaVectorHolder = zeros(3,length(accelSec));
forwardEarthAccelDeltaVectorHolder = zeros(3,length(accelSec));
forwardPositionDeltaVectorHolder = zeros(3,length(accelSec));

%% start calculations
for i = 1:length(accelSec)
    % readjust the gravity vector based on the angular position change.
    rotationX = [1,0,0; 0,cos(angularPosX(i)),sin(angularPosX(i)) ; 0,-sin(angularPosX(i)),cos(angularPosX(i))];
    rotationY = [cos(angularPosY(i)),0,-sin(angularPosY(i)); 0,1,0; sin(angularPosY(i)),0,cos(angularPosY(i))];
    rotationZ = [cos(angularPosZ(i)),sin(angularPosZ(i)),0; -sin(angularPosZ(i)), cos(angularPosZ(i)), 0; 0 0 1];
    gravityVectorHolder(:,i) = rotationY*rotationZ*rotationX*gravityVector;
    
    %remove the adjusted gravity vector data from the acceleration data.
    accel2DeltaX(i) = accelX(i) - gravityVectorHolder(1,i);
    accel2DeltaY(i) = accelY(i) - gravityVectorHolder(2,i);
    accel2DeltaZ(i) = accelZ(i) - gravityVectorHolder(3,i);
    accel2DeltaVectorHolder(:,i) = [accel2DeltaX(i); accel2DeltaY(i); accel2DeltaZ(i)]; 
    
    % based on the angular position change, readjust the accelerometer data
    % to compensate for rotation
    updatedRotationY = [cos(angularPosY(i)+pitch),0,-sin(angularPosY(i)+pitch); 0,1,0; sin(angularPosY(i)+pitch),0,cos(angularPosY(i)+pitch)];
    updatedRotationZ = [cos(angularPosZ(i)+yaw),sin(angularPosZ(i)+yaw),0; -sin(angularPosZ(i)+yaw), cos(angularPosZ(i)+yaw), 0; 0 0 1];
    updatedRotationX = [1,0,0; 0,cos(angularPosX(i)),sin(angularPosX(i)) ; 0,-sin(angularPosX(i)),cos(angularPosX(i))]; %eye(3); %-rotationX;
    
    a = inv(updatedRotationY*updatedRotationZ*updatedRotationX);
    earth2AccelDeltaVectorHolder(:,i) = a*accel2DeltaVectorHolder(:,i);
    
        %--->>>second alternative - just remove the DC value from the accelerometer
        %(presumed to be gravity vector)
        accelDeltaX(i) = accelX(i) - gravityAccelX(i); %gravityVector(1); %gravityVectorHolder(1,i);
        accelDeltaY(i) = accelY(i) - gravityAccelY(i); %gravityVector(2); %gravityVectorHolder(2,i);
        accelDeltaZ(i) = accelZ(i) - gravityAccelZ(i); %gravityVector(3); %gravityVectorHolder(3,i);
        accelDeltaVectorHolder(:,i) = [accelDeltaX(i); accelDeltaY(i); accelDeltaZ(i)];
    
        updatedGravityStrength = sqrt( gravityAccelX(i).^2 + gravityAccelY(i).^2 + gravityAccelZ(i).^2);
    
        updatedNormalizedMeanAccelX = gravityAccelX(i)/updatedGravityStrength;
        updatedNormalizedMeanAccelY = gravityAccelY(i)/updatedGravityStrength;
        updatedNormalizedMeanAccelZ = gravityAccelZ(i)/updatedGravityStrength;
    
        newAngY = atan(updatedNormalizedMeanAccelZ/updatedNormalizedMeanAccelX); %pitch; % angularPosY(i) +
        newAngZ = atan(updatedNormalizedMeanAccelY/sqrt(updatedNormalizedMeanAccelX.^2 + updatedNormalizedMeanAccelZ.^2));% yaw; % angularPosZ(i) +
    
        %rotate so that X axis points towards earth
        updatedRotationY = [cos(newAngY),0,-sin(newAngY); 0,1,0; sin(newAngY),0,cos(newAngY)];
        updatedRotationZ = [cos(newAngZ),sin(newAngZ),0; -sin(newAngZ), cos(newAngZ), 0; 0 0 1];
        updatedRotationX = eye(3); %-rotationX;
        a = inv(updatedRotationY*updatedRotationZ*updatedRotationX);
        earthAccelDeltaVectorHolder(:,i) = a*accelDeltaVectorHolder(:,i);
    %--------->>> END second alternative <<< --------------

    %rotate so that Z axis is direction of travel
    if i > 2
        xEarthPositionTemp = integrateIMU(accelSec(1:i), integrateIMU(accelSec(1:i), earthAccelDeltaVectorHolder(1,1:i)));
        yEarthPositionTemp = integrateIMU(accelSec(1:i), integrateIMU(accelSec(1:i), earthAccelDeltaVectorHolder(2,1:i)));
        zEarthPositionTemp = integrateIMU(accelSec(1:i), integrateIMU(accelSec(1:i), earthAccelDeltaVectorHolder(3,1:i)));
    
        positionStrength =sqrt( xEarthPositionTemp(end).^2 + yEarthPositionTemp(end).^2 + zEarthPositionTemp(end).^2); %sqrt(yEarthPositionTemp(end).^2 + zEarthPositionTemp(end).^2); %

        normalizedMeanPositionX = xEarthPositionTemp(end)/positionStrength;
        normalizedMeanPositionY = yEarthPositionTemp(end)/positionStrength;
        normalizedMeanPositionZ = zEarthPositionTemp(end)/positionStrength;
    
        roll = atan(normalizedMeanPositionY/normalizedMeanPositionZ);
        pitch = atan(-normalizedMeanPositionX/sqrt(normalizedMeanPositionY.^2 + normalizedMeanPositionZ.^2));

        updatedRotationX = [1,0,0; 0,cos(roll),sin(roll) ; 0,-sin(roll),cos(roll)]; %[cos(roll),sin(roll) ; -sin(roll),cos(roll)]; %
        updatedRotationY = [cos(pitch),0,-sin(pitch); 0,1,0; sin(pitch),0,cos(pitch)];
        updatedRotationZ = eye(3);
        %i
        %a = inv(updatedRotationX);
        a = inv(updatedRotationX*updatedRotationY*updatedRotationZ);
        forwardEarthAccelDeltaVectorHolder(:,i) = a*earthAccelDeltaVectorHolder(:,i);%[earthAccelDeltaVectorHolder(1,i); a*earthAccelDeltaVectorHolder(2:3,i)];
        forwardPositionDeltaVectorHolder(:,i) = a*[xEarthPositionTemp(end); yEarthPositionTemp(end); zEarthPositionTemp(end)]; 
    end
    
end

%accelPureDeltaHpfX = accelX; %highPassFilter(accelDeltaX, 100, 0.01);
%accelDeltaHpfY = accelDeltaY; %highPassFilter(accelDeltaY, 100, 0.01);
accelPureDeltaHpfZ = accelZ - 0.18; %highPassFilter(accelDeltaZ, 100, 0.01);

%xVelocity = integrateIMU(accelSec, accelDeltaHpfX);
%yVelocity = integrateIMU(accelSec, accelDeltaHpfY);
zPureVelocity = integrateIMU(accelSec, accelPureDeltaHpfZ);

%xPosition = integrateIMU(accelSec, xVelocity);
%yPosition = integrateIMU(accelSec, yVelocity);
zPurePosition = integrateIMU(accelSec, zPureVelocity);

xPureDeltaVelocity = integrateIMU(accelSec, accelDeltaX);
yPureDeltaVelocity = integrateIMU(accelSec, accelDeltaY);
zPureDeltaVelocity = integrateIMU(accelSec, accelDeltaZ);

xPureDeltaPosition = integrateIMU(accelSec, xPureDeltaVelocity);
yPureDeltaPosition = integrateIMU(accelSec, yPureDeltaVelocity);
zPureDeltaPosition = integrateIMU(accelSec, zPureDeltaVelocity);



accelDeltaHpfX = accelDeltaX; %highPassFilter(accelDeltaX, 100, 0.01);
accelDeltaHpfY = accelDeltaY; %highPassFilter(accelDeltaY, 100, 0.01);
accelDeltaHpfZ = accelDeltaZ; %highPassFilter(accelDeltaZ, 100, 0.01);

xVelocity = integrateIMU(accelSec, accelDeltaHpfX);
yVelocity = integrateIMU(accelSec, accelDeltaHpfY);
zVelocity = integrateIMU(accelSec, accelDeltaHpfZ);

xPosition = integrateIMU(accelSec, xVelocity);
yPosition = integrateIMU(accelSec, yVelocity);
zPosition = integrateIMU(accelSec, zVelocity);


earthAccelDeltaHpfX = earthAccelDeltaVectorHolder(1,:); %highPassFilter(earthAccelDeltaVectorHolder(1,:), 100, 0.01);
earthAccelDeltaHpfY = earthAccelDeltaVectorHolder(2,:); %highPassFilter(earthAccelDeltaVectorHolder(2,:), 100, 0.01);
earthAccelDeltaHpfZ = earthAccelDeltaVectorHolder(3,:); %earthAccelDeltaVectorHolder(3,:);% highPassFilter(earthAccelDeltaVectorHolder(3,:), 100, 0.05);

xEarthVelocity = integrateIMU(accelSec, earthAccelDeltaHpfX);
yEarthVelocity = integrateIMU(accelSec, earthAccelDeltaHpfY);
zEarthVelocity = 4.*integrateIMU(accelSec, earthAccelDeltaHpfZ);% + 0.12;

xEarthPosition = integrateIMU(accelSec, xEarthVelocity);
yEarthPosition = integrateIMU(accelSec, yEarthVelocity);
zEarthPosition = integrateIMU(accelSec, zEarthVelocity);


forwardEarthAccelDeltaHpfX = forwardEarthAccelDeltaVectorHolder(1,:); %highPassFilter(earthAccelDeltaVectorHolder(1,:), 100, 0.01);
forwardEarthAccelDeltaHpfY = forwardEarthAccelDeltaVectorHolder(2,:); %highPassFilter(earthAccelDeltaVectorHolder(2,:), 100, 0.01);
forwardEarthAccelDeltaHpfZ = forwardEarthAccelDeltaVectorHolder(3,:); %earthAccelDeltaVectorHolder(3,:);% highPassFilter(earthAccelDeltaVectorHolder(3,:), 100, 0.05);

xforwardEarthVelocity = integrateIMU(accelSec, forwardEarthAccelDeltaHpfX);
yforwardEarthVelocity = integrateIMU(accelSec, forwardEarthAccelDeltaHpfY);
zforwardEarthVelocity = integrateIMU(accelSec, forwardEarthAccelDeltaHpfZ);% + 0.12;

xforwardEarthPosition = integrateIMU(accelSec, xforwardEarthVelocity);
yforwardEarthPosition = integrateIMU(accelSec, yforwardEarthVelocity);
zforwardEarthPosition = integrateIMU(accelSec, zforwardEarthVelocity);


accel2DeltaHpfX = accel2DeltaX; %highPassFilter(accelDeltaX, 100, 0.01);
accel2DeltaHpfY = accel2DeltaY; %highPassFilter(accelDeltaY, 100, 0.01);
accel2DeltaHpfZ = accel2DeltaZ; %getFirstIntegration(getFirstIntegration(getFirstDifference(getFirstDifference(accel2DeltaZ,1),1))); % highPassFilter(accel2DeltaZ, 100, 0.01);

x2Velocity = integrateIMU(accelSec, accel2DeltaHpfX);
y2Velocity = integrateIMU(accelSec, accel2DeltaHpfY);
z2Velocity = integrateIMU(accelSec, accel2DeltaHpfZ);

x2Position = integrateIMU(accelSec, x2Velocity);
y2Position = integrateIMU(accelSec, y2Velocity);
z2Position = integrateIMU(accelSec, z2Velocity);

earth2AccelDeltaHpfX = earth2AccelDeltaVectorHolder(1,:); %highPassFilter(earthAccelDeltaVectorHolder(1,:), 100, 0.01);
earth2AccelDeltaHpfY = earth2AccelDeltaVectorHolder(2,:); %highPassFilter(earthAccelDeltaVectorHolder(2,:), 100, 0.01);
earth2AccelDeltaHpfZ = earth2AccelDeltaVectorHolder(3,:);%getFirstIntegration(getFirstIntegration(getFirstDifference(getFirstDifference(earth2AccelDeltaVectorHolder(3,:),1),1))); %earthAccelDeltaVectorHolder(3,:);% highPassFilter(earthAccelDeltaVectorHolder(3,:), 100, 0.05);
%earth2AccelDeltaHpfZ = earth2AccelDeltaHpfZ;% + 0.05;

xEarth2Velocity = integrateIMU(accelSec, earth2AccelDeltaHpfX);
yEarth2Velocity = integrateIMU(accelSec, earth2AccelDeltaHpfY);
zEarth2Velocity = integrateIMU(accelSec, earth2AccelDeltaHpfZ);% + 0.12;

xEarth2Position = integrateIMU(accelSec, xEarth2Velocity);
yEarth2Position = integrateIMU(accelSec, yEarth2Velocity);
zEarth2Position = integrateIMU(accelSec, zEarth2Velocity);

figure; plot(accelSec, xPureDeltaPosition.*9.81); hold on;
    plot(accelSec, yPureDeltaPosition.*9.81); 
    plot(accelSec, zPureDeltaPosition.*9.81);
title('pure delta position');
legend('x','y','z');

figure; plot(accelSec, accel2DeltaZ.*9.81); hold on;
    plot(accelSec, accel2DeltaHpfZ.*9.81);
    plot(accelSec, z2Velocity.*9.81); 
    plot(accelSec, z2Position.*9.81);
title('z 2');
legend('gravity removed','hpf','velocity','position');

figure; plot(accelSec, earthAccelDeltaVectorHolder(1,:).*9.81); hold on;
    plot(accelSec, earthAccelDeltaHpfX.*9.81);
    plot(accelSec, xEarthVelocity.*9.81); 
    plot(accelSec, xEarthPosition.*9.81);
title('x earth, DC removal adjusted');
legend('gravity removed','hpf','velocity','position');

figure; plot(accelSec, earthAccelDeltaVectorHolder(2,:).*9.81); hold on;
    plot(accelSec, earthAccelDeltaHpfY.*9.81);
    plot(accelSec, yEarthVelocity.*9.81); 
    plot(accelSec, yEarthPosition.*9.81);
title('y earth, DC removal adjusted');
legend('gravity removed','hpf','velocity','position');

figure; plot(accelSec, earthAccelDeltaVectorHolder(3,:).*9.81); hold on;
    plot(accelSec, earthAccelDeltaHpfZ.*9.81);
    plot(accelSec, zEarthVelocity.*9.81); 
    plot(accelSec, zEarthPosition.*9.81);
title('z earth, DC removal adjusted');
legend('gravity removed','hpf','velocity','position');


figure; plot(accelSec, forwardEarthAccelDeltaVectorHolder(1,:).*9.81); hold on;
    plot(accelSec, forwardEarthAccelDeltaHpfX.*9.81);
    plot(accelSec, xforwardEarthVelocity.*9.81); 
    plot(accelSec, xforwardEarthPosition.*9.81);
title('x forward earth');
legend('gravity removed','hpf','velocity','position');

figure; plot(accelSec, forwardEarthAccelDeltaVectorHolder(2,:).*9.81); hold on;
    plot(accelSec, forwardEarthAccelDeltaHpfY.*9.81);
    plot(accelSec, yforwardEarthVelocity.*9.81); 
    plot(accelSec, yforwardEarthPosition.*9.81);
title('y forward earth');
legend('gravity removed','hpf','velocity','position');

figure; plot(accelSec, forwardEarthAccelDeltaVectorHolder(3,:).*9.81); hold on;
    plot(accelSec, forwardEarthAccelDeltaHpfZ.*9.81);
    plot(accelSec, zforwardEarthVelocity.*9.81); 
    plot(accelSec, zforwardEarthPosition.*9.81);
title('z forward earth');
legend('gravity removed','hpf','velocity','position');


% figure; plot(accelSec, earth2AccelDeltaVectorHolder(1,:).*9.81); hold on;
%     plot(accelSec, earth2AccelDeltaHpfX.*9.81);
%     plot(accelSec, xEarth2Velocity.*9.81); 
%     plot(accelSec, xEarth2Position.*9.81);
% title('x earth, gyroscope adjusted with gravity removed');
% legend('gravity removed','hpf','velocity','position');
% 
% figure; plot(accelSec, earth2AccelDeltaVectorHolder(2,:).*9.81); hold on;
%     plot(accelSec, earth2AccelDeltaHpfY.*9.81);
%     plot(accelSec, yEarth2Velocity.*9.81); 
%     plot(accelSec, yEarth2Position.*9.81);
% title('y earth, gyroscope adjusted with gravity removed');
% legend('gravity removed','hpf','velocity','position');
% 
% figure; plot(accelSec, earth2AccelDeltaVectorHolder(3,:).*9.81); hold on;
%     plot(accelSec, earth2AccelDeltaHpfZ.*9.81);
%     plot(accelSec, zEarth2Velocity.*9.81); 
%     plot(accelSec, zEarth2Position.*9.81);
% title('z earth, gyroscope adjusted with gravity removed');
% legend('gravity removed','hpf','velocity','position');


