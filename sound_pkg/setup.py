from setuptools import find_packages, setup

package_name = 'sound_pkg'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='nguyena',
    maintainer_email='alexhuyngu@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [ 'beep_node = sound_pkg.sound_test:main',
                            'battery_alarm_node = sound_pkg.battery_alarm:main',
                            'detection_chime_node = sound_pkg.detection_chime:main',
        ],
    },
)
