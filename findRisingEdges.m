% Load a binary file and precomputed stats, look for threshold crossings.
function findRisingEdges(binaryFile, statsFile, outputFile, threshold)

if nargin < 1 || ~isfile(binaryFile)
    error('Please provide an input binary file name.')
end

if nargin < 2 || ~isfile(statsFile)
    error('Please provide an input stats JSON file name.')
end

if nargin < 3 || isempty(outputFile)
    [path, name] = fileparts(statsFile);
    outputFile = fullfile(path, [name '-edges.json']);
end

if nargin < 4
    threshold = 0.75;
end

fprintf('Reading binaryFile %s and statsFile %s, writing threshold crossings (%.2f of range) to %s.\n', ...
    binaryFile, statsFile, threshold, outputFile);

% User precomputed stats to choose a "high" level in the binary data.
statsJson = fileread(statsFile);
stats = jsondecode(statsJson);
highLevel = stats.min + threshold * (stats.max - stats.min);

% Scan for where the data goes from not-high to high.
fileMap = memmapfile(binaryFile, 'Format', 'uint8', 'Repeat', inf);
isHigh = fileMap.Data >= highLevel;
isRising = diff(isHigh);
risingEdgeTimes = find(isRising > 0);

risingEdgeJson = jsonencode(risingEdgeTimes, 'PrettyPrint', false);
fid = fopen(outputFile, 'w');
try
    fwrite(fid, risingEdgeJson);
    fclose(fid);
catch e
    fclose(fid);
    error(e);
end

% clf
% hold on
% plot(fileMap.Data, '.b')
% plot(find(isHigh), fileMap.Data(isHigh), '.r')
% plot(risingEdgeTimes + 1, fileMap.Data(risingEdgeTimes + 1), '*g')
% hold off

fprintf('Done writing rising edge times to %s.\n', outputFile);