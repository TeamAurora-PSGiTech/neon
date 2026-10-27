from setuptools import setup

package_name = 'panorama_clean'

setup(
    name=package_name,
    version='0.1.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='vimalanandham',
    maintainer_email='vimal@example.com',
    description='Clean panorama capture node',
    license='MIT',
    entry_points={
        'console_scripts': [
            'panorama_node=panorama_clean.panorama_node:main',
        ],
    },
)

