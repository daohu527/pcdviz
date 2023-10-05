
## animation
move.py - Set the point cloud to move according to the set curve
play.py - Set frame-by-frame play

## geometries
Types in the data directory are just wrappers for the open3d geometry classes. To put it simply, they inherit the types in open3d and just reconstruct the format conversion part.

There are types that are not implemented in open3d, we will implement this part ourselves. They inherit from `BaseObj` class.

In this way we can provide a simpler data reading interface and retain the methods in open3d. 

#### Types
arrow.py - 
box.py - open3d.geometry.OrientedBoundingBox
label.py - 
pointcloud.py - open3d.geometry.PointCloud

#### dataset

ml3d already implemented the dataset and visualization, so we will improve by this.

The implementation of the dataset class refers to pytorch, which simply means reading data from the dataset.

They are of two types:
- Map. Map type reads data from it, no order 
- Iter. In order

#### Statistics
In addition, we will add a data statistics interface to the data set to facilitate our understanding of the data. You can refer to YOLOV8’s chart for this part.

## filter
Filters are used to filter rules and display them. Of course, you can also save the filtered data. You can use it as a data preprocessing tool.

1. read from dataset
2. filter data
3. save or pass through

## proj
The proj module is mainly used for projecting perspective, I guess this is easily achieved by transforming the matrix.

- bev.py - point cloud projected onto bev
- img.py - point cloud projected by transformation matrix
- range_img.py - point cloud projected to front view

## config
input must be geometry

## example
1. frame_visualize_callback.yaml
first call calib callback and then oriented_bounding_box callback

calib callback interface
```
input: calib.path
output: {} 
```

oriented_bounding_box callback interface
```
input: path, calib.callback.output
output: bboxes
```
