import numpy as np
import csv
import open3d as o3d
import os


CUBOID_EXTENT_METERS = 3

METERS_BELOW_START = 2.2
METERS_ABOVE_START = 3.8

def main():
    CSV_file = "centroids"
    CSV_counter = 1
    submap_num = 1
    folder_num = 1

    n = 20
    xy_min = [-0.234, 58.322]
    xy_max = [0.766, 59.322]

    sampl = np.random.uniform(low=xy_min, high=xy_max, size=(n,2))

    pcd = o3d.io.read_point_cloud(r"F:\aashr\Documents\RecapRegisteredPC_v2.pts")
    for i in range(len(sampl)):

        os.makedirs("E:/Link Lab Data/with floor and cieling/6X6/Trainset/" + str(folder_num) + "/submaps_6m_1m")
        with open("E:/Link Lab Data/with floor and cieling/6X6/Trainset/"+ str(folder_num)+'/PC_locations_6m_1m.csv', 'w', newline='') as csvfile:

        ## Start point here corresponds to an ego vehicle position start in a point cloud
            start_position = {'x': sampl[i][0], 'y': sampl[i][1] , 'z': 1.7}
            x_value = start_position['x']
            y_value = start_position['y']

            for y in np.arange(start_position['y'], -0.436-0.8, -1):
                start_position['y'] = y
                start_position['x'] = x_value
                for x in np.arange(start_position['x'], 30.176+0.8, 1):
                    start_position['x'] = x

                    cuboid_points = getCuboidPoints(start_position)
                    points = o3d.utility.Vector3dVector(cuboid_points)
                    oriented_bounding_box = o3d.geometry.AxisAlignedBoundingBox.create_from_points(points)
                    point_cloud_crop = pcd.crop(oriented_bounding_box)
                    print(point_cloud_crop)

                    # o3d.visualization.draw_geometries([pcd, oriented_bounding_box])
                    # o3d.visualization.draw_geometries([point_cloud_crop, oriented_bounding_box])
                    o3d.io.write_point_cloud("E:/Link Lab Data/with floor and cieling/6X6/Trainset/"+ str(folder_num)+"/submaps_6m_1m"+"/"+str(submap_num)+".pcd", point_cloud_crop)

                    CSVwriter = csv.writer(csvfile, delimiter=',',
                                           quotechar='|', quoting=csv.QUOTE_MINIMAL)
                    CSVwriter.writerow([str(submap_num)] + [start_position['x']] + [start_position['y']] + [1.7])

                    with open("E:/Link Lab Data/with floor and cieling/6X6/Trainset/"+CSV_file+'.csv', 'a', newline='') as csvfile_cetroids:
                        CSVwriter_c = csv.writer(csvfile_cetroids, delimiter=',',
                                                 quotechar='|', quoting=csv.QUOTE_MINIMAL)
                        CSVwriter_c.writerow([str(submap_num)] + [start_position['x']] + [start_position['y']] + [1.7])
                    submap_num = submap_num + 1
        CSV_counter = CSV_counter + 1
        folder_num = folder_num + 1



def getCuboidPoints(start_position):
  return np.array([
    # Vertices Polygon1
    [start_position['x'] + (CUBOID_EXTENT_METERS), start_position['y'] + (CUBOID_EXTENT_METERS), start_position['z'] + METERS_ABOVE_START], # face-topright
    [start_position['x'] - (CUBOID_EXTENT_METERS), start_position['y'] + (CUBOID_EXTENT_METERS), start_position['z'] + METERS_ABOVE_START], # face-topleft
    [start_position['x'] - (CUBOID_EXTENT_METERS), start_position['y'] - (CUBOID_EXTENT_METERS), start_position['z'] + METERS_ABOVE_START], # rear-topleft
    [start_position['x'] + (CUBOID_EXTENT_METERS), start_position['y'] - (CUBOID_EXTENT_METERS), start_position['z'] + METERS_ABOVE_START], # rear-topright

    # Vertices Polygon 2
    [start_position['x'] + (CUBOID_EXTENT_METERS), start_position['y'] + (CUBOID_EXTENT_METERS), start_position['z'] - METERS_BELOW_START],
    [start_position['x'] - (CUBOID_EXTENT_METERS), start_position['y'] + (CUBOID_EXTENT_METERS), start_position['z'] - METERS_BELOW_START],
    [start_position['x'] - (CUBOID_EXTENT_METERS), start_position['y'] - (CUBOID_EXTENT_METERS), start_position['z'] - METERS_BELOW_START],
    [start_position['x'] + (CUBOID_EXTENT_METERS), start_position['y'] - (CUBOID_EXTENT_METERS), start_position['z'] - METERS_BELOW_START],
  ]).astype("float64")

if __name__ == '__main__':
  main()