function [ output_args ] = saveSensorStructToCsv(sensorStruct, filename)
%saveSensorStructToCsv takes in a structure containing sensor data, and an
%creates a csv file containing the data using the given filename
%   Detailed explanation goes here
fid = fopen(filename, 'w');
fields = fieldnames(sensorStruct);
for i=1:length(fields)
    if ~(strcmp(fields{i}, 'rawdata') || strcmp(fields{i}, 'data') || strcmp(fields{i},'filterData')) 
        fieldValue = getfield(sensorStruct,fields{i});
        if isnumeric(fieldValue)
            fprintf(fid,'%s, %d,\n',fields{i}, fieldValue);
        else
            fprintf(fid,'%s, %s,\n',fields{i}, fieldValue);
        end
    end
end
rawDataFields = fieldnames(sensorStruct.rawdata);
for j=1:length(rawDataFields)
    fprintf(fid,'rawData_%s,',rawDataFields{j});
end
dataFields = fieldnames(sensorStruct.data);
for k=1:length(dataFields)
    fprintf(fid,'data_%s,',dataFields{k});
end

%if there is filtered data
if isfield(sensorStruct, 'filterData')
    filterDataFields = fieldnames(sensorStruct.filterData);
    for i=1:length(filterDataFields)
        filterDataInfo = getfield(sensorStruct.filterData, filterDataFields{i});
        filterDataInfoFields = fieldnames(filterDataInfo);
        for j =1:length(filterDataInfoFields)
            fprintf(fid,[filterDataFields{i},'_%s,'],filterDataInfoFields{j});
        end
    end
end

fprintf(fid,'\n');
fclose(fid);
dataValues = [];
for m = 1:length(rawDataFields)
    dataValues = [dataValues, getfield(sensorStruct.rawdata,rawDataFields{m})'];
end
for n = 1:length(dataFields)
    dataValues = [dataValues, getfield(sensorStruct.data,dataFields{n})'];
end
%append filtered data
if isfield(sensorStruct, 'filterData')
    for i=1:length(filterDataFields)
        filterDataInfo = getfield(sensorStruct.filterData, filterDataFields{i})
        filterDataInfoFields = fieldnames(filterDataInfo)
        for j =1:length(filterDataInfoFields)
            dataValuesSize = size(dataValues)
            dataSize = size(getfield(filterDataInfo, filterDataInfoFields{j})')
            dataValues = [dataValues, getfield(filterDataInfo, filterDataInfoFields{j})'];
        end
    end
    
    
end
dlmwrite(filename, dataValues,'-append');
%fclose(fid);
end

