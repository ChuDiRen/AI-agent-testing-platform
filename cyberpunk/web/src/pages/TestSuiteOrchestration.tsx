import React, { useState } from 'react';
import { Table, Button, Input, Select, Space, Badge, Modal, Form, Transfer, Steps, Drawer, Descriptions, Tag, message, Card } from 'antd';
import {
  Play, Plus, Trash2, Clock,
  TestTube, FileStack
} from 'lucide-react';

const { Option } = Select;
const { TextArea } = Input;

// --- Types ---

interface TestSuite {
  id: string;
  name: string;
  description: string;
  caseCount: number;
  schedule: string; // Cron expression or 'Manual'
  status: 'active' | 'paused' | 'running';
  lastRun?: string;
}

interface TestCase {
  key: string;
  title: string;
  description: string;
  tag: string;
}

// --- Mock Data ---

const MOCK_SUITES: TestSuite[] = [
  {
    id: '1',
    name: '冒烟测试 - 每日',
    description: '每日构建的关键路径验证。',
    caseCount: 12,
    schedule: '0 2 * * *',
    status: 'active',
    lastRun: '2025-01-14 02:00:00'
  },
  {
    id: '2',
    name: '回归测试套件 - 每周',
    description: '系统完整回归测试。',
    caseCount: 156,
    schedule: '0 0 * * 0',
    status: 'paused',
    lastRun: '2025-01-07 00:00:00'
  },
  {
    id: '3',
    name: '认证模块校验',
    description: '专注于身份认证流程的测试。',
    caseCount: 24,
    schedule: '手动',
    status: 'active',
    lastRun: '2025-01-13 15:30:00'
  }
];

const MOCK_ALL_CASES: TestCase[] = Array.from({ length: 20 }).map((_, i) => ({
  key: i.toString(),
  title: `测试用例 ${i + 1}`,
  description: `验证功能集 ${Math.floor(i / 5) + 1}`,
  tag: ['API', 'UI', '性能'][i % 3],
}));

// --- Components ---

