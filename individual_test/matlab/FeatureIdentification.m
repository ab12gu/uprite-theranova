TailboneAnalysis;
close all;

gyroZHpf_2 = highPassFilter(gyroZ,100, 0.5);
angularPosZ_2 = integrateIMU(gyroSec, gyroZHpf_2).*pi/180;% + yaw;

angularPosZ_3 = lowPassfilter(angularPosZ_2,[5,6]/50,100);
posAngPosZ = angularPosZ_3;
posAngPosZ(posAngPosZ < 0) = 0;

negAngPosZ = angularPosZ_3;
negAngPosZ(negAngPosZ >= 0) = 0;
negAngPosZ = abs(negAngPosZ);

%[peaks] = findPeaksForward(posAngPosZ, 40, round(1/3*100), round(1/0.3*100), 100);


[peaks] = findPeaksForward(posAngPosZ, 40, round(1/3*100), round(1/0.5*100), 100);
[backwardPeaks] = findPeaksForward(fliplr(posAngPosZ), 40, round(1/3*100), round(1/0.5*100), 100);
backwardPeaks = fliplr((length(posAngPosZ)+1) - backwardPeaks );

allPeaks = sort([peaks, backwardPeaks(~ismember(backwardPeaks, peaks))]);

[troughs] = findPeaksForward(negAngPosZ, 40, round(1/3*100), round(1/0.5*100), 100);
[backwardTroughs] = findPeaksForward(fliplr(negAngPosZ), 40, round(1/3*100), round(1/0.5*100), 100);
backwardTroughs = fliplr((length(posAngPosZ)+1) - backwardTroughs);

allTroughs = sort([troughs, backwardTroughs(~ismember(backwardTroughs, troughs))]);

[accelPeaks] = findPeaksForward(earthXFilt, 5,  round(1/4*100), round(1/0.4*100), 100);
backwardAccelPeaks = findPeaksForward(fliplr(earthXFilt), 5,  round(1/4*100), round(1/0.4*100), 100);
backwardAccelPeaks = fliplr((length(earthXFilt)+1) - backwardAccelPeaks);
allAccelPeaks = sort([accelPeaks, backwardAccelPeaks(~ismember(backwardAccelPeaks, accelPeaks))]);

allTroughPeaks = sort([allPeaks, allTroughs]);

allAccelPeaks = [];
for i = 1:length(allTroughPeaks)-1
    startIndex = allTroughPeaks(i);
    endIndex = allTroughPeaks(i+1);

    accelPeak = findPeaksForward(earthXFilt(startIndex:endIndex), 5,  round(1/4*100), length(earthXFilt(startIndex:endIndex)), 100);
    accelPeak = accelPeak + startIndex - 1;

    allAccelPeaks = [allAccelPeaks accelPeak];
end


accelFirstDiff  = getFirstDifference(earthXFilt,1);
to_locations = [];
for i= 1:length(allAccelPeaks)
    
    startIndex = allAccelPeaks(i);
    if i == length(allAccelPeaks)
        endIndex = length(earthXFilt)-10;
    else
        endIndex = round(mean([allAccelPeaks(i + 1), allAccelPeaks(i)]));
    end
    
    if endIndex < startIndex
            endIndex = endIndex;
    end
    
    to_location = startIndex-1 + find(accelFirstDiff(startIndex:endIndex) == max(accelFirstDiff(startIndex:endIndex)),1);
    
    searchMin = to_location - 5;
    searchMax = to_location + 5;

    to_location = searchMin-1 + find(earthXFilt(searchMin:searchMax) == max(earthXFilt(searchMin:searchMax)));
    to_locations = [to_locations to_location];
    
end



figure;
ha(1) = subplot(2,1,1);
hold on;
plot(gyroSec,angularPosZ_3);
plot(gyroSec(allPeaks), angularPosZ_3(allPeaks),'gx');
plot(gyroSec(allTroughs), angularPosZ_3(allTroughs),'c^');

