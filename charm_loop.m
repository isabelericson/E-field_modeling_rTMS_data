%%% batching running charm function

%% GOAL: loop through all subject T1 MRI images to create simnibs head model msh files
%% first step to create simulations to based on patient data




% set working and output directory
indir='C:\Users\isaer291\Documents\datasets\rawdata for headmodels\T1_patients_from233';
outdir='C:\Users\isaer291\Documents\datasets\rawdata for headmodels\T1_patients_from233\headmodel_results';


% target all T1 images in working directory
t1_images=dir(fullfile(indir, '*nii.gz'));

% charm function loop
for i = 1:length(t1_images)
    t1_image = t1_images(i).name;
    charm_command = sprintf('charm --forceqform --forcerun sub-%d "%s"', i, fullfile(indir, t1_image));
    system(charm_command);
end
