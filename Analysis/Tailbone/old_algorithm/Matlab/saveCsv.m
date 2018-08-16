dataCsvFile = ['baroRawData','.csv']
fid = fopen(dataCsvFile, 'w')
fields = fieldnames(altitude);
for i=1:length(fields)
    if ~(strcmp(fields{i}, 'rawdata') || strcmp(fields{i}, 'data'))
        fieldValue = getfield(altitude,fields{i});
        if isnumeric(fieldValue)
            fprintf(fid,'%s, %d,\n',fields{i}, fieldValue);
        else
            fprintf(fid,'%s, %s,\n',fields{i}, fieldValue);
        end
    end
end
rawDataFields = fieldnames(altitude.rawdata);
for j=1:length(rawDataFields)
    fprintf(fid,'rawData_%s,',rawDataFields{j});
end
dataFields = fieldnames(altitude.data);
for k=1:length(dataFields)
    fprintf(fid,'data_%s,',dataFields{k});
end
fprintf(fid,'\n');
fclose(fid);
dataValues = [];
for m = 1:length(rawDataFields)
    dataValues = [dataValues, getfield(altitude.rawdata,rawDataFields{m})'];
end
for n = 1:length(dataFields)
    dataValues = [dataValues, getfield(altitude.data,dataFields{n})'];
end
dlmwrite(dataCsvFile, dataValues,'-append');