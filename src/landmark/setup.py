from setuptools import find_packages, setup

package_name = 'landmark'

setup(
    name=package_name,
    version='0.0.1',
    packages=find_packages(exclude=['test']),
    data_files=[
        # Package index
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),

        # Package manifest
        ('share/' + package_name, ['package.xml']),

        # Launch files
        ('share/' + package_name + '/launch',
            ['landmark/realworld_landmarks.launch.py']),

        # Config files
        ('share/' + package_name + '/config',
            ['config/landmarks.yaml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='vimalanandham',
    maintainer_email='vimalanandham@todo.todo',
    description='Real-world landmark recording and visualization using Nav2 + RTAB-Map',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'landmark_recorder = landmark.landmark_recorder:main',
            'marker_publisher = landmark.marker_publisher:main',
        ],
    },
)

