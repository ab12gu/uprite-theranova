function [ cleanedFilteredSignal, adjustedForwardFilterSignal,adjustedReInvertedFilterSignal, coeff] = highPassFilter(signal, fs, cutoff)
%UNTITLED3 Summary of this function goes here
%   Detailed explanation goes here

%create FIR coefficients
freqCutOff = cutoff; %Hz
order = 900;
normFreq = freqCutOff./(fs/2); 
coeff = fir1(order, normFreq,'high');

%freqz(coeff);
%length(coeff)

filterDelay = round(length(coeff)/2);

if filterDelay > length(signal)/2
    filterDelay = round(length(signal)/2);
end


signalOffset = signal;
forwardFilterSignal = filter(coeff,1, signal);

invertedSignal = fliplr(signalOffset);
backwardFilterSignal = filter(coeff,1,invertedSignal);
reInvertedFilterSignal = fliplr(backwardFilterSignal);

adjustedForwardFilterSignal = forwardFilterSignal(filterDelay:end);
adjustedReInvertedFilterSignal = [mean(reInvertedFilterSignal(1:(end-filterDelay)-20))*ones(1,filterDelay-1),...
                                    reInvertedFilterSignal(1:(end-(filterDelay-1)))];
sampleLength = length(adjustedForwardFilterSignal);
cleanedFilteredSignal = [adjustedForwardFilterSignal(1:round(sampleLength/2)),... 
                        adjustedReInvertedFilterSignal(round(sampleLength/2)+1:end)];
                   

end

