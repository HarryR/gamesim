import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pampy",
    version='0.0.2',
    author="Harry Roberts",
    author_email="HarryR@users.noreply.github.com",
    description="Stochastic and Deterministic simulation of state machine interaction",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/HarryR/gamesim",
    packages=setuptools.find_packages(),
    platforms='any',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6'
)