from setuptools import setup, find_packages

setup(
    name='BDC',
    version='',
    packages=find_packages(),
    url='',
    license='',
    author='R-L-solutions',
    author_email='',
    description='',
    install_requires=[
        'pandas==1.1.2',
        'numpy==1.19.3'
    ],
    entry_points={
        'console_scripts': [
            'prepare_data=src.data.make_dataset:main'
        ]
    }
)
