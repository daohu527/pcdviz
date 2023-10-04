# pcdviz
point cloud viz

## Quick start
1. Display one frame of data. You need to specify the point cloud path `lidar_file` and the ground truth `label_file`
```
pcdviz --lidar_file=data/kitti/velodyne/training/000003.bin --label_file=data/kitti/label_2/training/000003.txt --calib_file=data/kitti/calib/training/000003.txt
```


## plan
1. complete point cloud viz (1days)
2. complete bounding-box viz (1days)
3. complete KITTI dataset (3days)
4. complete button play KITTI, forward and backward, skip

pybind11

dataset
- Customize the frame order, which is useful when checking data quality
- Automatically filter based on conditions, for example, only display frames where the number of pedestrians is greater than 3

filter\statistics\proj
