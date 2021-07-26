import pandas as pd
import numpy as np
import os
from sklearn.neighbors import KDTree
import pickle
import random
import joblib

# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
base_path = "/home/aa9sz/Driver_in_the_loop/Amir/Indoor Localization/Link Lab Data/withF&C/6X6/"

runs_folder = "Trainset_bin/"
filename = "Origin_Centroids.csv"
pointcloud_fols = "/bin_submaps_6m_1m/"

all_folders = sorted(os.listdir(os.path.join(base_path, runs_folder)))
#all_folders.remove('.ipynb_checkpoints')

folders = []

# All runs are used for training 
index_list = range(len(all_folders))
print("Number of runs: " + str(len(index_list)))
for index in index_list:
    folders.append(all_folders[index])
print(folders)

#####For training and test data split#####
x_width = 6
y_width = 6


p1 = [23, 51]
p2 = [20, 17]
p3 = [8, 45]
p4 = [12, 30]

p = [p1, p2, p3, p4]


def check_in_test_set(northing, easting, points, x_width, y_width):
    in_test_set = False
    for point in points:
        if (point[0] - x_width < northing and northing < point[0] + x_width and point[
            1] - y_width < easting and easting < point[1] + y_width):
            in_test_set = True
            break
    return in_test_set


##########################################


def construct_query_dict(df_centroids, filename):
    tree = KDTree(df_centroids[['x', 'y']])
    ind_nn = tree.query_radius(df_centroids[['x', 'y']], r=6)
    #print("ind_nn:",ind_nn)
    ind_r = tree.query_radius(df_centroids[['x', 'y']], r=12)
    #print("ind_r:",ind_r)
    queries = {}
    for i in range(len(ind_nn)):
        query = df_centroids.iloc[i]["file"]
        #print("query:",query)
        positives = np.setdiff1d(ind_nn[i], [i]).tolist()
        #print("positives:",len(positives))
        negatives = np.setdiff1d(df_centroids.index.values.tolist(), ind_r[i]).tolist()
        #print("negatives len:",len(negatives))
        random.shuffle(negatives)
        queries[i] = {"query": query, "positives": positives, "negatives": negatives}

    with open(filename, 'wb') as handle:
        joblib.dump(queries, handle, protocol=pickle.HIGHEST_PROTOCOL)

    print("Done ", filename)


####Initialize pandas DataFrame
df_train = pd.DataFrame(columns=['file', 'x', 'y'])
df_test = pd.DataFrame(columns=['file', 'x', 'y'])

for folder in folders:
    df_locations = pd.read_csv(os.path.join(base_path, runs_folder, folder, filename), sep=',')
    df_locations['number'] = runs_folder + folder + pointcloud_fols + df_locations['number'].astype(str) + '.bin'
    df_locations = df_locations.rename(columns={'number': 'file'})

    for index, row in df_locations.iterrows():
        if (check_in_test_set(row['x'], row['y'], p, x_width, y_width)):
            df_test = df_test.append(row, ignore_index=True)
        else:
            df_train = df_train.append(row, ignore_index=True)

print("Number of training submaps: " + str(len(df_train['file'])))
print("Number of non-disjoint test submaps: " + str(len(df_test['file'])))
construct_query_dict(df_train, "/home/aa9sz/Driver_in_the_loop/Amir/Indoor Localization/Link Lab Data/Model/withF&C/training_queries_baseline_6-12.pickle")
construct_query_dict(df_test, "/home/aa9sz/Driver_in_the_loop/Amir/Indoor Localization/Link Lab Data/Model/withF&C/test_queries_baseline_6-12.pickle")