% Reward delay sensitivity (criteria check)
%% GET DATA for computer session
dbc = db.labdb.getConnection();
dbc.use('fmri');
% ShortDelay_Behavior
csdelay_S = 'select subjid, a.sessid, trialnum, rewmag, delay, choice from sessions a, trials b where a.sessid = b.sessid and treatment = "ShortDelay_Behavior" and sessiondate > "2019-08-20" order by subjid, a.sessid, trialid';
data_cs_S = dbc.query(csdelay_S);
% LongDelay_Behavior
csdelay_L = 'select subjid, a.sessid, trialnum, rewmag, delay, choice from sessions a, trials b where a.sessid = b.sessid and treatment = "LongDelay_Behavior" and sessiondate > "2019-08-20" order by subjid, a.sessid, trialid';
data_cs_L = dbc.query(csdelay_L);
% count subjects' missed buttonpresses
subjects0 = unique(data_cs_S.subjid);
MB = zeros(size(subjects0,1),3);
for sb=(1:numel(subjects0))
    MB(sb,1) = subjects0(sb); 
    data_S_subj = data_cs_S((data_cs_S.subjid==subjects0(sb)),:);
    MB(sb,2) = size(data_S_subj(isnan(data_S_subj.choice),:),1)/size(data_S_subj,1);
    data_L_subj = data_cs_L((data_cs_L.subjid==subjects0(sb)),:);
    MB(sb,3) = size(data_L_subj(isnan(data_L_subj.choice),:),1)/size(data_L_subj,1);
end
% remove subjects' missed buttonpresses
data_cs_S(isnan(data_cs_S.choice),:)=[];
data_cs_L(isnan(data_cs_L.choice),:)=[];
% % FIT GLM: Are all subjects sensitive to reward and delay?
subjects = unique(data_cs_S.subjid);
% run the model
modelspec = 'choice ~ rewmag + delay';
mdl_S = fitglm(data_cs_S,modelspec,'Distribution','binomial'); 
p_val_S = mdl_S.Coefficients.pValue 
% check: overall both betas significant, intercept not significant
mdl_L = fitglm(data_cs_L,modelspec,'Distribution','binomial'); 
p_val_L = mdl_L.Coefficients.pValue 
% check: overall both betas significant, intercept not significant

%% NOW RUN the model for each subject: choice ~ rewmag + probability
% p-values for betas by subject
X_S = zeros(size(subjects,1),3); % for Short sessions combined
X_L = zeros(size(subjects,1),3); % for Long sessions combined
for i=(1:numel(subjects))
    data_S_subj = data_cs_S((data_cs_S.subjid==subjects(i)),:);
    mdls_S = fitglm(data_S_subj,modelspec,'Distribution','binomial');
    p_vals_S = mdls_S.Coefficients.pValue;
    X_S(i,1) = subjects(i); 
    X_S(i,2) = p_vals_S(2);
    X_S(i,3) = p_vals_S(3);
    data_L_subj = data_cs_L((data_cs_L.subjid==subjects(i)),:);
    mdls_L = fitglm(data_L_subj,modelspec,'Distribution','binomial');
    p_vals_L = mdls_L.Coefficients.pValue;
    X_L(i,1) = subjects(i); 
    X_L(i,2) = p_vals_L(2);
    X_L(i,3) = p_vals_L(3);
end

%% check mean(choice) for each task subject by subject
% sessionid_L = unique(data_cs_L.sessid);
% sessionid_S = unique(data_cs_S.sessid);
Mean_L = zeros(size(subjects,1),2);
Mean_S = zeros(size(subjects,1),2);
for m=(1:numel(subjects))
    choice = data_cs_L((data_cs_L.subjid == subjects(m)),:).choice;
    Mean_L(m,1) = subjects(m);
    Mean_L(m,2) = mean(choice);
end
for n=(1:numel(subjects))
    choice = data_cs_S((data_cs_S.subjid == subjects(n)),:).choice;
    Mean_S(n,1) = subjects(n);
    Mean_S(n,2) = mean(choice);
end
%% check who passes 2 criteria and who are best candidates to pass
criteriapass = table;
criteriapass.subjid = X_L(:,1);
criteriapass.sensrewlong = X_L(:,2)<0.05;
criteriapass.sensdellong = X_L(:,3)<0.05;
criteriapass.sensrewshort = X_S(:,2)<0.05;
criteriapass.sensdelshort = X_S(:,3)<0.05;
criteriapass.meanlong19 = Mean_L(:,2)>=0.1&Mean_L(:,2)<=0.9;
criteriapass.meanshort19 = Mean_S(:,2)>=0.1&Mean_S(:,2)<=0.9;
criteriapass.passall = criteriapass.sensrewlong+criteriapass.sensdellong+criteriapass.sensrewshort+criteriapass.sensdelshort+criteriapass.meanlong19+criteriapass.meanshort19;
% who missed button presses
mbp = table;
mbp.subjid = MB(:,1);
mbp.mbpS = MB(:,2);
mbp.mbpL = MB(:,3);
% join tables
criteriapass = join(criteriapass,mbp);
figure;
scatter(Mean_S(:,2),Mean_L(:,2),[],'k');
hold on;
scatter(Mean_S(criteriapass.passall==6,2),Mean_L(criteriapass.passall==6,2),[],'b')
scatter(Mean_S(criteriapass.passall==5,2),Mean_L(criteriapass.passall==5,2),[],'r')
xlim([0 1]);
ylim([0 1]);
draw.unity;
line([0,1],[0.1,0.1]);
line([0,1],[0.9,0.9]);
line([0.1,0.1],[0,1]);
line([0.9,0.9],[0,1]);
text(0.1,0.8,'pass all','Color','blue','FontSize', 14);
text(0.1,0.7,'pass all but one','Color','red','FontSize', 14);
xlabel('Short P(later)');
ylabel('Long P(later)');
set (gca,'FontSize', 14);
set(gcf,'PaperPosition',[0 0 5 4]);
set(gcf, 'PaperSize', [5 4]);
saveas(gcf, '~/Downloads/passcriteria.png','png');

