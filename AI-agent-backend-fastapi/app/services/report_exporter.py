# Copyright (c) 2025 左岚. All rights reserved.
"""
测试报告导出服务

支持导出为PDF和Excel格式
"""
import io
from datetime import datetime
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    logger.warning("reportlab未安装，PDF导出功能不可用")

try:
    import xlsxwriter
    XLSXWRITER_AVAILABLE = True
except ImportError:
    XLSXWRITER_AVAILABLE = False
    logger.warning("xlsxwriter未安装，Excel导出功能不可用")


class ReportExporter:
    """报告导出器"""
    
    def __init__(self):
        self.pdf_available = REPORTLAB_AVAILABLE
        self.excel_available = XLSXWRITER_AVAILABLE
    
    def export_to_pdf(self, report_data: Dict[str, Any]) -> bytes:
        """
        导出报告为PDF
        
        Args:
            report_data: 报告数据字典，包含:
                - report_id: 报告ID
                - report_name: 报告名称
                - test_type: 测试类型
                - total_cases: 总用例数
                - passed_cases: 通过数
                - failed_cases: 失败数
                - skipped_cases: 跳过数
                - pass_rate: 通过率
                - duration: 总耗时
                - start_time: 开始时间
                - end_time: 结束时间
                - test_results: 测试结果列表
        
        Returns:
            PDF文件的字节流
        """
        if not self.pdf_available:
            raise ImportError("reportlab未安装，无法导出PDF")
        
        # 创建字节流
        buffer = io.BytesIO()
        
        # 创建PDF文档
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        # 构建PDF内容
        story = []
        styles = getSampleStyleSheet()
        
        # 标题样式
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1890ff'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        # 添加标题
        title = Paragraph(f"测试报告 - {report_data.get('report_name', '未命名报告')}", title_style)
        story.append(title)
        story.append(Spacer(1, 12))
        
        # 基本信息
        info_data = [
            ['报告ID:', str(report_data.get('report_id', 'N/A'))],
            ['测试类型:', report_data.get('test_type', 'N/A').upper()],
            ['开始时间:', report_data.get('start_time', 'N/A')],
            ['结束时间:', report_data.get('end_time', 'N/A')],
            ['总耗时:', f"{report_data.get('duration', 0):.2f}秒"],
        ]
        
        info_table = Table(info_data, colWidths=[2*inch, 4*inch])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey)
        ]))
        story.append(info_table)
        story.append(Spacer(1, 20))
        
        # 统计信息
        story.append(Paragraph("测试统计", styles['Heading2']))
        story.append(Spacer(1, 12))
        
        stats_data = [
            ['指标', '数值'],
            ['总用例数', str(report_data.get('total_cases', 0))],
            ['通过数', str(report_data.get('passed_cases', 0))],
            ['失败数', str(report_data.get('failed_cases', 0))],
            ['跳过数', str(report_data.get('skipped_cases', 0))],
            ['通过率', f"{report_data.get('pass_rate', 0):.2f}%"]
        ]
        
        stats_table = Table(stats_data, colWidths=[3*inch, 3*inch])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1890ff')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(stats_table)
        story.append(Spacer(1, 20))
        
        # 详细结果
        story.append(Paragraph("详细结果", styles['Heading2']))
        story.append(Spacer(1, 12))
        
        results = report_data.get('test_results', [])
        if results:
            result_data = [['用例名称', '状态', '耗时(秒)', '备注']]
            
            for result in results[:20]:  # 限制最多显示20条
                status = result.get('status', 'unknown')
                # 状态显示
                status_display = {
                    'passed': '✓ 通过',
                    'failed': '✗ 失败',
                    'skipped': '- 跳过',
                    'error': '! 错误'
                }.get(status, status)
                
                result_data.append([
                    result.get('testcase_name', 'N/A')[:30],
                    status_display,
                    f"{result.get('duration', 0):.2f}",
                    result.get('error_message', '')[:40] if status in ['failed', 'error'] else ''
                ])
            
            result_table = Table(result_data, colWidths=[2.5*inch, 1*inch, 1*inch, 2*inch])
            result_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1890ff')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')])
            ]))
            story.append(result_table)
        else:
            story.append(Paragraph("无测试结果", styles['Normal']))
        
        # 生成PDF
        doc.build(story)
        
        # 获取PDF字节流
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        return pdf_bytes
    
    def export_to_excel(self, report_data: Dict[str, Any]) -> bytes:
        """
        导出报告为Excel
        
        Args:
            report_data: 报告数据字典
        
        Returns:
            Excel文件的字节流
        """
        if not self.excel_available:
            raise ImportError("xlsxwriter未安装，无法导出Excel")
        
        # 创建字节流
        buffer = io.BytesIO()
        
        # 创建工作簿
        workbook = xlsxwriter.Workbook(buffer, {'in_memory': True})
        
        # 定义格式
        title_format = workbook.add_format({
            'bold': True,
            'font_size': 16,
            'align': 'center',
            'valign': 'vcenter',
            'fg_color': '#1890ff',
            'font_color': 'white'
        })
        
        header_format = workbook.add_format({
            'bold': True,
            'font_size': 12,
            'align': 'center',
            'valign': 'vcenter',
            'fg_color': '#e6f7ff',
            'border': 1
        })
        
        cell_format = workbook.add_format({
            'align': 'left',
            'valign': 'vcenter',
            'border': 1
        })
        
        number_format = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
            'num_format': '0.00'
        })
        
        passed_format = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
            'fg_color': '#d4edda',
            'font_color': '#155724'
        })
        
        failed_format = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
            'fg_color': '#f8d7da',
            'font_color': '#721c24'
        })
        
        # 创建概览工作表
        summary_sheet = workbook.add_worksheet('报告概览')
        summary_sheet.set_column('A:A', 20)
        summary_sheet.set_column('B:B', 40)
        
        # 写入标题
        summary_sheet.merge_range('A1:B1', f"测试报告 - {report_data.get('report_name', '未命名报告')}", title_format)
        
        # 写入基本信息
        row = 2
        info_items = [
            ('报告ID', report_data.get('report_id', 'N/A')),
            ('测试类型', report_data.get('test_type', 'N/A').upper()),
            ('开始时间', report_data.get('start_time', 'N/A')),
            ('结束时间', report_data.get('end_time', 'N/A')),
            ('总耗时(秒)', f"{report_data.get('duration', 0):.2f}"),
            ('', ''),
            ('总用例数', report_data.get('total_cases', 0)),
            ('通过数', report_data.get('passed_cases', 0)),
            ('失败数', report_data.get('failed_cases', 0)),
            ('跳过数', report_data.get('skipped_cases', 0)),
            ('通过率(%)', f"{report_data.get('pass_rate', 0):.2f}")
        ]
        
        for label, value in info_items:
            summary_sheet.write(row, 0, label, header_format)
            summary_sheet.write(row, 1, value, cell_format)
            row += 1
        
        # 创建详细结果工作表
        detail_sheet = workbook.add_worksheet('详细结果')
        detail_sheet.set_column('A:A', 40)
        detail_sheet.set_column('B:B', 15)
        detail_sheet.set_column('C:C', 15)
        detail_sheet.set_column('D:D', 15)
        detail_sheet.set_column('E:E', 50)
        
        # 写入表头
        headers = ['用例名称', '状态', '耗时(秒)', '执行时间', '错误信息']
        for col, header in enumerate(headers):
            detail_sheet.write(0, col, header, header_format)
        
        # 写入详细结果
        results = report_data.get('test_results', [])
        for row, result in enumerate(results, start=1):
            status = result.get('status', 'unknown')
            
            # 选择状态格式
            if status == 'passed':
                status_format = passed_format
            elif status in ['failed', 'error']:
                status_format = failed_format
            else:
                status_format = cell_format
            
            detail_sheet.write(row, 0, result.get('testcase_name', 'N/A'), cell_format)
            detail_sheet.write(row, 1, status, status_format)
            detail_sheet.write(row, 2, result.get('duration', 0), number_format)
            detail_sheet.write(row, 3, result.get('executed_at', 'N/A'), cell_format)
            detail_sheet.write(row, 4, result.get('error_message', ''), cell_format)
        
        # 关闭工作簿
        workbook.close()
        
        # 获取Excel字节流
        excel_bytes = buffer.getvalue()
        buffer.close()
        
        return excel_bytes


# 全局实例
report_exporter = ReportExporter()

