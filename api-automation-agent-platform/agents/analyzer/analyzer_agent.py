"""
Analyzer Agent - Test Result Analysis

The Analyzer Agent is responsible for:
1. Analyzing test execution results
2. Generating comprehensive reports
3. Creating visualizations and charts
4. Identifying patterns and trends
5. Providing recommendations and insights
"""
from typing import Any, Dict, List, Optional, Union
import json
import uuid
from datetime import datetime, timedelta
from dataclasses import dataclass
from collections import defaultdict
import statistics
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate


@dataclass
class TestMetrics:
    """Test metrics data structure"""
    total_tests: int
    passed_tests: int
    failed_tests: int
    skipped_tests: int
    pass_rate: float
    failure_rate: float
    average_duration: float
    total_duration: float


@dataclass
class PerformanceMetrics:
    """Performance metrics data structure"""
    avg_response_time: float
    min_response_time: float
    max_response_time: float
    p95_response_time: float
    p99_response_time: float
    total_requests: int
    requests_per_second: float


@dataclass
class AnalysisReport:
    """Comprehensive analysis report"""
    report_id: str
    generated_at: str
    test_metrics: TestMetrics
    performance_metrics: Optional[PerformanceMetrics]
    failure_analysis: Dict[str, Any]
    trends_analysis: Dict[str, Any]
    recommendations: List[str]
    visualizations: List[Dict[str, Any]]


