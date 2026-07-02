from setuptools import find_packages, setup

package_name = 'acknowledgement_pkg'

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
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'behavior_test_node=acknowledgement_pkg.behavior_testing:main',
            'auto_move=acknowledgement_pkg.auto_movement_test:main',
            'dodge_node=acknowledgement_pkg.dodge:main',
            'dodge_node_MLS=acknowledgement_pkg.dodgeMLS:main',
            'slow_node=acknowledgement_pkg.slow:main',
            'slow_node_MLS=acknowledgement_pkg.slowMLS:main',
            'stop_node=acknowledgement_pkg.stop_movement:main',
            'run_away_node=acknowledgement_pkg.run_away:main',
            'wave_node=acknowledgement_pkg.wave:main',
            'wave_node_MLS=acknowledgement_pkg.waveMLS:main',
            'avoid_node=acknowledgement_pkg.avoid:main',
            'lia_sound_node=acknowledgement_pkg.lia_sound:main',
            'plain_node=acknowledgement_pkg.plain:main',
        ],
    },
)


