from setuptools import setup, find_packages


long_description = open('README.md').read()

setup(
    name='agent-py',
    version='0.0.1',
    license='Apache Software License',
    url='https://github.com/ispysoftware/agent-py',
    author='Sean Tearney',
    author_email='sean@ispyconnect.com',
    description='A python wrapper around the Agent REST API.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=list(val.strip() for val in open('requirements.txt')),
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
