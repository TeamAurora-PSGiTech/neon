from setuptools import find_packages, setup

package_name = 'joystick_teleop'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
    ('share/ament_index/resource_index/packages',
        ['resource/joystick_teleop']),
    ('share/joystick_teleop', ['package.xml']),
    ('share/joystick_teleop/launch', ['launch/joystick_teleop.launch.py']),
],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='dharshan',
    maintainer_email='dharshanboopathy22@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
    'console_scripts': [
        'joy_twist = joystick_teleop.joy_twist:main',
    ],
},

)