export const TestSuiteOrchestration: React.FC = () => {
  const [suites, setSuites] = useState<TestSuite[]>(MOCK_SUITES);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [selectedSuite, setSelectedSuite] = useState<TestSuite | null>(null);
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);

  // Form State
  const [form] = Form.useForm();
  const [targetKeys, setTargetKeys] = useState<string[]>([]);
  const [selectedKeys, setSelectedKeys] = useState<string[]>([]);

  // --- Handlers ---

  const handleCreate = () => {
    setIsModalOpen(true);
    setCurrentStep(0);
    form.resetFields();
    setTargetKeys([]);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
  };

  const handleNext = async () => {
    try {
      if (currentStep === 0) {
        await form.validateFields(['name', 'description']);
      }
      setCurrentStep(currentStep + 1);
    } catch {
      // 校验失败
    }
  };

  const handlePrev = () => {
    setCurrentStep(currentStep - 1);
  };

  const handleFinish = () => {
    form.validateFields().then(values => {
      const newSuite: TestSuite = {
        id: Date.now().toString(),
        name: values.name,
        description: values.description,
        caseCount: targetKeys.length,
        schedule: values.scheduleType === 'manual' ? '手动' : values.cronExpression,
        status: 'active',
        lastRun: '-'
      };

      setSuites([...suites, newSuite]);
      message.success('测试套件创建成功');
      setIsModalOpen(false);
    });
  };

  const handleTransferChange = (nextTargetKeys: React.Key[]) => {
    setTargetKeys(nextTargetKeys as string[]);
  };

  const handleSelectChange = (sourceSelectedKeys: React.Key[], targetSelectedKeys: React.Key[]) => {
    setSelectedKeys([...sourceSelectedKeys, ...targetSelectedKeys] as string[]);
  };

  const handleRowClick = (record: TestSuite) => {
    setSelectedSuite(record);
    setIsDrawerOpen(true);
  };

  const handleDelete = (e: React.MouseEvent, id: string) => {
    e.stopPropagation();
    setSuites(suites.filter(s => s.id !== id));
    message.success('套件已删除');
  };

  // --- Renderers ---

  const columns = [
    {
      title: '名称',
      dataIndex: 'name',
      key: 'name',
      render: (text: string) => <span className="font-medium text-slate-700">{text}</span>,
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description',
      ellipsis: true,
      render: (text: string) => <span className="text-slate-500">{text}</span>,
    },
    {
      title: '用例数',
      dataIndex: 'caseCount',
      key: 'caseCount',
      width: 100,
      render: (count: number) => (
        <Tag icon={<FileStack size={12} />} className="bg-slate-100 text-slate-600 border-slate-200">
          {count}
        </Tag>
      ),
    },
    {
      title: '调度计划',
      dataIndex: 'schedule',
      key: 'schedule',
      width: 150,
      render: (text: string) => (
        <Space size={4}>
          {text === '手动' ? <Play size={14} className="text-slate-400" /> : <Clock size={14} className="text-blue-500" />}
          <span className="font-mono text-xs text-slate-500">{text}</span>
        </Space>
      ),
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 120,
      render: (status: string) => {
        const color = status === 'active' ? 'success' : status === 'running' ? 'processing' : 'default';
        const label = status === 'active' ? '活跃' : status === 'running' ? '运行中' : '已暂停';
        return <Badge status={color} text={<span className="text-slate-600">{label}</span>} />;
      },
    },
    {
      title: '操作',
      key: 'actions',
      width: 100,
      render: (_: unknown, record: TestSuite) => (
        <Space onClick={(e) => e.stopPropagation()}>
          <Button
            type="text"
            size="small"
            icon={<Play size={14} />}
            className="text-emerald-500 hover:text-emerald-700 hover:bg-emerald-50"
            title="立即运行"
          />
          <Button
            type="text"
            size="small"
            icon={<Trash2 size={14} />}
            className="text-slate-400 hover:text-red-500 hover:bg-red-50"
            onClick={(e) => handleDelete(e, record.id)}
            title="删除"
          />
        </Space>
      ),
    },
  ];

  // --- Modal Content ---

  const renderStepContent = () => {
    switch (currentStep) {
      case 0: // Basic Info
        return (
          <Form form={form} layout="vertical" className="mt-4">
            <Form.Item name="name" label="套件名称" rules={[{ required: true, message: '请输入套件名称' }]}>
              <Input placeholder="例如：每日回归测试" />
            </Form.Item>
            <Form.Item name="description" label="描述">
              <TextArea rows={4} placeholder="描述该套件的目的..." />
            </Form.Item>
          </Form>
        );
      case 1: // Select Cases
        return (
          <div className="mt-4 h-[300px]">
            <Transfer
              dataSource={MOCK_ALL_CASES}
              titles={['可选用例', '已选用例']}
              targetKeys={targetKeys}
              selectedKeys={selectedKeys}
              onChange={handleTransferChange}
              onSelectChange={handleSelectChange}
              render={(item) => item.title}
              listStyle={{
                width: 250,
                height: 300,
              }}
            />
          </div>
        );
      case 2: // Schedule
        return (
          <Form form={form} layout="vertical" className="mt-4">
            <Form.Item name="scheduleType" label="触发类型" initialValue="manual">
              <Select className="w-full">
                <Option value="manual">仅手动触发</Option>
                <Option value="scheduled">定时调度 (Cron)</Option>
              </Select>
            </Form.Item>

            <Form.Item
              noStyle
              shouldUpdate={(prev, current) => prev.scheduleType !== current.scheduleType}
            >
              {({ getFieldValue }) =>
                getFieldValue('scheduleType') === 'scheduled' && (
                  <Form.Item
                    name="cronExpression"
                    label="Cron 表达式"
                    rules={[{ required: true, message: '请输入 Cron 表达式' }]}
                    help="例如：'0 0 * * *' 表示每天午夜运行"
                  >
                    <Input prefix={<Clock size={16} className="text-slate-400" />} className="font-mono" placeholder="* * * * *" />
                  </Form.Item>
                )
              }
            </Form.Item>
          </Form>
        );
      default:
        return null;
    }
  };

  return (
    <div className="p-6 space-y-6 max-w-6xl mx-auto">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">测试套件编排</h1>
          <p className="text-slate-500">管理并调度自动化测试集合</p>
        </div>
        <Button
          type="primary"
          icon={<Plus size={16} />}
          onClick={handleCreate}
        >
          创建套件
        </Button>
      </div>

      <Card bordered={false} className="shadow-sm overflow-hidden" styles={{ body: { padding: 0 } }}>
        <Table
          columns={columns}
          dataSource={suites}
          rowKey="id"
          onRow={(record) => ({
            onClick: () => handleRowClick(record),
            className: 'cursor-pointer hover:bg-slate-50 transition-colors'
          })}
          pagination={false}
        />
      </Card>

      {/* Create Modal */}
      <Modal
        title="创建测试套件"
        open={isModalOpen}
        onCancel={handleCloseModal}
        footer={
          <div className="flex justify-between w-full">
            <Button disabled={currentStep === 0} onClick={handlePrev}>
              上一步
            </Button>
            {currentStep < 2 ? (
              <Button type="primary" onClick={handleNext}>
                下一步
              </Button>
            ) : (
              <Button type="primary" onClick={handleFinish} className="bg-emerald-600 hover:bg-emerald-500">
                完成
              </Button>
            )}
          </div>
        }
        width={700}
      >
        <Steps
          current={currentStep}
          size="small"
          className="mb-6"
          items={[
            { title: '基本信息' },
            { title: '选择用例' },
            { title: '调度设置' }
          ]}
        />
        <div className="py-4">
          {renderStepContent()}
        </div>
      </Modal>

      {/* Detail Drawer */}
      <Drawer
        title={<span className="text-slate-800">{selectedSuite?.name}</span>}
        placement="right"
        onClose={() => setIsDrawerOpen(false)}
        open={isDrawerOpen}
        width={500}
      >
        {selectedSuite && (
          <div className="space-y-6">
            <div className="flex justify-between items-center bg-slate-50 p-4 rounded-lg border border-slate-200">
              <Space direction="vertical" size={2}>
                <span className="text-xs text-slate-500 uppercase tracking-wider">状态</span>
                <Badge
                  status={selectedSuite.status === 'active' ? 'success' : 'default'}
                  text={<span className="text-slate-700 font-medium">{selectedSuite.status === 'active' ? '活跃' : '已暂停'}</span>}
                />
              </Space>
              <Button type="primary" icon={<Play size={16} />} className="bg-emerald-600 hover:bg-emerald-500 border-none">
                立即运行
              </Button>
            </div>

            <Descriptions column={1} layout="vertical" className="bg-white p-4 rounded-lg border border-slate-100">
              <Descriptions.Item label={<span className="text-slate-500">描述</span>}>
                <span className="text-slate-800">{selectedSuite.description}</span>
              </Descriptions.Item>
              <Descriptions.Item label={<span className="text-slate-500">调度计划</span>}>
                <span className="text-blue-600 font-mono">{selectedSuite.schedule}</span>
              </Descriptions.Item>
              <Descriptions.Item label={<span className="text-slate-500">上次运行时间</span>}>
                <span className="text-slate-800">{selectedSuite.lastRun}</span>
              </Descriptions.Item>
            </Descriptions>

            <div>
              <h4 className="text-sm font-bold text-slate-500 uppercase tracking-wider mb-3 flex items-center gap-2">
                <TestTube size={14} /> 包含的测试用例 ({selectedSuite.caseCount})
              </h4>
              <div className="border border-slate-200 rounded-lg overflow-hidden bg-white">
                {/* Mock list of cases in this suite */}
                {Array.from({ length: Math.min(5, selectedSuite.caseCount) }).map((_, i) => (
                  <div key={i} className="flex items-center justify-between p-3 border-b border-slate-100 last:border-0 hover:bg-slate-50">
                    <span className="text-slate-700 text-sm">测试用例 {i + 1}</span>
                    <Tag className="bg-slate-100 border-slate-200 text-slate-500 m-0">API</Tag>
                  </div>
                ))}
                {selectedSuite.caseCount > 5 && (
                  <div className="p-2 text-center text-xs text-slate-500 bg-slate-50 border-t border-slate-100">
                    还有 {selectedSuite.caseCount - 5} 条用例...
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </Drawer>
    </div>
  );
};
