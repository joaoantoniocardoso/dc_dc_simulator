from setuptools import find_packages, setup

setup(
    name="power_electronics_state_model",
    packages=find_packages(
        include=[
            "State_model",
        ]
    ),
    version="0.0.1",
    description="",
    author="",
    license="",
    install_requires=[
        "numpy==1.19.5",
        "sympy==1.9",
    ],
    # setup_requires=['pytest-runner'],
    # tests_require=['pytest==4.4.1'],
    # test_suite='tests',
)
