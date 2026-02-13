import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'g1_slam'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        # ament index resource (must exist as a file: resource/g1_slam)
        ('share/ament_index/resource_index/packages',
         ['resource/' + package_name]),

        # package manifest
        ('share/' + package_name, ['package.xml']),

        # launch files (*.launch.py)
        (os.path.join('share', package_name, 'launch'),
         glob(os.path.join('launch', '*.launch.py'))),

        # config files (*.yaml)
        (os.path.join('share', package_name, 'config'),
         glob(os.path.join('config', '*.yaml'))),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='mendes',
    maintainer_email='vitormendesrb@gmail.com',
    description='Bringup package for SLAM and localization on the Unitree G1 using Livox LiDAR',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [],
    },
)