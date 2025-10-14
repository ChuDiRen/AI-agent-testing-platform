"""API-Engine命令行执行服务"""
import subprocess
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

class ApiEngineService:
    """封装命令行调用huace-apirun执行逻辑"""
    
    @staticmethod
    def execute_test(
        yaml_dir: Path,
        report_dir: Path,
        log_file: Path,
        timeout: int = 300
    ) -> Dict[str, Any]:
        """
        执行API测试
        
        Args:
            yaml_dir: YAML用例目录
            report_dir: Allure报告目录
            log_file: 日志文件
            timeout: 超时时间（秒）
            
        Returns:
            执行结果字典
        """
        # 构建命令
        command = [
            'huace-apirun',
            '--cases', str(yaml_dir),
            '--alluredir', str(report_dir)
        ]
        
        # 执行结果
        result = {
            'success': False,
            'return_code': -1,
            'stdout': '',
            'stderr': '',
            'start_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'end_time': None,
            'duration': 0,
            'error_message': None
        }
        
        try:
            # 执行命令
            start_time = datetime.now()
            
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8'
            )
            
            # 等待执行完成
            stdout, stderr = process.communicate(timeout=timeout)
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # 更新结果
            result['return_code'] = process.returncode
            result['stdout'] = stdout
            result['stderr'] = stderr
            result['end_time'] = end_time.strftime('%Y-%m-%d %H:%M:%S')
            result['duration'] = duration
            result['success'] = process.returncode == 0
            
            # 写入日志文件
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write(f"=== 执行命令 ===\n")
                f.write(' '.join(command) + '\n\n')
                f.write(f"=== 开始时间 ===\n{result['start_time']}\n\n")
                f.write(f"=== 结束时间 ===\n{result['end_time']}\n\n")
                f.write(f"=== 执行时长 ===\n{duration}秒\n\n")
                f.write(f"=== 返回码 ===\n{process.returncode}\n\n")
                f.write(f"=== 标准输出 ===\n{stdout}\n\n")
                f.write(f"=== 错误输出 ===\n{stderr}\n")
            
        except subprocess.TimeoutExpired:
            result['error_message'] = f'测试执行超时（{timeout}秒）'
            if process:
                process.kill()
        except FileNotFoundError:
            result['error_message'] = 'huace-apirun命令不存在，请确认api-engine已正确安装'
        except Exception as e:
            result['error_message'] = f'执行失败: {str(e)}'
        
        return result
    
    @staticmethod
    def check_command_available() -> bool:
        """
        检查huace-apirun命令是否可用
        
        Returns:
            True表示可用，False表示不可用
        """
        try:
            result = subprocess.run(
                ['huace-apirun', '--help'],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except:
            return False
    
    @staticmethod
    def parse_allure_results(report_dir: Path) -> Optional[Dict[str, Any]]:
        """
        解析Allure测试结果
        
        Args:
            report_dir: Allure报告目录
            
        Returns:
            解析后的测试结果，如果失败返回None
        """
        try:
            # 查找result.json或其他allure结果文件
            result_files = list(report_dir.glob("*-result.json"))
            
            if not result_files:
                return None
            
            # 解析所有结果文件
            all_results = []
            for result_file in result_files:
                with open(result_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    all_results.append(data)
            
            # 汇总统计信息
            total = len(all_results)
            passed = sum(1 for r in all_results if r.get('status') == 'passed')
            failed = sum(1 for r in all_results if r.get('status') == 'failed')
            broken = sum(1 for r in all_results if r.get('status') == 'broken')
            skipped = sum(1 for r in all_results if r.get('status') == 'skipped')
            
            summary = {
                'total': total,
                'passed': passed,
                'failed': failed,
                'broken': broken,
                'skipped': skipped,
                'pass_rate': round(passed / total * 100, 2) if total > 0 else 0,
                'results': all_results
            }
            
            return summary
            
        except Exception as e:
            print(f"解析Allure结果失败: {e}")
            return None
    
    @staticmethod
    def extract_response_data(allure_results: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        从Allure结果中提取响应数据
        
        Args:
            allure_results: Allure解析结果
            
        Returns:
            提取的响应数据，包含状态码、响应时间、响应体等
        """
        if not allure_results or 'results' not in allure_results:
            return None
        
        results = allure_results['results']
        if not results:
            return None
        
        # 取第一个结果（通常一个YAML只有一个测试用例）
        first_result = results[0]
        
        # 提取响应数据
        response_data = {
            'status': first_result.get('status'),
            'status_code': None,
            'response_time': first_result.get('stop', 0) - first_result.get('start', 0),
            'response_body': None,
            'response_headers': None,
            'error_message': None
        }
        
        # 尝试从attachments中提取响应信息
        attachments = first_result.get('attachments', [])
        for attachment in attachments:
            if 'response' in attachment.get('name', '').lower():
                # 这里需要根据实际的attachment结构来解析
                # 暂时保留占位逻辑
                pass
        
        # 如果失败，提取错误信息
        if first_result.get('status') in ['failed', 'broken']:
            status_details = first_result.get('statusDetails', {})
            response_data['error_message'] = status_details.get('message', '未知错误')
        
        return response_data
