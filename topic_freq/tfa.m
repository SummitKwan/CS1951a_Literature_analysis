clear;
load('data_small.csv');
X = data_small;
fid = fopen('topic_small.csv'); 
tmp = fread(fid, '*char')';
fclose(fid);
T = regexp(tmp, '\n', 'split'); 
N = zeros(size(X));
rows = length(X(1,:));
for j = 1:rows
    X(:,j) = X(:,j)/sum(X(:,j));
end
plot(2013:2015,X');
xlabel('Year');
ylabel('Frequency');
legend(T{1:length(T)-1});
fileID = fopen('linear_reg_master_catagory.csv','w');
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
    
