# -*- coding: utf-8 -*-
"""
Created on Mon Feb 27 13:07:41 2023
@author: isaer291

GOAL ---------> create 2 TMS simulations per xml file for a given patient

BACKGROUND ---> looking for e-fields caused by real TMS treatment using patient
                data inc. TMS coil locations and T1 MRI-based head models.
                
                Subjects are depressed and schizophrenic patients who recieved
                dlPFC-targeted rTMS. Here we investigate which areas were
                actually targeted and later on, look at network effects.
                        ## note that average coil location is flipped
                        180°, as this was done digitally in the coil settings
"""

### imports
import numpy as np
import os
from simnibs import sim_struct, run_simnibs, localite
import datetime

### initialize a session
s = sim_struct.SESSION()
s2 = sim_struct.SESSION()

### path to head mesh
headmesh = r"D:\Isabels_workspace\rawdata for headmodels\T1_patients_from233\m2m_sub-9"
s.subpath = headmesh
s2.subpath = headmesh

### output folder
output_folder = r"C:\Users\isaer291\OneDrive - Vrije Universiteit Amsterdam\simulation_results\subject_401"



                                         # create a unique file per similation
                                         
### read all XML files in the directory
xml_dir = r"D:\Isabels_workspace\subject_xml_files\sub-401"
xml_files = [f for f in os.listdir(xml_dir) if f.endswith(".xml")]

for xml_file in xml_files:
    now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    xml_folder = os.path.splitext(xml_file)[0]
    output_folder_pos1 = os.path.join(output_folder, f"{xml_folder}_pos1_{now}")
    output_folder_pos2 = os.path.join(output_folder, f"{xml_folder}_pos2_{now}")

    print(f"Processing file {xml_file}")
    
    ### read the .xml file
fn = os.path.join(xml_dir, xml_file)
tmslist = localite().read(fn)


                                                      # extract coil locations
                                                  
### loop through to extract coil location matrix
coil_pos = []
for pos in tmslist.pos:
    matrix = np.array(pos.matsimnibs).reshape((4, 4))
    coil_pos.append(matrix)

### set EEG cap to None for all positions
for pos in tmslist.pos:
    pos.eeg_cap = None
    
                                                   # split data; calc averages
                                                   
    ### split data in half
    n = len(coil_pos)
    coil_pos_1_all = coil_pos[:n//2]
    coil_pos_2_all = coil_pos[n//2:]

    # Compute the average coil positions
    avg_coil_pos_1 = np.mean(coil_pos_1_all, axis=0)
    avg_coil_pos_2 = np.mean(coil_pos_2_all, axis=0)

                                                       # group 2: flip x and y                                    

    ### flip coil direction in group 2
    avg_coil_pos_2[:3, :2] *= -1
    print(avg_coil_pos_2)

    # create unique folder per simulation
    now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_folder_pos1 = os.path.join(output_folder, f"pos1_{now}")
    output_folder_pos2 = os.path.join(output_folder, f"pos2_{now}")
                                                        # run simulation 1
    ### create tms list object
    tms1 = s.add_tmslist()
    
    ### specify coil used
    tms1.fnamecoil = r"C:\Users\isaer291\SimNIBS-4.0\simnibs_env\Lib\site-packages\simnibs\resources\coil_models\Drakaki_BrainStim_2022\MagVenture_Cool-D-B80.ccd"
   
    ### add avg coil positions
    pos1 = sim_struct.POSITION()
    tms1.pos.append(pos1)
    pos1.matsimnibs = avg_coil_pos_1
    s.eeg_cap = None
    
    ### run simulation
    s.pathfem = output_folder_pos1
    run_simnibs(s)
    
    
    ### wait for simulation 1 to complete
while run_simnibs.check_status(s):
    pass

### delete MSH files generated after the first simulation
for file in os.listdir(output_folder_pos1):
    if file.endswith(".msh"):
        os.remove(os.path.join(output_folder_pos1, file))

                                                            # run simulation 2

    ### create tms list object
    tms2 = s2.add_tmslist()
    
    ### specify coil used
    tms2.fnamecoil = r"C:\Users\isaer291\SimNIBS-4.0\simnibs_env\Lib\site-packages\simnibs\resources\coil_models\Drakaki_BrainStim_2022\MagVenture_Cool-D-B80.ccd"
    
    ### add avg coil positions
    pos2 = sim_struct.POSITION()
    tms2.pos.append(pos2)
    pos2.matsimnibs = avg_coil_pos_2
    s2.eeg_cap = None
    
    ### sun simulation
    run_simnibs(s2)
    
    ### wait for simulation 2 to complete
while run_simnibs.check_status(s2):
    pass

### delete MSH files generated after the second simulation
for file in os.listdir(output_folder_pos2):
    if file.endswith(".msh"):
        os.remove(os.path.join(output_folder_pos2, file))