from setuptools import setup, find_packages

setup(
    name='rondo',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'flask', 'requests', 'python-string-utils',
	'numpy', 'dateutil'
    ],
)
