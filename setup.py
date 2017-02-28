import setuptools

setuptools.setup(
    name='openpr',
    version='1.1.0',
    url='https://github.com/yoichi/openpr',
    author='Yoichi Nakayama',
    author_email='yoichi.nakayama@gmail.com',
    description='Find pull request from given commit hash and open it in a Web browser.',
    license='BSD',
    packages=setuptools.find_packages(),
    entry_points={
        'console_scripts': [
            'openpr = openpr:main',
        ],
    },
    test_suite='test_openpr'
)
