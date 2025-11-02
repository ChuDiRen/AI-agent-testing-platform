"""
TestRun - 统一的测试引擎入口模块
"""

# 延迟导入避免RuntimeWarning
# 当直接运行 python -m testrun.cli 时，不会触发重复导入
__all__ = ['run']

def __getattr__(name):
    """延迟导入，避免模块重复导入警告"""
    if name == 'run':
        from .cli import run
        return run
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

