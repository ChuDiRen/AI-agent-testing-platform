"""
Perf Pytest 配置文件
提供性能测试的共享 fixtures 和配置
"""
import os
import pytest


# ==================== 环境配置 ====================

# 默认目标主机
DEFAULT_HOST = os.getenv("PERF_HOST", "https://jsonplaceholder.typicode.com")

# 默认性能配置
DEFAULT_USERS = int(os.getenv("PERF_USERS", "10"))
DEFAULT_SPAWN_RATE = int(os.getenv("PERF_SPAWN_RATE", "2"))
DEFAULT_RUN_TIME = int(os.getenv("PERF_RUN_TIME", "30"))


# ==================== Fixtures ====================

@pytest.fixture(scope="session")
def perf_host():
    """目标主机"""
    return DEFAULT_HOST


@pytest.fixture(scope="session")
def perf_users():
    """并发用户数"""
    return DEFAULT_USERS


@pytest.fixture(scope="session")
def perf_spawn_rate():
    """用户生成速率"""
    return DEFAULT_SPAWN_RATE


@pytest.fixture(scope="session")
def perf_run_time():
    """运行时间(秒)"""
    return DEFAULT_RUN_TIME


@pytest.fixture(scope="session")
def perf_config():
    """完整的性能测试配置"""
    return {
        "host": DEFAULT_HOST,
        "users": DEFAULT_USERS,
        "spawn_rate": DEFAULT_SPAWN_RATE,
        "run_time": DEFAULT_RUN_TIME,
        "wait_time_min": 1.0,
        "wait_time_max": 3.0,
        # 性能阈值
        "max_failure_rate": 0.05,
        "max_avg_response_time": 1000,
        "max_p95_response_time": 1500
    }


# ==================== Pytest 配置 ====================

def pytest_configure(config):
    """Pytest 配置钩子"""
    # 注册自定义 markers
    config.addinivalue_line(
        "markers", "perf: 性能测试用例"
    )
    config.addinivalue_line(
        "markers", "stress: 压力测试用例"
    )
    config.addinivalue_line(
        "markers", "load: 负载测试用例"
    )


def pytest_collection_modifyitems(config, items):
    """修改测试用例收集"""
    for item in items:
        # 为所有 perf 目录下的测试添加 perf marker
        if "perf-cases_pytest" in str(item.fspath):
            item.add_marker(pytest.mark.perf)


# ==================== 报告钩子 ====================

@pytest.hookimpl(tryfirst=True)
def pytest_runtest_makereport(item, call):
    """生成测试报告时的钩子"""
    if call.when == "call":
        # 可以在这里添加额外的报告信息
        pass
