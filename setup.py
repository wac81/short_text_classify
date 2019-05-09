import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="stclassify",
    version="0.1.0.4",
    author="wac",
    author_email="wuanch@gmail.com",
    description="short_text_classify",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/wac81/short_text_classify",
    packages=setuptools.find_packages(),
    install_requires=['jieba', 'numpy'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],

)