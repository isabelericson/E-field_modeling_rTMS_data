# -*- coding: utf-8 -*-
"""
Created on Thu Mar  9 12:50:36 2023

@author: isaer291
"""

##### GOAL--------> BATCH RUN STIMULATIONS.
#                   use patient iTBS data to recreate treatment as a simulation
#                   in order to investigate potential differences between targeted
#                   vs. real effects of iTBS. Did we potentiate the targeted region?
#                   are there any network effects?

##### Background -> Subjetcts consist of treatment-resistent depression patients
#                   who recieved iTBS targeting the dlPFC

##### NEXT PHASE--> Investigate network effects of iTBS using simulation results 
#                   and C toolbox in MATLAB.



                                                                       # setup                          
### imports
import numpy as np
import os
from simnibs import sim_struct, run_simnibs, localite
import datetime

### initialize a session
s = sim_struct.SESSION()
s2 = sim_struct.SESSION()

### data directory
data_dir = r"D:\Isabels_workspace\data_dir"

### path to head mesh
subjects = ['sub-215', 'sub-216', 'sub-217', 'sub-218', 'sub-219', 'sub-220', 'sub-221', 'sub-223', 'sub-224', 'sub-225', 'sub-226', 'sub-227', 'sub-228', 'sub-229', 'sub-230', 'sub-231', 'sub-232', 'sub-233', 'sub-234', 'sub-235', 'sub-236', 'sub-237', 'sub-238', 'sub-239', 'sub-240', 'sub-241', 'sub-242', 'sub-401', 'sub-402', 'sub-403', 'sub-404', 'sub-405', 'sub-406', 'sub-407', 'sub-408', 'sub-410', 'sub-411', 'sub-412', 'sub-413']
 

### output folder
#output_folder = r"C:\Users\isaer291\OneDrive - Vrije Universiteit Amsterdam\results"



                                                     ### stimulation intensity
### specify intensity values as a %
### specify intensity values as a %
intensity_values = {
    0.4: ['sub-402', 'sub-403', 'sub-404', 'sub-405', 'sub-406', 'sub-407', 'sub-408', 'sub-410', 'sub-411', 'sub-412', 'sub-413'],
    0.44: ['sub-232', 'sub-233', 'sub-234', 'sub-235', 'sub-236', 'sub-237', 'sub-238', 'sub-239', 'sub-240', 'sub-241'],
    0.52: ['sub-215', 'sub-216', 'sub-217', 'sub-218', 'sub-219', 'sub-220', 'sub-221', 'sub-223', 'sub-224', 'sub-225', 'sub-226', 'sub-227', 'sub-228', 'sub-229', 'sub-230', 'sub-231'],
    0.61: ['sub-242'],
    0.63: ['sub-401']
}

### create empty lists to store subject and intensity values
intensity_list = []
subject_list = []

for intensity, sub_list in intensity_values.items():
    for sub in sub_list:
        ### check if the directory for the subject exists
        sub_dir = os.path.join(data_dir, sub)
        if not os.path.exists(sub_dir):
            continue
        
        ### add current subject and intensity values to lists
        intensity_list.append(intensity)
        subject_list.append(sub)
        
        ### specify headmesh and xml directory
        headmesh = os.path.join(data_dir, sub, "m2m_" + sub)
        xml_dir = os.path.join(data_dir, sub, "xml_files")
        output_folder = os.path.join(data_dir, sub, "simulation_results")

        ### make sure the xml directory exists
        if not os.path.exists(xml_dir):
            continue

        ### get a list of xml files for this subject
        xml_files = [f for f in os.listdir(xml_dir) if f.endswith(".xml")]

        ### loop through xml files and run simulations
        for xml_file in xml_files:
            print(f"Processing file {xml_file}")
            now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            xml_folder = os.path.splitext(xml_file)[0]
            output_folder_pos1 = os.path.join(output_folder, f"{xml_folder}_pos1_{now}")
            output_folder_pos2 = os.path.join(output_folder, f"{xml_folder}_pos2_{now}")
            fn = os.path.join(xml_dir, xml_file)
            tmslist = localite().read(fn)
            coil_pos = []
            for pos in tmslist.pos:
                matrix = np.array(pos.matsimnibs).reshape((4, 4))
                coil_pos.append(matrix)
                pos.eeg_cap = None

                                                      # average coil location for 2 groups
            ### split data in half
            n = len(coil_pos)
            coil_pos_1 = coil_pos
            coil_pos_2 = coil_pos
            
            ### Append the coil positions to the running lists
            coil_pos_1_all = coil_pos_1
            coil_pos_2_all = coil_pos_2
            
            # Compute the average coil positions
            avg_coil_pos_1 = np.mean(coil_pos_1_all, axis=0)
            avg_coil_pos_2 = np.mean(coil_pos_2_all, axis=0)
            
            
                                                            # group 2: flip coil direction                                    
            
            ### flip coil direction in group 2
            avg_coil_pos_2[:3, :2] *= -1
            print(avg_coil_pos_2)
            
            
                                                                         # run simulations
            ### run simulation 1
            s = sim_struct.SESSION()
            s.subpath = headmesh
            s.pathfem = output_folder_pos1
            tms1 = s.add_tmslist()
            tms1.fnamecoil = os.path.join('Drakaki_BrainStim_2022', 'MagVenture_Cool-D-B80.ccd')
            pos1 = sim_struct.POSITION()
            tms1.pos.append(pos1)
            pos1.matsimnibs = avg_coil_pos_1
            s.eeg_cap = None
            tms1.dcoil = intensity
            run_simnibs(s)
            
            ### run simulation 2
            s2 = sim_struct.SESSION()
            s2.subpath = headmesh
            s2.pathfem = output_folder_pos2
            tms2 = s2.add_tmslist()
            tms2.fnamecoil = os.path.join('Drakaki_BrainStim_2022', 'MagVenture_Cool-D-B80.ccd')
            pos2 = sim_struct.POSITION()
            tms2.pos.append(pos2)
            pos2.matsimnibs = avg_coil_pos_2
            s2.eeg_cap = None
            tms2.dcoil = intensity
            run_simnibs(s2)

