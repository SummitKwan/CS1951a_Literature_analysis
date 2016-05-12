clear;
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
C = zeros(length(X),3);
for i = 1:length(X)
    tmp = corrcoef(N(i,:),1:rows);
    C(i,1) = tmp(1,2);
end
hold on;
k = 1;
figure(1)
for i = 1:length(X)
    if C(i,1) > 0.95
        tmp = polyfit(1:rows, N(i,:),1);
        C(i,2:3) = tmp;
        if C(i,3) < 0.05
            plot(2009:2015,N(i,:));
            legendInfo(k) = i;
            k = k + 1;
        end
    end
end
k
legend(T{legendInfo})
fileID = fopen('top_by_correlation.csv','w');
for i = 1:length(legendInfo)
    t = T{legendInfo(i)};
    fprintf(fileID,t(1:length(t)-1));
    fprintf(fileID, ',');
    fprintf(fileID, '%f,%f,%f\n', C(legendInfo(i), 1),C(legendInfo(i), 2), C(legendInfo(i), 3));
end
fclose(fileID);