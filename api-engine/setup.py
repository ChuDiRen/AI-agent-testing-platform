import setuptools
"""
打包成一个 可执行模块
"""
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    # 关于项目的介绍 - 随便写都可以
    name="HuaceAPIRunner",
    version="0.0.1",
    author="hctestedu.com",
    author_email="zhangfeng0103@live.com",
    description="华测教育 API 自动化测试工具",
    license="GPLv3",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://www.hctestedu.com",
    project_urls={
        "Bug Tracker": "https://www.hctestedu.com",
        "Contact Us": "https://www.hctestedu.com",
    },

    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
    ],
    # 需要安装的依赖 -- 工具依赖
    install_requires=[
        "allure-pytest==2.13.5",
        "allure-combine>=1.0.11",
        "Jinja2",
        "jsonpath",
        "pluggy",
        "pycparser",
        "PyMySQL",
        "PySocks",
        "pytest",
        "PyYAML",
        "pyyaml-include==1.3.1",
        "requests",
        "selenium",
        "SQLAlchemy",
        "exceptiongroup"
    ],
    packages=setuptools.find_packages(),

    python_requires=">=3.6",
    # 生成一个 可执行文件 例如 windows下面 .exe
    entry_points={
        'console_scripts': [
            # 可执行文件的名称=执行的具体代码方法
            'huace-apirun=apirun.cli:run'
        ]
    },
    zip_safe=False
)