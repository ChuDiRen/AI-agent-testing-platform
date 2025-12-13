import setuptools
"""
打包成一个 可执行模块
"""
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="api-engine",
    version="1.0.0",
    author="ChuDiRen",
    author_email="",
    description="API 自动化测试引擎 - 基于关键字驱动和数据驱动的 API 测试框架",
    license="MIT",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ChuDiRen/AI-agent-testing-platform",
    project_urls={
        "Bug Tracker": "https://github.com/ChuDiRen/AI-agent-testing-platform/issues",
        "Source Code": "https://github.com/ChuDiRen/AI-agent-testing-platform",
    },

    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Testing",
        "Framework :: Pytest",
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

    python_requires=">=3.8",
    # 生成一个可执行文件
    entry_points={
        'console_scripts': [
            'apirun=apirun.cli:run'
        ]
    },
    zip_safe=False
)