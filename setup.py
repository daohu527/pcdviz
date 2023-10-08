import setuptools
from glob import glob

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pcdviz",
    version="0.0.3",
    author="daohu527",
    author_email="daohu527@gmail.com",
    description="point cloud viz",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/daohu527/pcdviz",
    project_urls={
        "Bug Tracker": "https://github.com/daohu527/pcdviz/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "."},
    data_files=[('pcdviz/config', glob('config/*yaml')),
                ('pcdviz/data/custom/label', 
                 glob('data/custom/label/*txt')),
                ('pcdviz/data/custom/prediction', 
                 glob('data/custom/prediction/*txt')),                 
                ('pcdviz/data/custom/velodyne', 
                 glob('data/custom/velodyne/*bin')),
                ('pcdviz/data/kitti/training/calib', 
                 glob('data/kitti/training/calib/*txt')),
                ('pcdviz/data/kitti/training/label_2', 
                 glob('data/kitti/training/label_2/*txt')),
                ('pcdviz/data/kitti/training/velodyne', 
                 glob('data/kitti/training/velodyne/*bin')),],
    packages=setuptools.find_packages(where="."),
    install_requires=[
        'open3d',
        # 'seaborn',
        'numpy',
        'pyyaml',
    ],
    entry_points={
        'console_scripts': [
            'pcdviz = pcdviz.main:main',
        ],
    },
    python_requires=">=3.6",
)