class AnalyzerAgent:
    """
    Test Result Analysis Agent
    
    Analyzes test results and generates comprehensive reports with visualizations.
    """

    def __init__(self, llm: Optional[Any] = None, mcp_client: Optional[Any] = None):
        """
        Initialize analyzer agent
        
        Args:
            llm: Optional LLM instance
            mcp_client: Optional MCP client for Chart generation
        """
        self.llm = llm or ChatOpenAI(
            model="gpt-4-turbo-preview",
            temperature=0.3
        )
        self.mcp_client = mcp_client
        self.name = "analyzer"
        self.description = "Analyze test results and generate reports"

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze test results and generate reports
        
        Args:
            input_data: Dictionary containing:
                - test_results: Test execution results
                - historical_data: Optional historical test data
                - analysis_options: Analysis configuration options
        
        Returns:
            Dictionary containing analysis report and visualizations
        """
        try:
            # Extract input parameters
            test_results = input_data.get("test_results", {})
            historical_data = input_data.get("historical_data", [])
            analysis_options = input_data.get("analysis_options", {})
            
            # Analyze test results
            test_metrics = self._calculate_test_metrics(test_results)
            performance_metrics = self._calculate_performance_metrics(test_results)
            
            # Perform failure analysis
            failure_analysis = await self._analyze_failures(test_results)
            
            # Analyze trends (if historical data available)
            trends_analysis = await self._analyze_trends(test_results, historical_data)
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(
                test_metrics, performance_metrics, failure_analysis
            )
            
            # Generate visualizations
            visualizations = await self._generate_visualizations(
                test_metrics, performance_metrics, test_results
            )
            
            # Create comprehensive report
            report = AnalysisReport(
                report_id=str(uuid.uuid4()),
                generated_at=datetime.utcnow().isoformat(),
                test_metrics=test_metrics,
                performance_metrics=performance_metrics,
                failure_analysis=failure_analysis,
                trends_analysis=trends_analysis,
                recommendations=recommendations,
                visualizations=visualizations
            )
            
            return {
                "status": "success",
                "analysis_report": report.__dict__,
                "metadata": {
                    "analyzed_at": datetime.utcnow().isoformat(),
                    "data_points": len(test_results.get("individual_results", [])),
                    "has_historical_data": len(historical_data) > 0,
                    "visualization_count": len(visualizations)
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "analysis_report": None
            }

    def _calculate_test_metrics(self, test_results: Dict[str, Any]) -> TestMetrics:
        """Calculate basic test metrics"""
        suite_result = test_results.get("suite_result", {})
        individual_results = test_results.get("individual_results", [])
        
        total_tests = suite_result.get("total_cases", len(individual_results))
        passed_tests = suite_result.get("passed_cases", 0)
        failed_tests = suite_result.get("failed_cases", 0)
        skipped_tests = suite_result.get("skipped_cases", 0)
        
        # Calculate rates
        pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        failure_rate = (failed_tests / total_tests * 100) if total_tests > 0 else 0
        
        # Calculate duration metrics
        durations = [r.get("duration_ms", 0) for r in individual_results if r.get("duration_ms")]
        average_duration = statistics.mean(durations) if durations else 0
        total_duration = suite_result.get("duration_ms", sum(durations))
        
        return TestMetrics(
            total_tests=total_tests,
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            skipped_tests=skipped_tests,
            pass_rate=pass_rate,
            failure_rate=failure_rate,
            average_duration=average_duration,
            total_duration=total_duration
        )

    def _calculate_performance_metrics(self, test_results: Dict[str, Any]) -> Optional[PerformanceMetrics]:
        """Calculate performance metrics from test results"""
        individual_results = test_results.get("individual_results", [])
        
        # Extract performance data
        response_times = []
        for result in individual_results:
            perf_data = result.get("performance_data", {})
            if perf_data.get("response_time_ms"):
                response_times.append(perf_data["response_time_ms"])
        
        if not response_times:
            return None
        
        # Calculate statistics
        avg_response_time = statistics.mean(response_times)
        min_response_time = min(response_times)
        max_response_time = max(response_times)
        p95_response_time = self._percentile(response_times, 95)
        p99_response_time = self._percentile(response_times, 99)
        
        # Calculate requests per second
        total_duration = sum(r.get("duration_ms", 0) for r in individual_results) / 1000  # Convert to seconds
        requests_per_second = len(response_times) / total_duration if total_duration > 0 else 0
        
        return PerformanceMetrics(
            avg_response_time=avg_response_time,
            min_response_time=min_response_time,
            max_response_time=max_response_time,
            p95_response_time=p95_response_time,
            p99_response_time=p99_response_time,
            total_requests=len(response_times),
            requests_per_second=requests_per_second
        )

    async def _analyze_failures(self, test_results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze test failures and identify patterns"""
        individual_results = test_results.get("individual_results", [])
        failed_tests = [r for r in individual_results if r.get("status") == "failed"]
        
        if not failed_tests:
            return {
                "total_failures": 0,
                "failure_patterns": [],
                "common_errors": [],
                "failure_categories": {}
            }
        
        # Categorize failures
        failure_categories = defaultdict(int)
        error_patterns = defaultdict(int)
        common_errors = []
        
        for failed_test in failed_tests:
            error_message = failed_test.get("error_message", "")
            
            # Categorize by error type
            if "timeout" in error_message.lower():
                failure_categories["timeout"] += 1
            elif "401" in error_message or "unauthorized" in error_message.lower():
                failure_categories["authentication"] += 1
            elif "404" in error_message or "not found" in error_message.lower():
                failure_categories["endpoint_not_found"] += 1
            elif "500" in error_message or "internal server error" in error_message.lower():
                failure_categories["server_error"] += 1
            elif "assertion" in error_message.lower():
                failure_categories["assertion_failure"] += 1
            else:
                failure_categories["other"] += 1
            
            # Extract error patterns
            if error_message:
                # Simple pattern extraction
                words = error_message.split()[:5]  # First 5 words
                pattern = " ".join(words)
                error_patterns[pattern] += 1
                
                # Add to common errors if it appears multiple times
                if error_patterns[pattern] > 1:
                    common_errors.append({
                        "pattern": pattern,
                        "count": error_patterns[pattern],
                        "example": error_message[:100] + "..." if len(error_message) > 100 else error_message
                    })
        
        return {
            "total_failures": len(failed_tests),
            "failure_rate": len(failed_tests) / len(individual_results) * 100,
            "failure_categories": dict(failure_categories),
            "error_patterns": dict(error_patterns),
            "common_errors": common_errors[:5],  # Top 5 common errors
            "failed_tests": [
                {
                    "case_id": test.get("case_id"),
                    "name": test.get("name"),
                    "error": test.get("error_message")
                }
                for test in failed_tests
            ]
        }

    async def _analyze_trends(self, test_results: Dict[str, Any], historical_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze trends using historical data"""
        if not historical_data:
            return {
                "trend_analysis": "No historical data available",
                "trend_data": {},
                "insights": []
            }
        
        # Extract metrics from historical data
        historical_metrics = []
        for data in historical_data:
            if "test_metrics" in data:
                historical_metrics.append(data["test_metrics"])
        
        if len(historical_metrics) < 2:
            return {
                "trend_analysis": "Insufficient historical data for trend analysis",
                "trend_data": {},
                "insights": []
            }
        
        # Calculate trends
        current_metrics = self._calculate_test_metrics(test_results)
        
        # Pass rate trend
        pass_rates = [m.get("pass_rate", 0) for m in historical_metrics]
        pass_rates.append(current_metrics.pass_rate)
        
        # Duration trend
        durations = [m.get("total_duration", 0) for m in historical_metrics]
        durations.append(current_metrics.total_duration)
        
        # Calculate trend direction
        pass_rate_trend = "improving" if pass_rates[-1] > pass_rates[-2] else "declining" if pass_rates[-1] < pass_rates[-2] else "stable"
        duration_trend = "improving" if durations[-1] < durations[-2] else "declining" if durations[-1] > durations[-2] else "stable"
        
        # Generate insights
        insights = []
        
        if pass_rate_trend == "declining":
            insights.append("Test pass rate is declining. Consider reviewing recent changes.")
        elif pass_rate_trend == "improving":
            insights.append("Test pass rate is improving. Keep up the good work!")
        
        if duration_trend == "declining":
            insights.append("Test execution time is increasing. Consider performance optimization.")
        elif duration_trend == "improving":
            insights.append("Test execution time is improving. Good performance optimization!")
        
        return {
            "trend_analysis": f"Pass rate is {pass_rate_trend}, execution time is {duration_trend}",
            "trend_data": {
                "pass_rates": pass_rates,
                "durations": durations,
                "data_points": len(historical_metrics) + 1
            },
            "insights": insights
        }

    async def _generate_recommendations(self, test_metrics: TestMetrics, performance_metrics: Optional[PerformanceMetrics], failure_analysis: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations based on analysis"""
        recommendations = []
        
        # Test metrics recommendations
        if test_metrics.pass_rate < 80:
            recommendations.append("Test pass rate is below 80%. Review and fix failing tests.")
        
        if test_metrics.failure_rate > 20:
            recommendations.append("High failure rate detected. Consider implementing better error handling.")
        
        if test_metrics.average_duration > 5000:  # 5 seconds
            recommendations.append("Average test duration is high. Consider optimizing test performance.")
        
        # Performance metrics recommendations
        if performance_metrics:
            if performance_metrics.avg_response_time > 2000:  # 2 seconds
                recommendations.append("API response time is slow. Consider performance optimization.")
            
            if performance_metrics.p95_response_time > 5000:  # 5 seconds
                recommendations.append("95th percentile response time is high. Investigate performance bottlenecks.")
        
        # Failure analysis recommendations
        failure_categories = failure_analysis.get("failure_categories", {})
        
        if failure_categories.get("timeout", 0) > 0:
            recommendations.append("Timeout failures detected. Consider increasing timeout values or optimizing performance.")
        
        if failure_categories.get("authentication", 0) > 0:
            recommendations.append("Authentication failures detected. Review authentication mechanisms.")
        
        if failure_categories.get("assertion_failure", 0) > 0:
            recommendations.append("Assertion failures detected. Review test expectations and API contracts.")
        
        # General recommendations
        if not recommendations:
            recommendations.append("Test results look good! Continue monitoring and maintaining test quality.")
        
        return recommendations

    async def _generate_visualizations(self, test_metrics: TestMetrics, performance_metrics: Optional[PerformanceMetrics], test_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate visualizations for the analysis report"""
        visualizations = []
        
        if self.mcp_client:
            # Use Chart MCP Server for professional visualizations
            try:
                # Test results pie chart
                pie_chart = await self._generate_pie_chart(test_metrics)
                if pie_chart:
                    visualizations.append(pie_chart)
                
                # Performance metrics line chart
                if performance_metrics:
                    perf_chart = await self._generate_performance_chart(performance_metrics)
                    if perf_chart:
                        visualizations.append(perf_chart)
                
                # Test execution timeline
                timeline_chart = await self._generate_timeline_chart(test_results)
                if timeline_chart:
                    visualizations.append(timeline_chart)
                
            except Exception as e:
                print(f"Warning: Failed to generate charts with MCP: {e}")
                # Fallback to simple chart data
                visualizations.extend(self._generate_simple_charts(test_metrics, performance_metrics))
        else:
            # Generate simple chart data
            visualizations.extend(self._generate_simple_charts(test_metrics, performance_metrics))
        
        return visualizations

    async def _generate_pie_chart(self, test_metrics: TestMetrics) -> Optional[Dict[str, Any]]:
        """Generate test results pie chart using Chart MCP"""
        try:
            chart_data = {
                "type": "pie",
                "data": {
                    "labels": ["Passed", "Failed", "Skipped"],
                    "values": [
                        test_metrics.passed_tests,
                        test_metrics.failed_tests,
                        test_metrics.skipped_tests
                    ]
                },
                "config": {
                    "title": "Test Results Distribution",
                    "colors": ["#52c41a", "#ff4d4f", "#faad14"],
                    "legend": {
                        "position": "bottom"
                    }
                }
            }
            
            result = await self.mcp_client.call_tool(
                "chart_generate",
                {
                    "chart_type": "pie",
                    "data": chart_data["data"],
                    "config": chart_data["config"]
                }
            )
            
            return {
                "type": "pie_chart",
                "title": "Test Results Distribution",
                "chart_data": chart_data,
                "chart_result": json.loads(result) if isinstance(result, str) else result
            }
            
        except Exception as e:
            return None

    async def _generate_performance_chart(self, performance_metrics: PerformanceMetrics) -> Optional[Dict[str, Any]]:
        """Generate performance metrics chart using Chart MCP"""
        try:
            chart_data = {
                "type": "bar",
                "data": {
                    "labels": ["Avg", "Min", "Max", "P95", "P99"],
                    "values": [
                        performance_metrics.avg_response_time,
                        performance_metrics.min_response_time,
                        performance_metrics.max_response_time,
                        performance_metrics.p95_response_time,
                        performance_metrics.p99_response_time
                    ]
                },
                "config": {
                    "title": "Response Time Metrics (ms)",
                    "xField": "metric",
                    "yField": "time",
                    "color": "#1890ff"
                }
            }
            
            result = await self.mcp_client.call_tool(
                "chart_generate",
                {
                    "chart_type": "bar",
                    "data": chart_data["data"],
                    "config": chart_data["config"]
                }
            )
            
            return {
                "type": "performance_chart",
                "title": "Response Time Metrics",
                "chart_data": chart_data,
                "chart_result": json.loads(result) if isinstance(result, str) else result
            }
            
        except Exception as e:
            return None

    async def _generate_timeline_chart(self, test_results: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate test execution timeline chart using Chart MCP"""
        try:
            individual_results = test_results.get("individual_results", [])
            
            # Create timeline data
            timeline_data = []
            cumulative_time = 0
            
            for i, result in enumerate(individual_results):
                duration = result.get("duration_ms", 0) / 1000  # Convert to seconds
                timeline_data.append({
                    "test": f"Test {i+1}",
                    "start_time": cumulative_time,
                    "duration": duration,
                    "status": result.get("status", "unknown")
                })
                cumulative_time += duration
            
            chart_data = {
                "type": "timeline",
                "data": timeline_data,
                "config": {
                    "title": "Test Execution Timeline",
                    "xField": "start_time",
                    "yField": "test",
                    "colorField": "status"
                }
            }
            
            result = await self.mcp_client.call_tool(
                "chart_generate",
                {
                    "chart_type": "timeline",
                    "data": chart_data["data"],
                    "config": chart_data["config"]
                }
            )
            
            return {
                "type": "timeline_chart",
                "title": "Test Execution Timeline",
                "chart_data": chart_data,
                "chart_result": json.loads(result) if isinstance(result, str) else result
            }
            
        except Exception as e:
            return None

    def _generate_simple_charts(self, test_metrics: TestMetrics, performance_metrics: Optional[PerformanceMetrics]) -> List[Dict[str, Any]]:
        """Generate simple chart data as fallback"""
        charts = []
        
        # Test results pie chart data
        charts.append({
            "type": "pie_chart_data",
            "title": "Test Results Distribution",
            "data": {
                "labels": ["Passed", "Failed", "Skipped"],
                "values": [
                    test_metrics.passed_tests,
                    test_metrics.failed_tests,
                    test_metrics.skipped_tests
                ]
            }
        })
        
        # Performance metrics bar chart data
        if performance_metrics:
            charts.append({
                "type": "performance_chart_data",
                "title": "Response Time Metrics",
                "data": {
                    "labels": ["Avg", "Min", "Max", "P95", "P99"],
                    "values": [
                        performance_metrics.avg_response_time,
                        performance_metrics.min_response_time,
                        performance_metrics.max_response_time,
                        performance_metrics.p95_response_time,
                        performance_metrics.p99_response_time
                    ]
                }
            })
        
        return charts

    def _percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile value"""
        if not data:
            return 0
        
        sorted_data = sorted(data)
        index = (percentile / 100) * (len(sorted_data) - 1)
        
        if index.is_integer():
            return sorted_data[int(index)]
        else:
            lower = sorted_data[int(index)]
            upper = sorted_data[int(index) + 1]
            return lower + (upper - lower) * (index - int(index))

    async def generate_markdown_report(self, analysis_report: Dict[str, Any]) -> str:
        """Generate a comprehensive markdown report"""
        report = analysis_report.get("analysis_report", {})
        test_metrics = report.get("test_metrics", {})
        performance_metrics = report.get("performance_metrics", {})
        failure_analysis = report.get("failure_analysis", {})
        recommendations = report.get("recommendations", [])
        
        markdown = f"""
# API Test Analysis Report

**Generated:** {report.get('generated_at', 'Unknown')}  
**Report ID:** {report.get('report_id', 'Unknown')}

## 📊 Test Summary

- **Total Tests:** {test_metrics.get('total_tests', 0)}
- **Passed:** {test_metrics.get('passed_tests', 0)} ({test_metrics.get('pass_rate', 0):.1f}%)
- **Failed:** {test_metrics.get('failed_tests', 0)} ({test_metrics.get('failure_rate', 0):.1f}%)
- **Skipped:** {test_metrics.get('skipped_tests', 0)}
- **Total Duration:** {test_metrics.get('total_duration', 0):.2f}ms
- **Average Duration:** {test_metrics.get('average_duration', 0):.2f}ms

## ⚡ Performance Metrics

"""
        
        if performance_metrics:
            markdown += f"""
- **Average Response Time:** {performance_metrics.get('avg_response_time', 0):.2f}ms
- **Min Response Time:** {performance_metrics.get('min_response_time', 0):.2f}ms
- **Max Response Time:** {performance_metrics.get('max_response_time', 0):.2f}ms
- **95th Percentile:** {performance_metrics.get('p95_response_time', 0):.2f}ms
- **99th Percentile:** {performance_metrics.get('p99_response_time', 0):.2f}ms
- **Requests/Second:** {performance_metrics.get('requests_per_second', 0):.2f}
"""
        else:
            markdown += "No performance data available.\n"
        
        markdown += "\n## 🚨 Failure Analysis\n\n"
        
        if failure_analysis.get("total_failures", 0) > 0:
            markdown += f"- **Total Failures:** {failure_analysis.get('total_failures', 0)}\n"
            markdown += f"- **Failure Rate:** {failure_analysis.get('failure_rate', 0):.1f}%\n\n"
            
            failure_categories = failure_analysis.get("failure_categories", {})
            if failure_categories:
                markdown += "**Failure Categories:**\n"
                for category, count in failure_categories.items():
                    markdown += f"- {category.replace('_', ' ').title()}: {count}\n"
                markdown += "\n"
            
            common_errors = failure_analysis.get("common_errors", [])
            if common_errors:
                markdown += "**Common Error Patterns:**\n"
                for error in common_errors[:3]:  # Top 3
                    markdown += f"- {error.get('pattern', 'Unknown')}: {error.get('count', 0)} occurrences\n"
                markdown += "\n"
        else:
            markdown += "No failures detected. All tests passed! 🎉\n\n"
        
        markdown += "## 💡 Recommendations\n\n"
        
        for i, recommendation in enumerate(recommendations, 1):
            markdown += f"{i}. {recommendation}\n"
        
        markdown += "\n## 📈 Visualizations\n\n"
        
        visualizations = report.get("visualizations", [])
        for viz in visualizations:
            viz_type = viz.get("type", "unknown")
            viz_title = viz.get("title", "Chart")
            markdown += f"- **{viz_title}** ({viz_type})\n"
        
        return markdown
