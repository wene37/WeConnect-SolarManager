from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="WeConnect-SolarManager",
    version="0.3.0rc4",
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
        ('SolarManager', ['src/init.py', 'src/main.py', 'src/app.py', 'src/Helper.py', 'src/config.txt']),
        ('SolarManager/logs', ['src/logs/.gitkeep']),
        ('SolarManager/static', ['src/static/axios.min.js', 'src/static/default.css', 'src/static/jquery-3.6.4.js', 'src/static/jquery-3.6.4.min.js', 'src/static/manifest.json', 'src/static/pushNotification.js', 'src/static/serviceWorker.js']),
        ('SolarManager/static/images/favicon', ['src/static/images/favicon/icon-16.png', 'src/static/images/favicon/icon-32.png', 'src/static/images/favicon/icon-57.png', 'src/static/images/favicon/icon-60.png', 'src/static/images/favicon/icon-64.png', 'src/static/images/favicon/icon-72.png', 'src/static/images/favicon/icon-76.png', 'src/static/images/favicon/icon-96.png', 'src/static/images/favicon/icon-114.png', 'src/static/images/favicon/icon-120.png', 'src/static/images/favicon/icon-144.png', 'src/static/images/favicon/icon-152.png', 'src/static/images/favicon/icon-180.png', 'src/static/images/favicon/icon-192.png', 'src/static/images/favicon/icon-512.png']),
        ('SolarManager/templates', ['src/templates/index.html'])
    ],
    python_requires=">=3.7, <4",
    install_requires=[
        'requests >= 2.27.1',
        'weconnect[Images] >= 0.55.0',
        'flask >= 2.3.1',
        'cryptography==3.3.2',
        'pywebpush >= 1.14.0'
    ],
    project_urls={
        "Bug Reports": "https://github.com/wene37/WeConnect-SolarManager/issues",
        "Source": "https://github.com/wene37/WeConnect-SolarManager"
    }
)