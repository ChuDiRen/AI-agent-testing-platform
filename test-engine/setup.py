"""
Test Engine 安装配置
统一的自动化测试引擎，支持 API 和 Web 测试
"""
from setuptools import setup, find_packages

with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="test-engine",
    version="1.0.0",
    description="统一的自动化测试引擎，支持 API 测试和 Web UI 测试，采用关键字驱动和数据驱动设计",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Test Engine Team",
    author_email="test@example.com",
    url="https://github.com/yourusername/test-engine",
    
    # 包含所有包
    packages=find_packages(),
    
    # 包含非 Python 文件
    include_package_data=True,
    package_data={
        'testengine_api': ['*.yaml', '*.ini'],
        'testengine_web': ['*.yaml', '*.ini'],
    },
    
    # 安装依赖
    install_requires=requirements,
    
    # Python 版本要求
    python_requires=">=3.9",
    
    # 分类信息
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Testing",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    
    # 命令行入口点
    entry_points={
        "console_scripts": [
            "testrun=testrun.cli:run",
        ],
    },
    
    keywords="automation testing api web selenium requests keyword-driven data-driven",
    
    project_urls={
        "Documentation": "https://github.com/yourusername/test-engine/wiki",
        "Source": "https://github.com/yourusername/test-engine",
        "Tracker": "https://github.com/yourusername/test-engine/issues",
    },
    
    zip_safe=False,
)

