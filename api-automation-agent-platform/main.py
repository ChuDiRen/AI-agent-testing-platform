"""
API Automation Agent Platform - Main Application

This is the main entry point for the API Automation Agent Platform.
It provides a unified interface to start all services and components.
"""
import asyncio
import sys
import signal
from pathlib import Path
from typing import List, Optional
import argparse
import json
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.config import get_config, PlatformConfig, validate_environment, create_sample_env_file
from core.logging_config import setup_logging
from examples.complete_workflow_example import APITestAutomationPlatform


class PlatformManager:
    """Platform manager for orchestrating all services"""
    
    def __init__(self, config: PlatformConfig):
        self.config = config
        self.services: List[asyncio.Task] = []
        self.platform: Optional[APITestAutomationPlatform] = None
        self.running = False
        
    async def start(self):
        """Start all platform services"""
        print(f"🚀 Starting API Automation Agent Platform")
        print(f"📊 Environment: {self.config.environment.value}")
        print(f"🌐 Host: {self.config.host}:{self.config.port}")
        print(f"📅 Started at: {datetime.utcnow().isoformat()}")
        print("=" * 60)
        
        # Validate configuration
        if not validate_environment():
            print("❌ Configuration validation failed")
            return False
        
        # Setup logging
        setup_logging(self.config.logging)
        
        # Initialize platform
        self.platform = APITestAutomationPlatform()
        
        # Start MCP servers if enabled
        await self._start_mcp_servers()
        
        # Start main API server
        await self._start_api_server()
        
        self.running = True
        print("✅ Platform started successfully")
        
        return True
    
    async def stop(self):
        """Stop all platform services"""
        print("\n🛑 Stopping platform services...")
        
        self.running = False
        
        # Cancel all services
        for service in self.services:
            if not service.done():
                service.cancel()
                try:
                    await service
                except asyncio.CancelledError:
                    pass
        
        # Cleanup platform
        if self.platform:
            # Platform cleanup would go here
            pass
        
        print("✅ Platform stopped")
    
    async def _start_mcp_servers(self):
        """Start MCP servers if enabled"""
        mcp_config = self.config.get_mcp_servers_config()
        
        if mcp_config["rag_server"]["enabled"]:
            print("🔍 Starting RAG MCP Server...")
            # Start RAG server
            rag_task = asyncio.create_task(self._run_rag_server())
            self.services.append(rag_task)
        
        if mcp_config["chart_server"]["enabled"]:
            print("📈 Starting Chart MCP Server...")
            # Start Chart server
            chart_task = asyncio.create_task(self._run_chart_server())
            self.services.append(chart_task)
        
        if mcp_config["automation_server"]["enabled"]:
            print("🔧 Starting Automation-Quality MCP Server...")
            # Start Automation server
            automation_task = asyncio.create_task(self._run_automation_server())
            self.services.append(automation_task)
    
    async def _start_api_server(self):
        """Start main API server"""
        print("🌐 Starting Main API Server...")
        # Start API server
        api_task = asyncio.create_task(self._run_api_server())
        self.services.append(api_task)
    
    async def _run_rag_server(self):
        """Run RAG MCP server"""
        try:
            from mcp_servers.rag_server import main as rag_main
            await rag_main()
        except Exception as e:
            print(f"❌ RAG server error: {e}")
    
    async def _run_chart_server(self):
        """Run Chart MCP server"""
        try:
            from mcp_servers.chart_server import main as chart_main
            await chart_main()
        except Exception as e:
            print(f"❌ Chart server error: {e}")
    
    async def _run_automation_server(self):
        """Run Automation-Quality MCP server"""
        try:
            from mcp_servers.automation_quality import main as automation_main
            await automation_main()
        except Exception as e:
            print(f"❌ Automation server error: {e}")
    
    async def _run_api_server(self):
        """Run main API server"""
        try:
            # This would start the FastAPI server
            # For now, just keep it running
            while self.running:
                await asyncio.sleep(1)
        except Exception as e:
            print(f"❌ API server error: {e}")


async def run_interactive_mode(platform_manager: PlatformManager):
    """Run interactive mode"""
    print("\n🎮 Interactive Mode")
    print("=" * 40)
    
    while platform_manager.running:
        try:
            print("\nAvailable commands:")
            print("1. Run complete workflow")
            print("2. Test individual agent")
            print("3. Show platform status")
            print("4. Show configuration")
            print("5. Exit")
            
            choice = input("\nSelect option (1-5): ").strip()
            
            if choice == "1":
                await run_workflow_demo(platform_manager.platform)
            elif choice == "2":
                await test_individual_agents(platform_manager.platform)
            elif choice == "3":
                show_platform_status(platform_manager)
            elif choice == "4":
                show_configuration(platform_manager.config)
            elif choice == "5":
                break
            else:
                print("❌ Invalid choice")
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"❌ Error: {e}")


async def run_workflow_demo(platform: APITestAutomationPlatform):
    """Run workflow demonstration"""
    print("\n🎬 Running Workflow Demo")
    print("-" * 30)
    
    demo_requests = [
        "为用户登录API生成Playwright测试代码",
        "分析Swagger文档并生成完整测试套件",
        "为电商API创建功能和安全测试"
    ]
    
    print("Select demo request:")
    for i, request in enumerate(demo_requests, 1):
        print(f"{i}. {request}")
    
    try:
        choice = input("Select demo (1-3): ").strip()
        
        if choice.isdigit() and 1 <= int(choice) <= 3:
            request = demo_requests[int(choice) - 1]
            print(f"\n🎯 Executing: {request}")
            
            results = await platform.run_complete_workflow(request)
            
            print("\n📊 Results Summary:")
            print(f"Status: {results.get('status', 'unknown')}")
            print(f"Steps: {len(results.get('steps', []))}")
            
        else:
            print("❌ Invalid choice")
            
    except Exception as e:
        print(f"❌ Demo failed: {e}")


