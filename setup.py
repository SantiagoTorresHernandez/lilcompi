from setuptools import setup, find_packages

setup(
    name="patito",
    version="0.1.0",
    packages=find_packages(),
    package_data={
        "patito": ["*.lark"],
    },
    install_requires=[
        "lark",
    ],
    python_requires=">=3.7",
)

