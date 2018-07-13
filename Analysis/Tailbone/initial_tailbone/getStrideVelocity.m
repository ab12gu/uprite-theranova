function [strideVelocity, meanStrideVelocity] = getStrideVelocity(accelSec,position, velocity, hs_locations)
%UNTITLED Summary of this function goes here
%   Detailed explanation goes here

strideVelocity = [];
meanStrideVelocity = [];
for i=1:length(hs_locations)-1
    startIndex = find(round(accelSec*100) == round(hs_locations(i)*100));
    endIndex = find(round(accelSec*100) == round(hs_locations(i+1)*100));
    strideVelocity = [strideVelocity,  9.81*(position(endIndex)- position(startIndex))/(accelSec(endIndex)- accelSec(startIndex))];
    meanStrideVelocity = [meanStrideVelocity,  9.81*mean(velocity(startIndex:endIndex))];
end



end

