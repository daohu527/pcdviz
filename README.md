# pcdviz
point cloud viz

## Quick start
1. Display point cloud
```
pcdviz --pcd=data/kitti/velodyne/training/000003.bin
```

2. Display multi point cloud
```
pcdviz --cfg=config/multi_pointcloud.yaml
```

2. Display dataset
```
pcdviz --cfg=config/dataset_visualize.yaml
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
