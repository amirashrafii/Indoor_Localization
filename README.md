# Indoor localization for an Augmented Reality-based assissting system


We provide a guideline in which it’s described what actions we took to buildour indoor localization model for the future reference step by step as following: 
1. We collected our 3D point cloud model with FARO Focus laser scanner
2. In the next step we registered the point cloud scan files with the AutodeskReCap software to have an integrated and accurate 3D model.
3. Then, we assigned one of the model’s corner as our origin point (0,0) to beused for referencing in global scale.
4. After that, we assign a region of 1m X 1m for randomly selecting a startingpoint in normal distribution for generating submaps for each run and eachsubset.
5. For  generating  submaps,  we  used  Open3D  which  is  a  python  library  forprocessing 3D data.
6. For training subsets, the interval between submaps were set to 1 meter, andfor testing the interval were set to 3 and 6 meters for submap sizes 3mX3mand 6mX6m respectively in order to generate disjoint submaps without over-lapping area in each testing subset.
7. After generating submaps, they have to be pre-processed to be entered intodeep  network. Therefore, By  using  MATLAB  point  cloud  downsampling functionwe can downsample each point cloud to 4096 points. Then each of themare normalized with zero mean and (x,y,z) values between -1 and 1 to be inthe same scale for deep learning.
8. Next, we made our tuples consist of an anchor point, positives points, andnegative points by using k-nearest neighbors for every submaps, at the sametime we split the submaps into training and testing references by definingrandom regions of 6mX6m and saved them in pickle files.
9. Then we trained the baseline deep model by loading the laser scanner tu-ples in 10 epochs in which those testing regions used for evaluation loss calculation 
10. Then we generated the tuples for the model evaluation. In this step, all theground truths of queries in the testing regions are extracted from the wholetestset except the subset that has the targeted query in each iteration. This has been done by K-nearest neighbors and we set 1-meter as our positiverange.
11. Finally, we  evaluated  the  trained  model  with  the  both  laser  scanner  andhololens testsets in which the assigned testing regions have been evaluatedas disjoint queries to the system to see how good the trained model answer tothe queries. In this step, the top global descriptor vectors (which belong toother subsets of testset except the query’s) will be checked with the groundtruths we calculated in the previous step to see how many of the top resultsare in the ground truths of the query. 
