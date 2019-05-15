import setuptools

import os

from setuptools.command.install import install

from setuptools import setup


with open('README.md') as f:
    LONG_DESCRIPTION = f.read()


class MakeCommand(install):
    def run(self):
        os.system('make')
        common_dir = 'stclassify/svc_impl'
        target_dir = '%s/%s' % (self.build_lib, common_dir)
        print(self.build_lib, target_dir)
        self.mkpath(target_dir)
        os.system('cp %s/util.so.1 %s' % (common_dir, target_dir))
        common_dir = common_dir + '/liblinear'
        target_dir = '%s/%s' % (self.build_lib, common_dir)
        self.mkpath(target_dir)
        os.system('cp %s/liblinear.so.1 %s' % (common_dir, target_dir))
        install.run(self)


setuptools.setup(
    name="stclassify",
    version="0.1.0.13",
    author="wac",
    author_email="wuanch@gmail.com",
    description="short_text_classify",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url="https://github.com/wac81/short_text_classify",
    # packages=setuptools.find_packages(),
    packages=['stclassify', 'stclassify.svc_impl', 'stclassify.svc_impl.liblinear.python'],

    install_requires=['jieba',
                      'numpy'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    cmdclass={'install': MakeCommand}

)