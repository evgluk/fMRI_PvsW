% Deming Regression
c_fits = readtable('stanfits_computer.csv');
params_a = table2array(c_fits(:,:));
s_idx = find(strcmpi(c_fits.Properties.VariableNames,'K_S'));
x(:,1) = log(exp(params_a(:,s_idx))/86400);
l_idx = find(strcmpi(c_fits.Properties.VariableNames,'K_L'));
y(:,1) = params_a(:,l_idx);
b = deming(x(:,1), y(:,1));
%-- 10/02/2025 21:33 --% b = 3.5679 2.6922

