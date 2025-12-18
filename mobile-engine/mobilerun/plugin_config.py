import sys
from pathlib import Path

import yaml


class PluginConfig:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._config = None
            cls._instance._parsed_args = {}
        return cls._instance

    def load_config(self):
        if self._config is not None:
            return
        project_root = Path(__file__).parent.parent
        config_file = project_root / "plugin.yaml"
        if not config_file.exists():
            self._config = {}
            return
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                self._config = yaml.safe_load(f) or {}
        except Exception:
            self._config = {}

    @property
    def name(self):
        self.load_config()
        return self._config.get("name", "unknown")

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
        return self._config.get("command", "")

    @property
    def params(self):
        self.load_config()
        return self._config.get("params", [])

    def parse_args(self):
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
            for arg in sys.argv:
                if arg.startswith(cli_name + "="):
                    value = arg.split("=", 1)[1]
                    consumed.append(arg)
                    break
            if value is not None and param_type == "boolean" and isinstance(value, str):
                value = value.lower() in ("true", "1", "yes")
            args[param_name] = value
        for arg in consumed:
            if arg in sys.argv:
                sys.argv.remove(arg)
        self._parsed_args = args
        return args

    def get_arg(self, name, default=None):
        if not self._parsed_args:
            self.parse_args()
        return self._parsed_args.get(name, default)

    def print_help(self):
        print(f"\n{self.name} v{self.version}")
        print(f"{self.description}\n")
        print(f"用法: {self.command} [选项]\n")
        for param in self.params:
            name = param.get("name", "")
            cli = "--" + name.replace("_", "-")
            label = param.get("label", name)
            help_text = param.get("help", "")
            default = param.get("default", "")
            print(f"  {cli:<20} {label}")
            if help_text:
                print(
                    f"                       {help_text} (默认: {default})"
                    if default
                    else f"                       {help_text}"
                )


plugin_config = PluginConfig()
