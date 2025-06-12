% Permutation Tests
fits = readtable('joint_fits.csv');

% Short: computer session vs fMRI session
[p,ci] = bootmean(fits.K_S_x-fits.K_S_y,'boots',10000) 
% x - fmri; y - computer
mean(log(exp(fits.K_S_x)/86400))
mean(log(exp(fits.K_S_y)/86400))
% Mk_S_fmri = -2.2743 Mk_S_computer = -2.3975
% p = 0.1010 ci = -0.0256    0.2605

% Long: computer session vs fMRI session
[p,ci] = bootmean(fits.K_L_x-fits.K_L_y,'boots',10000) 
% x - fmri; y - computer
mean(fits.K_L_x)
mean(fits.K_L_y)
% Mk_L_fmri = -3.3009 Mk_L_computer = -3.3957
% p = 0.4906 ci = -0.1812    0.3623