ha(2) = subplot(2,1,2);
plot(accelSec, earthXFilt); hold on;
%plot(accelSec(accelPeaks),earthXFilt(accelPeaks),'gx');
plot(accelSec(allAccelPeaks),earthXFilt(allAccelPeaks),'gx');
plot(accelSec(to_locations), earthXFilt(to_locations),'k^');
plot(accelSec, accelFirstDiff);

for i=1:length(allPeaks)
    line([gyroSec(allPeaks(i)) gyroSec(allPeaks(i))],[min(earthXFilt), max(earthXFilt)], 'Color','g', 'LineStyle','--');
end

for i=1:length(allTroughs)
    line([gyroSec(allTroughs(i)) gyroSec(allTroughs(i))],[min(earthXFilt), max(earthXFilt)], 'Color','c', 'LineStyle','--');
end

plot(right_HS, zeros(1,length(right_HS)),'c*');
plot(right_TO, zeros(1,length(right_TO)),'m*');
plot(left_HS, zeros(1,length(left_HS)),'bo');
plot(left_TO, zeros(1,length(left_TO)),'ro');
legend('xaccel','accelPeaks','to location','x diff','right HS','right TO','left HS','left TO')

linkaxes(ha,'x')

%% featureExtract
rightHS = [];
rightTO = [];
leftHS = [];
leftTO = [];

for i = 1:length(allTroughs)
    if i ~=length(allTroughs)
        firstTrough =  allTroughs(i);
        secondTrough = allTroughs(i+1);
        peak = allPeaks(allPeaks > firstTrough & allPeaks < secondTrough);
        if isempty(peak)
            continue;
        elseif length(peak) > 1
            peak = peak(1);
            %right leg movement
            accelPeak = allAccelPeaks(allAccelPeaks > firstTrough & allAccelPeaks < peak);
        
            if ~isempty(accelPeak) && length(accelPeak) == 1
                rightHS = [rightHS accelPeak];
                to_location = to_locations(to_locations > firstTrough & to_locations < peak);
                leftTO = [leftTO to_location];
            end
        end
        
        %right leg movement
        accelPeak = allAccelPeaks(allAccelPeaks > firstTrough & allAccelPeaks < peak);
        
        if ~isempty(accelPeak) && length(accelPeak) == 1
            rightHS = [rightHS accelPeak];
            to_location = to_locations(to_locations > firstTrough & to_locations < peak);
            leftTO = [leftTO to_location];
        end
        
        %left leg movement
        accelPeak = allAccelPeaks(allAccelPeaks > peak & allAccelPeaks < secondTrough);
        
         if ~isempty(accelPeak) && length(accelPeak) == 1
            leftHS = [leftHS accelPeak];
            to_location = to_locations(to_locations > peak & to_locations < secondTrough);
            rightTO = [rightTO to_location];
        end
    else
        firstTrough = allTroughs(i);
        peak = allPeaks(allPeaks > firstTrough);
        if ~isempty(peak)
            peak = peak(1);
        else
            continue;
        end
        
        %right leg movement
        accelPeak = allAccelPeaks(allAccelPeaks > firstTrough & allAccelPeaks < peak);
        
        if ~isempty(accelPeak) && length(accelPeak) == 1
            rightHS = [rightHS accelPeak];
            to_location = to_locations(to_locations > firstTrough & to_locations < peak);
            leftTO = [leftTO to_location];
        end
        
    end
    
    
end

figure;
ha(1) = subplot(2,1,1);
hold on;
plot(gyroSec,angularPosZ_3);
plot(gyroSec(allPeaks), angularPosZ_3(allPeaks),'gx');
plot(gyroSec(allTroughs), angularPosZ_3(allTroughs),'c^');
legend('z angular position','peak','trough')

ha(2) = subplot(2,1,2);
plot(accelSec, earthXFilt); hold on;
%plot(accelSec(accelPeaks),earthXFilt(accelPeaks),'gx');
%plot(accelSec(allAccelPeaks),earthXFilt(allAccelPeaks),'gx');
%plot(accelSec(to_locations), earthXFilt(to_locations),'k^');
plot(accelSec, accelFirstDiff);
plot(accelSec(rightHS), earthXFilt(rightHS),'c*');
plot(accelSec(rightTO), earthXFilt(rightTO),'m*');
plot(accelSec(leftHS), earthXFilt(leftHS),'bo');
plot(accelSec(leftTO), earthXFilt(leftTO),'ro');
legend('xaccel','x diff','right HS','right TO','left HS','left TO')

