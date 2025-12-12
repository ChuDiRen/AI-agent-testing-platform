"""
Perf Engine 安装配置
基于 Locust 的性能测试引擎
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="perf-engine",
    version="1.0.0",
    author="ChuDiRen",
    author_email="",
    description="性能测试引擎 - 基于 Locust 的关键字驱动和数据驱动性能测试框架",
    license="MIT",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ChuDiRen/AI-agent-testing-platform",
    packages=find_packages(),
    install_requires=[
        "locust>=2.20.0",
        "PyYAML>=6.0",
        "jsonpath>=0.82",
        "gevent>=23.0.0",
        "Jinja2>=3.0.0",
    ],
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Testing",
        "Topic :: Software Development :: Testing :: Traffic Generation",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    entry_points={
        "console_scripts": [
            "perf-engine=perfrun.cli:run",
        ],
    },
    keywords="locust performance load testing keyword-driven data-driven stress",
    project_urls={
        "Documentation": "https://github.com/ChuDiRen/AI-agent-testing-platform/wiki",
        "Source": "https://github.com/ChuDiRen/AI-agent-testing-platform",
        "Bug Tracker": "https://github.com/ChuDiRen/AI-agent-testing-platform/issues",
    },
)
