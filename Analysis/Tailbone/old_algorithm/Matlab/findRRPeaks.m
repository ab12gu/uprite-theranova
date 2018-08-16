function [ peaksFound, heartRate] = findRRPeaks(signal, fs)
%findRRPeaks Locates the R peaks of an ecg signal
%   ecg is the ecg signal
%   fs is the rate of sampling
import signalExtraction.*
import signalProcessing.*

%signal = filterEcg(signal,fs);

[forwardPeaks forwardHR] = findRRPeaksForward(signal, fs)

backwardEcg = fliplr(signal);

[backwardPeaks backwardHR] = findRRPeaksForward(backwardEcg, fs)

backwardPeaks = fliplr((length(signal)+1) - backwardPeaks);

heartRate = mean([forwardHR, backwardHR]);
if ~isempty(forwardPeaks)
    peaksFound = [backwardPeaks(backwardPeaks < forwardPeaks(1)) , forwardPeaks ];
else
    peaksFound = backwardPeaks;
end
end

