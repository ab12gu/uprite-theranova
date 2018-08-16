function [result] = integrateIMU(seconds, value)
%UNTITLED2 Summary of this function goes here
%   Detailed explanation goes here

result = zeros(1,length(seconds));
for i = 2:length(seconds)
    result(i) = result(i-1) + value(i).*(seconds(i)-seconds(i-1));

end

end

