from setuptools import find_packages, setup

package_name = 'user'

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
            'control = user.control:main',
            's_mo = user.s_mo:main',
            's_mls = user.s_mls:main',
            'd_mo = user.d_mo:main',
            'd_mls = user.d_mls:main',
            'w_mo = user.w_mo:main',
            'w_mls = user.w_mls:main',
        ],
    },
)
