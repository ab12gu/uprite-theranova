function [ peaksFound, lowToHighLocs, highToLowLocs, heartRate] = findPeaksForward(signal, searchSize, minDistance, maxDistance, fs)
%findRRPeaks Locates the R peaks of an ecg signal
%   ecg is the ecg signal
%   fs is the rate of sampling

%get the filtered ECG value
%update 9/29/2016. ecg is not filtered. For full algorithm, which does a
%bakcwards and forward analysis, use findRRPeaks(ecg,fs)
%signal %= signal; % = filterEcg(ecg, fs);

%get the first difference, followed by the absolute value
%signal(signal < 0 ) = 0;
firstDiff = getFirstDifference(signal,1);

%figure;
%plot(ecgFirstDiff);

absFirstDiff =firstDiff; % abs(firstDiff);
%hold on;
%plot(ecgAbsFirstDiff,'r');

%start checking for peaks - after a time when the filter has settled
%define a window to check for the max and min - the window should be able
%to pick up 1 step

SLOW_STEP = maxDistance;% round(1/0.3*fs);
FAST_STEP = minDistance;% 1/3*fs;
time_window =  maxDistance;%round(1/0.3*fs); % (sec/min) / (beats/min) * samples/sec
windowCounter = 0;

oldMaxValue = 2^32;
oldMinValue = -2^32;

HIGH_THRESHOLD_SCALE_FACTOR = 5/8;
LOW_THRESHOLD_SCALE_FACTOR = 1/4;

highThreshold = oldMaxValue*HIGH_THRESHOLD_SCALE_FACTOR;
lowThreshold = oldMinValue*LOW_THRESHOLD_SCALE_FACTOR;

highToLow = 0;
lowToHigh = 0;
highThresholdMet = 0;
lowThresholdMet = 0;

maxValue = -2^32;
minValue = 2^32;

lastPeakLoc = 0;

avgValueBuffer = zeros(1,time_window);
peaksFound = [];
oldMaxValues = [];
oldMinValues = [];
highThresholds = [];
lowThresholds = [];
avgValues = [];
windowIntervals =[];
lowToHighLocs = [];
highToLowLocs = [];

oldMaxValue = max(absFirstDiff(1:time_window));
oldMinValue = min(absFirstDiff(1:time_window));
highThreshold = oldMaxValue*HIGH_THRESHOLD_SCALE_FACTOR;
avgValue = mean(absFirstDiff(1:time_window));
lowThreshold = avgValue;
        
maxValue = -2^32;
minValue = 2^32;
        
%used for post analysis and plotting
oldMaxValues = [oldMaxValues oldMaxValue];
oldMinValues = [oldMinValues oldMinValue];
highThresholds = [highThresholds highThreshold];
lowThresholds = [lowThresholds lowThreshold];
windowIntervals = [windowIntervals 1];
avgValues = [avgValues avgValue];
%reset window counter
windowCounter = 0;


for i = 1:length(absFirstDiff)

    if windowCounter <= time_window
        %locate the max and min value in this window
        maxValue = max(absFirstDiff(i), maxValue);
        minValue = min(absFirstDiff(i), minValue);
        avgValueBuffer(i) = absFirstDiff(i);
        
        if absFirstDiff(i) > highThreshold
            if ~highThresholdMet
                highThresholdMet = 1;
                if lowThresholdMet
                    lowToHighLocs = [lowToHighLocs i];
                    lowToHigh = 1;
                    lowThresholdMet = 0; %reset the low threshold met flag.
                end
            end
        elseif absFirstDiff(i) < lowThreshold
            if ~lowThresholdMet
                lowThresholdMet = 1;
                if highThresholdMet
                    highToLowLocs = [highToLowLocs i];
                    highTolow = 1;
                    highThresholdMet = 0; %reset the high threshold met flag.
                    
                    %peak has been found; record it
                    if lowToHigh == 1 && highTolow == 1
                        %locate the local maximum in this area of the
                        %signal
                        lastLowToHigh = lowToHighLocs(end) - searchSize;
                        if lastLowToHigh < 1
                            lastLowToHigh = 1;
                        end
                        
                        lastHighToLow = highToLowLocs(end) + searchSize;
                        if lastHighToLow > length(signal)
                            lastHighToLow = length(signal);
                        end
                        localPeakLoc = find(signal(lastLowToHigh:lastHighToLow) ==...
                            max(signal(lastLowToHigh:lastHighToLow)));
                       
                        peakLoc = localPeakLoc + lastLowToHigh-1;
                        
                        %check if is within usual human step range
                        if (peakLoc - lastPeakLoc) >= FAST_STEP && (peakLoc - lastPeakLoc) <= SLOW_STEP
                            peaksFound = [peaksFound peakLoc];
                        end
                        %reset the last stored peak location.
                        lastPeakLoc = peakLoc;
                        
                        lowToHigh = 0;
                        highToLow = 0;
                    else
                        lowToHigh = 0;
                        highToLow = 0;
                    end
                end
            end
        end
        windowCounter = windowCounter + 1;
    end
    
    if windowCounter >= time_window
        oldMaxValue = maxValue;
        oldMinValue = minValue;
        highThreshold = oldMaxValue*HIGH_THRESHOLD_SCALE_FACTOR;
        %lowThreshold = oldEcgMinValue*LOW_THRESHOLD_SCALE_FACTOR;
        avgValue = mean(avgValueBuffer);
        lowThreshold = avgValue;
        
        maxValue = -2^32;
        minValue = 2^32;
        
        %used for post analysis and plotting
        oldMaxValues = [oldMaxValues oldMaxValue];
        oldMinValues = [oldMinValues oldMinValue];
        highThresholds = [highThresholds highThreshold];
        lowThresholds = [lowThresholds lowThreshold];
        windowIntervals = [windowIntervals i];
        avgValues = [avgValues avgValue];
        %reset window counter
        windowCounter = 0;
    end
     
end
%{
figure;
plot(absFirstDiff,'b');
hold on;
for i = 1:length(windowIntervals)
    line([windowIntervals(i) (windowIntervals(i)+time_window)],...
        [oldMaxValues(i), oldMaxValues(i)], 'Color','r');
    line([windowIntervals(i) (windowIntervals(i)+time_window)],...
        [oldMinValues(i), oldMinValues(i)], 'Color','y');
    line([windowIntervals(i) (windowIntervals(i)+time_window)],...
        [highThresholds(i), highThresholds(i)], 'Color','m');
    line([windowIntervals(i) (windowIntervals(i)+time_window)],...
        [lowThresholds(i), lowThresholds(i)], 'Color','g');
end

plot(lowToHighLocs, absFirstDiff(lowToHighLocs), 'ks')
plot(highToLowLocs, absFirstDiff(highToLowLocs), 'c*')
plot(peaksFound, absFirstDiff(peaksFound), 'go')
figure;
plot(signal);
hold on;
plot(lowToHighLocs, signal(lowToHighLocs), 'ks')
plot(highToLowLocs, signal(highToLowLocs), 'c*')
plot(peaksFound, signal(peaksFound), 'go')
%}

heartRate = fs/mean(diff(peaksFound))*60;

end

