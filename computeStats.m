% Load a binary file as bytes and compute some stats, like min and max.
function computeStats(inputFile, outputFile)

if nargin < 1 || ~isfile(inputFile)
    error('Please provide an input file name.')
end

if nargin < 2
    [path, name] = fileparts(inputFile);
    outputFile = fullfile(path, [name '-stats.json']);
end

fprintf('Reading inputFile %s, writing stats to %s.\n', inputFile, outputFile);

fileMap = memmapfile(inputFile, 'Format', 'uint8', 'Repeat', inf);

stats.count = numel(fileMap.Data);
stats.min = min(fileMap.Data);
stats.max = max(fileMap.Data);
stats.mean = mean(fileMap.Data);

outputJson = jsonencode(stats, 'PrettyPrint', true);
fid = fopen(outputFile, 'w');
try
    fwrite(fid, outputJson);
    fclose(fid);
catch e
    fclose(fid);
    error(e);
end

fprintf('Done writing stats to %s.\n', outputFile);
