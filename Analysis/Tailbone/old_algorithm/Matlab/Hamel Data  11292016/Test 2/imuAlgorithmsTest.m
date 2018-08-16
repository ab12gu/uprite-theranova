load test2.mat

lpf_10HzData = lFoot.accel.filterData.lpf_10Hz;

%show them to me!
figure; plot(lpf_10HzData.x); hold on;
 plot(lpf_10HzData.y);
 plot(lpf_10HzData.z);
 
%get the gravity vector
notmovingTimePoint =250;

xNotMoving = lpf_10HzData.x(250);
yNotMoving = lpf_10HzData.y(250);
zNotMoving = lpf_10HzData.z(250);

gravityVector =nthroot( (xNotMoving.^2 + yNotMoving.^2 + zNotMoving.^2), 3)
% http://cache.freescale.com/files/sensors/doc/app_note/AN3461.pdf
roll = 0;
pitch = 0;
yaw = 0;

roll = atan(yNotMoving/zNotMoving)
pitch = atan(-xNotMoving/sqrt(yNotMoving.^2 + zNotMoving.^2))


