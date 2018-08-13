function [result] = getFirstIntegration(value)
%UNTITLED2 Summary of this function goes here
%   Detailed explanation goes here

result = zeros(1,length(value));
for i = 2:length(value)
    result(i) = result(i-1) + value(i);
end

end

