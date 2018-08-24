function [ firstDiff ] = getFirstDifference(value, interval)
%UNTITLED3 Summary of this function goes here
%   Detailed explanation goes here

firstDiff = zeros(1,length(value));

for i=(interval+1):length(value)
    firstDiff(i) = value(i) - value(i-interval);
end
end

