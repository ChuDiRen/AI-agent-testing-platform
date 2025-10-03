// Copyright (c) 2025 左岚. All rights reserved.
/**
 * 导出工具类
 * 支持导出为 Excel 和 PDF
 */
import * as XLSX from 'xlsx'
import { saveAs } from 'file-saver'
import jsPDF from 'jspdf'
import autoTable from 'jspdf-autotable'
import type { TestReport } from '@/api/report'
import type { TestCase } from '@/api/testcase'

/**
 * 导出测试报告为 Excel
 */
export function exportReportToExcel(reports: TestReport[], filename: string = '测试报告') {
  try {
    // 准备数据
    const data = reports.map((report) => ({
      ID: report.id,
      报告名称: report.name,
      状态: getReportStatusText(report.status),
      报告类型: getReportTypeText(report.report_type),
      总用例数: report.total_cases,
      通过用例: report.passed_cases,
      失败用例: report.failed_cases,
      跳过用例: report.skipped_cases,
      '通过率(%)': report.pass_rate,
      '执行率(%)': report.execution_rate,
      '耗时(秒)': report.duration || 0,
      开始时间: report.start_time || '',
      结束时间: report.end_time || '',
      创建时间: report.created_at
    }))

    // 创建工作表
    const worksheet = XLSX.utils.json_to_sheet(data)

    // 设置列宽
    const colWidths = [
      { wch: 8 },  // ID
      { wch: 25 }, // 报告名称
      { wch: 10 }, // 状态
      { wch: 12 }, // 报告类型
      { wch: 10 }, // 总用例数
      { wch: 10 }, // 通过用例
      { wch: 10 }, // 失败用例
      { wch: 10 }, // 跳过用例
      { wch: 12 }, // 通过率
      { wch: 12 }, // 执行率
      { wch: 12 }, // 耗时
      { wch: 20 }, // 开始时间
      { wch: 20 }, // 结束时间
      { wch: 20 }  // 创建时间
    ]
    worksheet['!cols'] = colWidths

    // 创建工作簿
    const workbook = XLSX.utils.book_new()
    XLSX.utils.book_append_sheet(workbook, worksheet, '测试报告')

    // 导出文件
    const excelBuffer = XLSX.write(workbook, { bookType: 'xlsx', type: 'array' })
    const blob = new Blob([excelBuffer], {
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    })
    saveAs(blob, `${filename}_${new Date().getTime()}.xlsx`)

    return true
  } catch (error) {
    console.error('导出 Excel 失败:', error)
    return false
  }
}

/**
 * 导出测试报告为 PDF
 */
export function exportReportToPDF(reports: TestReport[], filename: string = '测试报告') {
  try {
    // 创建 PDF 文档
    const doc = new jsPDF()

    // 设置中文字体（注：需要额外配置字体文件）
    // doc.setFont('SimSun')

    // 添加标题
    doc.setFontSize(18)
    doc.text('测试报告', 14, 20)

    // 添加生成时间
    doc.setFontSize(10)
    doc.text(`生成时间: ${new Date().toLocaleString('zh-CN')}`, 14, 30)

    // 准备表格数据
    const tableData = reports.map((report) => [
      report.id,
      report.name,
      getReportStatusText(report.status),
      report.total_cases,
      report.passed_cases,
      report.failed_cases,
      `${report.pass_rate}%`,
      report.duration || 0,
      report.created_at.substring(0, 10)
    ])

    // 生成表格
    autoTable(doc, {
      startY: 35,
      head: [['ID', '报告名称', '状态', '总数', '通过', '失败', '通过率', '耗时(s)', '创建时间']],
      body: tableData,
      styles: {
        fontSize: 8,
        cellPadding: 2
      },
      headStyles: {
        fillColor: [64, 158, 255],
        textColor: 255,
        fontStyle: 'bold'
      },
      columnStyles: {
        0: { cellWidth: 15 },
        1: { cellWidth: 45 },
        2: { cellWidth: 20 },
        3: { cellWidth: 15 },
        4: { cellWidth: 15 },
        5: { cellWidth: 15 },
        6: { cellWidth: 20 },
        7: { cellWidth: 18 },
        8: { cellWidth: 25 }
      }
    })

    // 保存文件
    doc.save(`${filename}_${new Date().getTime()}.pdf`)

    return true
  } catch (error) {
    console.error('导出 PDF 失败:', error)
    return false
  }
}

/**
 * 导出测试用例为 Excel
 */
export function exportTestCasesToExcel(testCases: TestCase[], filename: string = '测试用例') {
  try {
    // 准备数据
    const data = testCases.map((testCase) => ({
      ID: testCase.id,
      用例名称: testCase.name,
      所属模块: testCase.module || '',
      用例类型: testCase.test_type,
      优先级: testCase.priority,
      状态: testCase.status,
      描述: testCase.description || '',
      前置条件: testCase.preconditions || '',
      测试步骤: testCase.test_steps || '',
      预期结果: testCase.expected_result || '',
      标签: testCase.tags || '',
      创建时间: testCase.created_at,
      更新时间: testCase.updated_at
    }))

    // 创建工作表
    const worksheet = XLSX.utils.json_to_sheet(data)

    // 设置列宽
    const colWidths = [
      { wch: 8 },  // ID
      { wch: 25 }, // 用例名称
      { wch: 15 }, // 所属模块
      { wch: 12 }, // 用例类型
      { wch: 10 }, // 优先级
      { wch: 10 }, // 状态
      { wch: 30 }, // 描述
      { wch: 30 }, // 前置条件
      { wch: 40 }, // 测试步骤
      { wch: 30 }, // 预期结果
      { wch: 20 }, // 标签
      { wch: 20 }, // 创建时间
      { wch: 20 }  // 更新时间
    ]
    worksheet['!cols'] = colWidths

    // 创建工作簿
    const workbook = XLSX.utils.book_new()
    XLSX.utils.book_append_sheet(workbook, worksheet, '测试用例')

    // 导出文件
    const excelBuffer = XLSX.write(workbook, { bookType: 'xlsx', type: 'array' })
    const blob = new Blob([excelBuffer], {
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    })
    saveAs(blob, `${filename}_${new Date().getTime()}.xlsx`)

    return true
  } catch (error) {
    console.error('导出 Excel 失败:', error)
    return false
  }
}

/**
 * 获取报告状态文本
 */
function getReportStatusText(status: string): string {
  const statusMap: Record<string, string> = {
    generating: '生成中',
    completed: '已完成',
    failed: '失败',
    archived: '已归档'
  }
  return statusMap[status] || status
}

/**
 * 获取报告类型文本
 */
function getReportTypeText(type: string): string {
  const typeMap: Record<string, string> = {
    execution: '执行报告',
    summary: '汇总报告',
    detailed: '详细报告',
    custom: '自定义报告'
  }
  return typeMap[type] || type
}

