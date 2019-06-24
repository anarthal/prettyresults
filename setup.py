import setuptools
import os

def get_web_package_data():
    paths = [os.path.join('web', '*')]
    project_root = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'prettyresults')
    for (path, directories, _) in os.walk(os.path.join(project_root, 'web')):
        relative = os.path.relpath(path, project_root)
        paths += [os.path.join(relative, d, '*') for d in directories]
    return paths

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="prettyresults",
    version="1.0.0",
    author="Anarthal",
    author_email="rubenperez038@gmail.com",
    description="Present data analysis results in Web or Docx format",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/anarthal/prettyresults",
    packages=setuptools.find_packages(),
    package_data={'': get_web_package_data()},
    include_package_data=True,
    install_requires=[
        'matplotlib>=2.1.1',
        'numpy>=1.13.3',
        'pandas>=0.24.1',
        'python-docx>=0.8.10',
        'scipy>=0.19.1',
        'Pillow>=5.1.0',
    ],
    classifiers=[
        "Programming Language :: Python :: 3 :: Only",
        "License :: OSI Approved :: MIT License",
        "Topic :: Scientific/Engineering",
    ],
)