linkaxes(ha,'x')

close all

plot(accelSec, -1*earthXFilt); hold on;
%plot(accelSec(accelPeaks),earthXFilt(accelPeaks),'gx');
%plot(accelSec(allAccelPeaks),earthXFilt(allAccelPeaks),'gx');
%plot(accelSec(to_locations), earthXFilt(to_locations),'k^');
plot(accelSec(rightHS), -1*earthXFilt(rightHS),'c*');
plot(accelSec(rightTO), -1*earthXFilt(rightTO),'m*');
plot(accelSec(leftHS), -1*earthXFilt(leftHS),'bo');
plot(accelSec(leftTO), -1*earthXFilt(leftTO),'ro');

legend('Uprite Accel X Filtered','Zeno HS right','Zeno TO right','Zeno HS left','Zeno HS left');


linkaxes(ha,'x')


%plot(peaks, angularPosZ_2(peaks), 'c*');
%plot(troughs, angularPosZ_2(troughs), 'mo');
%plot(backwardPeaks, angularPosZ_2(backwardPeaks), 'bd');
%plot(backwardTroughs, angularPosZ_2(backwardTroughs), 'rs');

%% save data to CSV
dataFile = '../docs/matlab_data.csv';
fid = fopen(dataFile, 'w');
fprintf(fid,'%s, ', 'accelSec');
fprintf(fid,'%d, ', accelSec);
fprintf(fid,'\n');
fprintf(fid,'%s, ', 'accelX');
fprintf(fid,'%d, ', accelX);
fprintf(fid,'\n');
fprintf(fid,'%s, ', 'accelY');
fprintf(fid,'%d, ', accelY);
fprintf(fid,'\n');
fprintf(fid,'%s, ', 'accelZ');
fprintf(fid,'%d, ', accelZ);
fprintf(fid,'\n');
fprintf(fid,'%s, ', 'earthXFilt');
fprintf(fid,'%d, ', earthXFilt);
fprintf(fid,'\n');

fprintf(fid,'%s, ', 'accelFirstDiff');
fprintf(fid,'%d, ', accelFirstDiff);
fprintf(fid,'\n');

fprintf(fid,'%s, ', 'accelPeaks');
fprintf(fid,'%d, ', accelSec(allAccelPeaks));
fprintf(fid,'\n');

fprintf(fid,'%s, ', 'to_locations');
fprintf(fid,'%d, ', accelSec(to_locations));
fprintf(fid,'\n');

fprintf(fid,'%s, ', 'rightHS');
fprintf(fid,'%d, ', accelSec(rightHS));
fprintf(fid,'\n');

fprintf(fid,'%s, ', 'rightTO');
fprintf(fid,'%d, ', accelSec(rightTO));
fprintf(fid,'\n');

fprintf(fid,'%s, ', 'leftHS');
fprintf(fid,'%d, ', accelSec(leftHS));
fprintf(fid,'\n');

fprintf(fid,'%s, ', 'leftTO');
fprintf(fid,'%d, ', accelSec(leftTO));
fprintf(fid,'\n');

fprintf(fid,'%s, ', 'gyroSec');
fprintf(fid,'%d, ', gyroSec);
fprintf(fid,'\n');

fprintf(fid,'%s, ', 'gyroZHpf_2');
fprintf(fid,'%d, ', gyroZHpf_2);
fprintf(fid,'\n');

fprintf(fid,'%s, ', 'angularPosZ_2');
fprintf(fid,'%d, ', angularPosZ_2);
fprintf(fid,'\n');

fprintf(fid,'%s, ', 'angularPosPeaks');
fprintf(fid,'%d, ', gyroSec(allPeaks));
fprintf(fid,'\n');

fprintf(fid,'%s, ', 'angularPosTroughs');
fprintf(fid,'%d, ', gyroSec(allTroughs));
fprintf(fid,'\n');

fclose(fid);