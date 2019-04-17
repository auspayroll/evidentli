from setuptools import setup

setup(
    name='rondo',
    packages=['rondo'],
    include_package_data=True,
    install_requires=[
        'flask', 'requests', 'unittest', 'python-string-utils',
	'numpy'
    ],
)
