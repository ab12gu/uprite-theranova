function [ cleanedFilteredData, filteredData, reInvertedFilteredData, hh] = lowPassfilter(data, fcuts, fs)
%lowPassfilter creates an FIR low pass filter using kaiser order window and
%filters a set of data, and removes phase delay from the filter
%   data the data to be filtered
%   fcuts a 1x2 matrix containing the filter cutoff rolloff. i.e. [10 11]
%   creates a filter with a cutoff of 10 Hz, that rolls off to 11 Hz
%   fs is the sampling rate of the data
%   returns cleanedFilteredData, the data that is filtered from the
%   constructed filter.

fsamp = fs;
%fcuts = [5 6]; %set the rolloff to be from 5 Hz to 6 Hz
mags = [1 0]; %passband has gain of 1, stopband has gain of 0
devs  = [0.001, 0.1]; %accept .01% ripple in passband, 1% ripple in stopband

[n,Wn,beta,ftype] = kaiserord(fcuts,mags,devs,fsamp);

hh = fir1(n,Wn,ftype,kaiser(n+1,beta),'noscale');
%freqz(hh);
%filter the ecg signal
filteredData = filter(hh,1,data);

%invert the ecg signal, to filter the signal backwards
dataInverted = fliplr(data);
filteredInvertedData = filter(hh,1,dataInverted);
%reinvert the inverted filtered ecg signal the signal right
reInvertedFilteredData = fliplr(filteredInvertedData);

filterDelay = round(length(hh)/2);

%readjust the positioning due to phase offset.
adjustedFilteredData = filteredData(filterDelay:end); 
adjustedReInvertedFilteredData = [mean(reInvertedFilteredData(1:(end-filterDelay)-20))*ones(1,filterDelay),...
                                    reInvertedFilteredData(1:(end-filterDelay))];

cleanedFilteredData = [adjustedFilteredData(1:round(length(adjustedFilteredData)/2)),... 
                        adjustedReInvertedFilteredData(round(length(adjustedFilteredData)/2)+1:end)];

end

