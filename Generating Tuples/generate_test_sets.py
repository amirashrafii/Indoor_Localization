import pandas as pd
import numpy as np
import os
import pandas as pd
from sklearn.neighbors import KDTree
import pickle
import random

#####For training and test data split#####
x_width = 6
y_width = 6

# For Laser
# p1 = [23, 51]
# p2 = [20, 17]
# p3 = [8, 45]
# p4 = [12, 30]



# p_dict = {"linklab": [p1, p2, p3, p4], "Holo": [p1, p2, p3, p4]}


def check_in_test_set(northing, easting, points, x_width, y_width):
    in_test_set = False
    for point in points:
        if (point[0] - x_width < northing and northing < point[0] + x_width and point[
            1] - y_width < easting and easting < point[1] + y_width):
            in_test_set = True
            break
    return in_test_set


##########################################

def output_to_file(output, filename):
    with open(filename, 'wb') as handle:
        pickle.dump(output, handle, protocol=pickle.HIGHEST_PROTOCOL)
    print("Done ", filename)


def construct_query_and_database_sets(base_path, runs_folder, folders, pointcloud_fols, filename, p, output_name):
    database_trees = []
    test_trees = []
    for folder in folders:
        print(folder)
        df_database = pd.DataFrame(columns=['file', 'x', 'y'])
        df_test = pd.DataFrame(columns=['file', 'x', 'y'])

        df_locations = pd.read_csv(os.path.join(base_path, runs_folder, folder, filename), sep=',')
        # df_locations['timestamp']=runs_folder+folder+pointcloud_fols+df_locations['timestamp'].astype(str)+'.bin'
        # df_locations=df_locations.rename(columns={'timestamp':'file'})
        for index, row in df_locations.iterrows():
            # entire business district is in the test set
            if (output_name == "Holo_testset"):
                df_test = df_test.append(row, ignore_index=True)
            elif (check_in_test_set(row['x'], row['y'], p, x_width, y_width)):
                df_test = df_test.append(row, ignore_index=True)
            df_database = df_database.append(row, ignore_index=True)

        database_tree = KDTree(df_database[['x', 'y']])
        test_tree = KDTree(df_test[['x', 'y']])
        database_trees.append(database_tree)
        test_trees.append(test_tree)

    test_sets = []
    database_sets = []
    for folder in folders:
        database = {}
        test = {}
        df_locations = pd.read_csv(os.path.join(base_path, runs_folder, folder, filename), sep=',')
        df_locations['number'] = runs_folder + folder + pointcloud_fols + df_locations['number'].astype(
            str) + '.bin'
        df_locations = df_locations.rename(columns={'number': 'file'})
        for index, row in df_locations.iterrows():
            # entire business district is in the test set
            if (output_name == "Holo_testset"):
                test[len(test.keys())] = {'query': row['file'], 'x': row['x'], 'y': row['y']}
            elif (check_in_test_set(row['x'], row['y'], p, x_width, y_width)):
                test[len(test.keys())] = {'query': row['file'], 'x': row['x'], 'y': row['y']}
            database[len(database.keys())] = {'query': row['file'], 'x': row['x'],
                                              'y': row['y']}
        database_sets.append(database)
        test_sets.append(test)

    for i in range(len(database_sets)):
        tree = database_trees[i]
        for j in range(len(test_sets)):
            if (i == j):
                continue
            for key in range(len(test_sets[j].keys())):
                coor = np.array([[test_sets[j][key]["x"], test_sets[j][key]["y"]]])
                index = tree.query_radius(coor, r=1)
                # indices of the positive matches in database i of each query (key) in test set j
                test_sets[j][key][i] = index[0].tolist()

    print("database_sets length : "+ str(len(database_sets)))
    print("test_sets length : " + str(len(test_sets)))

    output_to_file(database_sets, 'E:/Link Lab Data/Model/'+ output_name + '_evaluation_database.pickle')
    output_to_file(test_sets, 'E:/Link Lab Data/Model/' + output_name + '_evaluation_query.pickle')


###Building database and query files for evaluation
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
base_path = "E:/Link Lab Data/"

# For Laser
folders = []
runs_folder = "Testset/"
all_folders = sorted(os.listdir(os.path.join(base_path, runs_folder)))
index_list = range(len(all_folders))
print(all_folders)
# # print(len(index_list))
for index in index_list:
    folders.append(all_folders[index])

print(folders)
construct_query_and_database_sets(base_path, runs_folder, folders, "/bin_submaps_6m/", "Origin_Centroids.csv",
                                   p_dict["linklab"], "linklab")

# For Holo
folders = []
runs_folder = "Testset_Holo/"
all_folders = sorted(os.listdir(os.path.join(base_path, runs_folder)))
uni_index = range(len(all_folders))
for index in uni_index:
    folders.append(all_folders[index])

print(folders)
construct_query_and_database_sets(base_path, runs_folder, folders, "/bin_submaps_6m/", "Origin_Centroids.csv",
                                  p_dict["Holo"], "Holo_testset")
