clear;
load('data_half.csv');
X = data_half;
fid = fopen('topic_half.csv'); 
tmp = fread(fid, '*char')';
fclose(fid);
T = regexp(tmp, '\n', 'split'); 
N = zeros(size(X));
rows = length(X(1,:));
cats = ['A','B','C','D','E','F','G'];
for j = 1:rows
    X(:,j) = X(:,j)/sum(X(:,j));
end

legendInfo = {{},{},{},{},{},{}};
legendCount = zeros(1,7);

for i = 1:length(X)
    t = T{i}; c = t(1);
    for j = 1:length(cats)
        if c == cats(j)
            figure(j)
            hold on;
            plot(2013:2015,X(i,:));
            legendCount(j) = legendCount(j) + 1;
            legendInfo{j}{legendCount(j)} = T{i};
        end
    end
end

for j = 1:length(cats)
    figure(j);
    legend(legendInfo{j}{:})
    set(gca,'XTick',[2013,2014,2015])
    title(cats(j));
    xlabel('Year');
    ylabel('Frequency');
end

fileID = fopen('linear_reg_half.csv','w');
for i = 1:length(X)
    t = T{i};
    fprintf(fileID,t(1:length(t)-1));
    fprintf(fileID, ',');
    tmp = polyfit(1:3, X(i,:),1);
    tmp2 = corrcoef(X(i,:),1:rows);
    fprintf(fileID, '%f,%f,%f\n', tmp2(2,1),tmp(1),tmp(2));
end
set(gca,'XTick',[2013,2014,2015])
fclose(fileID);
    
