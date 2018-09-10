
vect = load("../Theranova070/Data.5.04_04_2018_10.25.17.915.AM/imuData.mat");

display('Sensor Data')
display(vect.sensorData)

display('Left Ankle Data')
display(vect.sensorData.leftAnkle)

display('Accleration Data')
display(vect.sensorData.leftAnkle.accel)

display('Raw Data')
display(vect.sensorData.leftAnkle.accel.rawdata)

display('Scaled Data')
display(vect.sensorData.leftAnkle.accel.data) 

display('Filtered Data')
display(vect.sensorData.leftAnkle.accel.filterData)
