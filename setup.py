from setuptools import setup, find_packages

setup(
    name='ullr-data-cli',
    version='1.0.3',
    author='jshlydnzl',
    author_email='jshlydnzl@users.noreply.github.com',
    description='A purely native Practice Engine for aspiring Data Analysts to generate and audit datasets',
    long_description='Ullr is a pure Python Data Engine that automatically audits CSV/Excel files for data quality (ghost data, invisible spaces, duplicates) and generates Dynamic Dashboard Blueprints for Excel, Power BI, Tableau, and Looker Studio.',
    long_description_content_type='text/markdown',
    url='https://github.com/jshlydnzl/ullr-data-cli',
    packages=find_packages(),
    install_requires=[
        'rich',
        'pandas',
        'openpyxl',
        'faker'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Topic :: Scientific/Engineering :: Information Analysis',
    ],
    python_requires='>=3.7',
    entry_points={
        'console_scripts': [
            'ullr=ullr.main:cli',
        ],
    },
)
