import setuptools

with open('requirements.txt', "r") as f:
    requirements = f.read().splitlines()

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="usttc",
    version="0.0.5",
    author="Kuo Zhang",
    author_email="kuo.zh92@gmail.com",
    description="Unified Speech-to-text Client",
    download_url='https://github.com/kakakuoka/usttc/archive/refs/tags/v0.0.5.tar.gz',
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=requirements,
    packages=setuptools.find_packages(),
    include_package_data=True
)