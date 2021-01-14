#!/usr/bin/env python3
"""
Author : Travis Simmons <920117874@student.ccga.edu>
Date   : 1/14/2021
Purpose: Finding the bounding volume of a cropped out plant PCD
"""

import argparse
import os
import sys
import copy
import os.path
import numpy as np
import open3d as o3d
import statistics as stats
from sklearn.cluster import KMeans



# --------------------------------------------------
def get_args():
    """Get command-line arguments"""

    parser = argparse.ArgumentParser(
        description='Rock the Casbah',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('Cropped Plant PCD',
                        metavar='cropped_plant',
                        help='Path to cropped plant PCD')

    parser.add_argument('-o',
                        '--outdir',
                        help='Output directory for isolated plant PCD',
                        metavar='outdir',
                        type=str,
                        default= 'isolated_plant_outputs')
    
    parser.add_argument('-f',
                        '--filename',
                        help='Output filename for isolated plant PCD',
                        metavar='filename',
                        type=str,
                        default='isolated_plant.ply')

    return parser.parse_args()


# --------------------------------------------------
def main():

    """Make a jazz noise here"""

    args = get_args()

    if not os.path.isdir(args.outdir):
        os.makedirs(args.outdir)


    # Load in point cloud
    plant = args.cropped_plant

    # Output
    plant_points = []

    # Read .ply file
    pcd_whole = o3d.io.read_point_cloud(plant)
    ar_whole_plant = np.asarray(pcd_whole.points)

    # Find middle z
    z_axis = []

    for i in ar_whole_plant:
        z_axis.append(i[2])

    median_z = stats.median(z_axis)


    # Slicing

    slice_storage_list = []

    a = ar_whole_plant[0][0]
    cnt = 1

    # Create one slice
    for i in ar_whole_plant:
        
        
        if (abs(i[0] - a) < 10) | (len(slice_storage_list) < 1):
            slice_storage_list.append(list(i))
            a = i[0]


        # Cluster the slice, and add clusters that have  a point above the overall
        # z to a 'plant list'
        else:
            # Drop y to flatten here
            flat_slice = copy.deepcopy(slice_storage_list)
            for j in flat_slice:
                del j[1]
            # Cluster here
            km = KMeans(
                n_clusters=5, init='random',
                n_init=10, max_iter=300, 
                tol=1e-04, random_state=0
            )
            
            X = np.array(flat_slice)
            y_km = km.fit_predict(X)

            # Choose cluster
            l0 = []
            l1 = []
            l2 = []
            l3 = []
            l4 = []
            for index, row in enumerate(slice_storage_list):
                # print(index, y_km[index], row)


                if y_km[index] == 0:
                    l0.append(row)
                if y_km[index] == 1:
                    l1.append(row)
                if y_km[index] == 2:
                    l2.append(row)
                if y_km[index] == 3:
                    l3.append(row)
                if y_km[index] == 4:
                    l4.append(row)

            clusters = [l0,l1,l2,l3,l4]

            

            for c in clusters:
                counter = 0
                for i in c:
                    # print(i)
                    # Below worked ok

                    # Tweak these two to get different outputs
                    # best so far is is .01 and 20

                    if i[2] > median_z + (median_z * .01):
                    # if i[2] > median_z:
                        counter += 1
                    
                    if counter >= (len(c)*.2):
                        plant_points.extend(c)
                        break



            slice_storage_list = []

            a = i[0]
            print(len(plant_points))
            # print(f'Slice {cnt} done')
            cnt+=1

    # Output plant pcd
    pcd_slice = o3d.geometry.PointCloud()
    pcd_slice.points = o3d.utility.Vector3dVector(plant_points)
    o3d.io.write_point_cloud(os.path.join(args.outdir, args.filename), pcd_slice)
        

# --------------------------------------------------
if __name__ == '__main__':
    main()