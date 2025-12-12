"""
Perf Engine 插件配置管理
参考 api-engine 实现
"""
import sys
from pathlib import Path
import yaml


class PluginConfig:
    """插件配置单例类"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._config = None
            cls._instance._parsed_args = {}
        return cls._instance
    
    def load_config(self):
        """加载 plugin.yaml 配置"""
        if self._config is not None:
            return
        project_root = Path(__file__).parent.parent
        config_file = project_root / "plugin.yaml"
        if not config_file.exists():
            self._config = {}
            return
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                self._config = yaml.safe_load(f) or {}
        except Exception as e:
            print(f"加载 plugin.yaml 失败: {e}")
            self._config = {}
    
    @property
    def name(self):
        self.load_config()
        return self._config.get("name", "perf-engine")
    
    @property
    def version(self):
        self.load_config()
        return self._config.get("version", "1.0.0")
    
    @property
    def description(self):
        self.load_config()
        return self._config.get("description", "")
    
    @property
    def command(self):
        self.load_config()
        return self._config.get("command", "perf-engine")
    
    @property
    def params(self):
        self.load_config()
        return self._config.get("params", [])
    
    def parse_args(self):
        """解析命令行参数"""
        if self._parsed_args:
            return self._parsed_args
        
        args = {}
        consumed = []
        
        for param in self.params:
            param_name = param.get("name", "")
            cli_name = "--" + param_name.replace("_", "-")
            default = param.get("default")
            param_type = param.get("type", "string")
            value = default
            
            for i, arg in enumerate(sys.argv):
                if arg.startswith(cli_name + "="):
                    value = arg.split("=", 1)[1]
                    consumed.append(arg)
                    break
                elif arg == cli_name and i + 1 < len(sys.argv):
                    value = sys.argv[i + 1]
                    consumed.append(arg)
                    consumed.append(sys.argv[i + 1])
                    break
            
            # 类型转换
            if value is not None:
                if param_type == "boolean":
                    if isinstance(value, str):
                        value = value.lower() in ("true", "1", "yes")
                elif param_type == "number":
                    try:
                        value = int(value) if '.' not in str(value) else float(value)
                    except (ValueError, TypeError):
                        pass
            
            args[param_name] = value
        
        # 从 sys.argv 中移除已消费的参数
        for arg in consumed:
            if arg in sys.argv:
                sys.argv.remove(arg)
        
        self._parsed_args = args
        return args
    
    def get_arg(self, name, default=None):
        """获取指定参数值"""
        if not self._parsed_args:
            self.parse_args()
        return self._parsed_args.get(name, default)
    
    def print_help(self):
        """打印帮助信息"""
        print(f"\n{self.name} v{self.version}")
        print(f"{self.description}\n")
        print(f"用法: {self.command} [选项]\n")
        print("选项:")
        for param in self.params:
            name = param.get("name", "")
            cli = "--" + name.replace("_", "-")
            label = param.get("label", name)
            help_text = param.get("help", "")
            default = param.get("default", "")
            print(f"  {cli:<20} {label}")
            if help_text:
                default_str = f" (默认: {default})" if default != "" else ""
                print(f"                       {help_text}{default_str}")
        print()


# 全局单例
plugin_config = PluginConfig()
