function [dataStruct] = extractUpRiteData(fileName)
%extractUpRiteData Extracts the data out of a sensor data file and converts
%it to a struct value.
%   Detailed explanation goes here
fid = fopen(fileName);
firstLine = fgets(fid); %get the header information... Actually gets all file information...
%String replace function
%Replaces the enter command with a space character
firstLine = strrep(firstLine,sprintf('\n'),'');
firstLine = strrep(firstLine,sprintf('\r'),'');

dataStruct.sampRate = [];
dataStruct.sampRateUnits = [];
dataStruct.scale = [];
dataStruct.scaleUnits = [];

parsingFormat = [];

parsingFormat1 = 'X_LSB X_MSB Y_LSB Y_MSB Z_LSB Z_MSB';
parsingFormat2 = 'A0 A1 A2 A3';

firstLineInfo = strsplit(firstLine,',\t'); %Saves 2nd part of string after \t = tab 
for i = 1:length(firstLineInfo) %iterate through firstlineinfo
    data = strsplit(firstLineInfo{i},': '); %save data...
    if strcmp('sampRate',data{1}) %compares values and returns 1 true, 0 false
       sampRateInfo = strsplit(data{2},' ');
       dataStruct.sampRate =  str2num(sampRateInfo{1});
       dataStruct.sampRateUnits = sampRateInfo{2};
    elseif strcmp('scale',data{1})
        scaleInfo = strsplit(data{2},'/');
        dataStruct.scale = str2num(scaleInfo{1});
        dataStruct.scaleUnits = scaleInfo{2};
    elseif strcmp('Format',data{1}(1:6))
        parsingFormat = data{2};
    end
    
end

if strcmp(parsingFormat, parsingFormat1)
    dataStruct.rawdata.x = [];
    dataStruct.rawdata.y= [];
    dataStruct.rawdata.z= [];
    dataStruct.rawdata.seconds = [];
    dataStruct.data.x = [];
    dataStruct.data.y = [];
    dataStruct.data.z = [];
    dataStruct.data.seconds = [];
    byteStream = fread(fid);
    % Parse Data
    %  [X_LSB, X_MSB, Y_LSB, Y_MSB, Z_LSB, Z_MSB] 
    for i = 1:6:length(byteStream)
        xBytes = [byteStream(i), byteStream(i+1)];
        xAx = double(typecast(uint8(xBytes),'int16'));
        dataStruct.rawdata.x = [dataStruct.rawdata.x xAx];
        dataStruct.data.x = [dataStruct.data.x xAx/dataStruct.scale];
    
        yBytes = [byteStream(i+2), byteStream(i+3)];
        yAx = double(typecast(uint8(yBytes),'int16'));
        dataStruct.rawdata.y = [dataStruct.rawdata.y yAx];
        dataStruct.data.y = [dataStruct.data.y yAx/dataStruct.scale];

        zBytes = [byteStream(i+4), byteStream(i+5)];
        zAx = double(typecast(uint8(zBytes),'int16'));
        dataStruct.rawdata.z = [dataStruct.rawdata.z zAx];
        dataStruct.data.z = [dataStruct.data.z zAx/dataStruct.scale];
    end

    if strcmp(dataStruct.sampRateUnits,'Hz')
        dataStruct.rawdata.seconds = 0:1/dataStruct.sampRate:(length(dataStruct.data.x)-1)/dataStruct.sampRate;
        dataStruct.data.seconds = dataStruct.rawdata.seconds;
    else %TODO: handle different cases where the samp rate units are weird
        dataStruct.rawdata.seconds = 0:1/dataStruct.sampRate:(length(dataStruct.data.x)-1)/dataStruct.sampRate;
        dataStruct.data.seconds = dataStruct.rawdata.seconds;
    end

elseif strcmp(parsingFormat, parsingFormat2)
    dataStruct.rawdata.values = [];
    dataStruct.rawdata.seconds = [];
    dataStruct.data.values = [];
    dataStruct.data.seconds = [];
    byteStream = fread(fid);
    % Parse Data
    %  [A0 A1 A2 A3] 
    for i = 1:4:length(byteStream)
        bytes = [byteStream(i), byteStream(i+1), byteStream(i+2), byteStream(i+3)];
        value = double(typecast(uint8(bytes),'int32'));
        dataStruct.rawdata.values = [dataStruct.rawdata.values value];
        dataStruct.data.values = [dataStruct.data.values value/dataStruct.scale];
    end
    
    if strcmp(dataStruct.sampRateUnits,'Hz')
        dataStruct.rawdata.seconds = 0:1/dataStruct.sampRate:(length(dataStruct.data.values)-1)/dataStruct.sampRate;
        dataStruct.data.seconds = dataStruct.rawdata.seconds;
    else %TODO: handle different cases where the samp rate units are weird
        dataStruct.rawdata.seconds = 0:1/dataStruct.sampRate:(length(dataStruct.data.values)-1)/dataStruct.sampRate;
        dataStruct.data.seconds = dataStruct.rawdata.seconds;
    end
end

fclose(fid);
end

