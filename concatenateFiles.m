% Concatenate variable number of binary files to one outputFile.
function concatenateFiles(outputFile, varargin)

if nargin < 1
    error('Please provide an output file name.')
end

fprintf('Writing to outputFile %s \n', outputFile);

% Discard current contents of the output file.
fid = fopen(outputFile, 'w');
fclose(fid);

% Append each input file to the output file.
fid = fopen(outputFile, 'a');
try
    for ii = 1:numel(varargin)
        inputFile = varargin{ii};
        fprintf('Appending to input file %s \n', inputFile);

        fileMap = memmapfile(inputFile, 'Format', 'uint8', 'Repeat', inf);
        fileByteCount = numel(fileMap.Data);

        blocksize = 500;
        nblocks = ceil(fileByteCount ./ blocksize);
        for iblock = 1:nblocks
            dataStart = (iblock - 1) * blocksize + 1;
            dataEnd = min(fileByteCount, iblock * blocksize);
            dataRange = dataStart:dataEnd;
            fwrite(fid, fileMap.Data(dataRange), 'uint8');
        end
    end

    fclose(fid);
catch e
    fclose(fid);
    error(e);
end

fprintf('Done writing to outputFile %s \n', outputFile);
