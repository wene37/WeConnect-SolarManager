# Always prefer setuptools over distutils
from setuptools import setup, find_packages
from setuptools.command.install import install
import pathlib

here = pathlib.Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="WeConnect-SolarManager",
    version="0.2.2",
    description="With WeConnect-SolarManager you can automatically charge your Volkswagen ID car (e.g. ID.4) with solar electricity, even if your wallbox does not support this.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/wene37/WeConnect-SolarManager",
    author="Thomas Werner",
    classifiers=[
        "License :: OSI Approved :: MIT License"
    ],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    data_files=[
        ('SolarManager', ['src/init.py', 'src/main.py', 'src/config.txt']),
        ('SolarManager/logs', ['src/logs/.gitkeep'])
    ],
    python_requires=">=3.7, <4",
    install_requires=[
        'requests >= 2.27.1',
        'weconnect[Images] >= 0.54.2',
        'flask >= 2.3.1'
    ],
    project_urls={
        "Bug Reports": "https://github.com/wene37/WeConnect-SolarManager/issues",
        "Source": "https://github.com/wene37/WeConnect-SolarManager"
    }
)