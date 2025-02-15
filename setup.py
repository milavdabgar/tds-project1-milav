from setuptools import setup, find_packages

setup(
    name="tds-project1",
    version="0.1",
    packages=find_packages(),
    py_modules=["datagen"],
    install_requires=[
        "faker",
        "pillow",
    ],
)