async def test_individual_agents(platform: APITestAutomationPlatform):
    """Test individual agents"""
    print("\n🧪 Test Individual Agents")
    print("-" * 30)
    
    agents = [
        ("RAG Retrieval Agent", platform.rag_agent),
        ("Planner Agent", platform.planner_agent),
        ("Generator Agent", platform.generator_agent),
        ("Executor Agent", platform.executor_agent),
        ("Analyzer Agent", platform.analyzer_agent)
    ]
    
    print("Available agents:")
    for i, (name, _) in enumerate(agents, 1):
        print(f"{i}. {name}")
    
    try:
        choice = input("Select agent (1-5): ").strip()
        
        if choice.isdigit() and 1 <= int(choice) <= 5:
            name, agent = agents[int(choice) - 1]
            print(f"\n🔍 Testing {name}")
            
            # Simple test for each agent
            if "RAG" in name:
                result = await agent.execute({
                    "query": "获取用户登录API信息",
                    "mode": "mix",
                    "top_k": 5
                })
            elif "Planner" in name:
                result = await agent.execute({
                    "api_info": {"entities": [{"name": "Login API", "type": "ENDPOINT"}]},
                    "test_types": ["functional"],
                    "special_requirements": []
                })
            elif "Generator" in name:
                result = await agent.execute({
                    "test_plan": {"test_cases": [{"case_id": "TC001", "name": "Test"}]},
                    "output_format": "playwright",
                    "language": "typescript"
                })
            elif "Executor" in name:
                result = await agent.execute({
                    "test_files": [{"name": "test.spec.ts", "content": "// test code"}],
                    "framework": "playwright"
                })
            elif "Analyzer" in name:
                result = await agent.execute({
                    "test_results": {
                        "suite_result": {"total_cases": 10, "passed_cases": 8},
                        "individual_results": []
                    }
                })
            
            print(f"✅ {name} test completed")
            print(f"Status: {result.get('status', 'unknown')}")
            
        else:
            print("❌ Invalid choice")
            
    except Exception as e:
        print(f"❌ Agent test failed: {e}")


def show_platform_status(platform_manager: PlatformManager):
    """Show platform status"""
    print("\n📊 Platform Status")
    print("-" * 30)
    print(f"Running: {platform_manager.running}")
    print(f"Services: {len(platform_manager.services)}")
    print(f"Environment: {platform_manager.config.environment.value}")
    print(f"Uptime: {datetime.utcnow().isoformat()}")


def show_configuration(config: PlatformConfig):
    """Show configuration"""
    print("\n⚙️ Platform Configuration")
    print("-" * 30)
    
    print(f"Environment: {config.environment.value}")
    print(f"Debug: {config.debug}")
    print(f"Host: {config.host}:{config.port}")
    print(f"LLM Provider: {config.llm.provider.value}")
    print(f"LLM Model: {config.llm.model}")
    print(f"RAG Enabled: {config.mcp.enable_rag_server}")
    print(f"Charts Enabled: {config.mcp.enable_chart_server}")
    print(f"Automation Enabled: {config.mcp.enable_automation_server}")


def setup_signal_handlers(platform_manager: PlatformManager):
    """Setup signal handlers for graceful shutdown"""
    def signal_handler(signum, frame):
        print(f"\nReceived signal {signum}")
        asyncio.create_task(platform_manager.stop())
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


async def main():
    """Main application entry point"""
    parser = argparse.ArgumentParser(description="API Automation Agent Platform")
    parser.add_argument("--config", type=str, help="Configuration file path")
    parser.add_argument("--env", type=str, choices=["development", "testing", "staging", "production"], 
                       help="Environment")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--interactive", action="store_true", help="Run in interactive mode")
    parser.add_argument("--demo", action="store_true", help="Run demo workflow")
    parser.add_argument("--create-env", action="store_true", help="Create sample .env file")
    parser.add_argument("--validate", action="store_true", help="Validate configuration")
    
    args = parser.parse_args()
    
    # Handle special commands
    if args.create_env:
        create_sample_env_file()
        print("✅ Sample .env file created")
        return
    
    if args.validate:
        if validate_environment():
            print("✅ Configuration is valid")
        else:
            print("❌ Configuration validation failed")
        return
    
    # Load configuration
    config_kwargs = {}
    if args.config:
        config_kwargs["_env_file"] = args.config
    if args.env:
        config_kwargs["environment"] = args.env
    if args.debug:
        config_kwargs["debug"] = True
    
    config = get_config(**config_kwargs)
    
    # Create platform manager
    platform_manager = PlatformManager(config)
    setup_signal_handlers(platform_manager)
    
    try:
        # Start platform
        if not await platform_manager.start():
            return
        
        if args.demo:
            # Run demo
            await run_workflow_demo(platform_manager.platform)
        elif args.interactive:
            # Run interactive mode
            await run_interactive_mode(platform_manager)
        else:
            # Run normal mode
            print("\n🎮 Platform is running. Press Ctrl+C to stop.")
            print("Run with --interactive for interactive mode")
            print("Run with --demo for demo workflow")
            
            # Keep running
            while platform_manager.running:
                await asyncio.sleep(1)
                
    except KeyboardInterrupt:
        print("\n👋 Interrupted by user")
    except Exception as e:
        print(f"\n❌ Platform error: {e}")
    finally:
        await platform_manager.stop()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)
