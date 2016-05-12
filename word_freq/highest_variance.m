clear; hold off; hold on;
load('data.csv');
X = data;
fid = fopen('titles.csv'); 
tmp = fread(fid, '*char')';
fclose(fid);
T = regexp(tmp, '\n', 'split'); 
N = zeros(size(X));
rows = length(X(1,:));
for i = 1:length(X)
    N(i,:) = X(i,:)/sum(X(i,:));
end
C = zeros(length(X),1);
k = 1;
figure(1)
for i = 1:length(X)
    C(i) = std(N(i,:));
    if C(i) > 0.29
        plot(2009:2015,N(i,:));
        legendInfo(k) = i;
        k = k + 1;
    end
end
k
legend(T{legendInfo})
fileID = fopen('highest_variance.csv','w');
for i = 1:length(legendInfo)
    t = T{legendInfo(i)};
    fprintf(fileID,t(1:length(t)-1));
    fprintf(fileID, ',');
    fprintf(fileID, '%f\n', C(legendInfo(i)));
end
fclose(fileID);