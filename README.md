# Indoor localization for an Augmented Reality-based assissting system


We provide a guideline in which it’s described what actions we took to build our indoor localization model for the future reference step by step as following: 
1. We collected our 3D point cloud model with FARO Focus laser scanner
2. For our case study, we collected the test data with Microsoft HoloLens2 via a user walks through the indoor environment and collect the triangular meshes from around him/her. Then this mesh maps should be converted to 3D point cloud.
3. In the next step we registered the point cloud scan files with the Autodesk ReCap software to have an integrated and accurate 3D model. Here you can follow the guideline shows in [Manual Registration](https://knowledge.autodesk.com/support/recap/learn-explore/caas/CloudHelp/cloudhelp/2018/ENU/Reality-Capture/files/GUID-37FBC8AE-2674-4E11-97F2-A81806A5BABC-htm.html) for registering structured (fixed-location e.g. Faro laser scanner) point cloud scan files.
4. For registering the HoloLens2 point cloud files, you should follow the guideline in [Registering Unstructured Scans](https://knowledge.autodesk.com/support/recap/learn-explore/caas/CloudHelp/cloudhelp/2018/ENU/Reality-Capture/files/GUID-AF55A2EB-FCE8-4982-B3D6-CEAD5732DF03-htm.html). As a summary, for registering unstructured scans (photogrammetry, handheld, or mobile) which HoloLens is part of, we should combine them with the structured scan files to get them registered then by removing structured data, finally we have integrated unstructured 3D point cloud of HoloLens.
5. In Recap, we assigned one of the model’s corner as our origin point (0,0) to be used for referencing in global scale.
6. For generating submaps, we used Open3D which is a python library forprocessing 3D data. (refer to number 13, Generating Submaps folder in ourgithub repository)
7. In Open3D, we assign a region of 1m X 1m for randomly selecting a starting point in normal distribution for generating submaps for each run and each subset.(refer to number 13, Generating Submaps folder in our github repository)
8. For generating submaps, we used Open3D which is a python library for processing 3D data.
9. Laser scanner 3D point cloud map was used for training subsets in which the interval between submaps were set to 1 meter for both submap sizes 3 and 6 meters. HoloLens2 3D point cloud map used for testing in whichninterval were set to 3 and 6 meters for submap sizes 3mX3m and 6mX6m respectively in order to generate disjoint submaps without overlapping areas in each testing subset. (refer to number 13, Generating Submaps folder inour github repository)
10. After generating submaps, they have to be pre-processed to be entered into deep network. Therefore, by using MATLAB point cloud downsampling function we can downsample each point cloud to 4096 points. Then each of them are normalized with zero mean and new (x,y,z) values between -1 and 1. Also new labels based on the new axes values are calculated and assignedto each submaps. (refer to number 13, Submap pre-processing folder in our github repository)
11. Next, we made our training tuples consist of an anchor point, positives points, and negative points by using k-nearest neighbors for every submaps, at the same time we split the submaps into training and testing references by defining random regions of 6mX6m and saved them in pickle files.(refer to number 13, Generating Tuples/generate_training_tuples_baseline.py file in our github repository)
12. Then we trained the baseline deep model by loading the laser scanner tuples in 10 epochs in which those testing regions used for evaluation loss calculation in every 200 batches. (refer to number 13, Main.py file in our github repository) 
13. Then we generated the testing tuples for evaluating the trained model (step 11). In this step, all the ground truths of queries are extracted from the whole testset except the subset that includes the targeted query in each iteration to avoid self-matching. This has been done by K-nearest neighbors and we set 1-meter as our positive range (k).  (refer to number 13,Generating Tuples/generate_testsets.py file in our github repository)
14. Finally, we evaluated the trained model (step 11) with the HoloLens disjoint queries testsets to see how good the trained model localize the queries that come from a different device with different way of collecting data which is the mesh collection by a user walked through the indoor space.  The mesh data has to be converted to a 3D point cloud data with Open3D library.  In this step, the top global descriptor vectors which are the model outcomes, will be checked with the ground truths we calculated in the previous step to see how many of the top results exist in the ground truths of the query.(refer to number 13, evaluate.py file in our github repository) 
