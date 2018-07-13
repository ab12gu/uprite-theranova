right_HS = [4.93, 6.17, 7.27, 8.35, 9.41, 10.48, 11.6, 12.78];
right_TO = [5.69, 6.83, 7.92, 8.98, 10.05, 11.16, 12.3];
left_HS = [5.55, 6.7, 7.79, 8.85, 9.92, 11.02, 12.17];
left_TO = [5.14, 6.31, 7.41, 8.48, 9.56, 10.63, 11.75, 12.88];


figure;
ha(1) = subplot(2,1,1);
plot(accel.data.seconds, -accel.filterData.lpf_10Hz.x);
hold on;
plot(accel.data.seconds, -accel.data.x);
plot(accel.data.seconds, accel.data.y);
plot(accel.data.seconds, accel.data.z);
plot(right_HS, zeros(1,length(right_HS)),'c*');
plot(right_TO, zeros(1,length(right_TO)),'go');
plot(left_HS, zeros(1,length(left_HS)),'bo');
plot(left_TO, zeros(1,length(left_TO)),'ro');
legend('lpf x','x','y','z','right HS','right TO','left HS','left TO')

ha(2) = subplot(2,1,2);
plot(gyro.data.seconds, gyro.data.x);
hold on;
plot(gyro.data.seconds, gyro.data.y);
plot(gyro.data.seconds, gyro.data.z);
legend('x','y','z')
linkaxes(ha,'x');




