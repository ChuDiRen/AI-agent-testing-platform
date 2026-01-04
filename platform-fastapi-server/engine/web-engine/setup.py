"""
Web Engine 安装配置
"""
from setuptools import setup, find_packages

with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="web-engine",
    version="1.0.0",
    description="Web 自动化测试引擎 - 基于 Playwright 的关键字驱动和数据驱动测试框架",
    author="ChuDiRen",
    author_email="",
    url="https://github.com/ChuDiRen/AI-agent-testing-platform",
    packages=find_packages(),
    install_requires=requirements,
    python_requires=">=3.9",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Testing",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    entry_points={
        "console_scripts": [
            "webrun=webrun.cli:run",
        ],
    },
    keywords="playwright web automation testing keyword-driven data-driven",
    project_urls={
        "Documentation": "https://github.com/ChuDiRen/AI-agent-testing-platform/wiki",
        "Source": "https://github.com/ChuDiRen/AI-agent-testing-platform",
        "Bug Tracker": "https://github.com/ChuDiRen/AI-agent-testing-platform/issues",
    },
)

