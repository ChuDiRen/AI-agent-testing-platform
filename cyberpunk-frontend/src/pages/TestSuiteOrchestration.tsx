import React, { useState } from 'react';
import { Table, Button, Input, Select, Space, Badge, Modal, Form, Transfer, Steps, Drawer, Descriptions, Tag, message } from 'antd';
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
    description: '夜间构建的关键路径验证。',
    caseCount: 12,
    schedule: '0 2 * * *',
    status: 'active',
    lastRun: '2025-01-14 02:00:00'
  },
  {
    id: '2',
    name: '回归测试套件 - 每周',
    description: '完整的系统回归测试。',
    caseCount: 156,
    schedule: '0 0 * * 0',
    status: 'paused',
    lastRun: '2025-01-07 00:00:00'
  },
  {
    id: '3',
    name: '认证模块验证',
    description: '专注于认证流程的测试。',
    caseCount: 24,
    schedule: 'Manual',
    status: 'active',
    lastRun: '2025-01-13 15:30:00'
  }
];

const MOCK_ALL_CASES: TestCase[] = Array.from({ length: 20 }).map((_, i) => ({
  key: i.toString(),
  title: `测试用例 ${i + 1}`,
  description: `验证功能集 ${Math.floor(i / 5) + 1} 的功能`,
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
      // Validation failed
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
        schedule: values.scheduleType === 'manual' ? 'Manual' : values.cronExpression,
        status: 'active',
        lastRun: '-'
      };
      
      setSuites([...suites, newSuite]);
      message.success('Test Suite created successfully');
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
    message.success('Suite deleted');
  };

  // --- Renderers ---

  const columns = [
    {
      title: 'Name',
      dataIndex: 'name',
      key: 'name',
      render: (text: string) => <span className="font-medium text-slate-200">{text}</span>,
    },
    {
      title: 'Description',
      dataIndex: 'description',
      key: 'description',
      ellipsis: true,
      render: (text: string) => <span className="text-slate-400">{text}</span>,
    },
    {
      title: 'Cases',
      dataIndex: 'caseCount',
      key: 'caseCount',
      width: 100,
      render: (count: number) => (
        <Tag icon={<FileStack size={12} />} className="bg-slate-800 text-slate-300 border-slate-700">
          {count}
        </Tag>
      ),
    },
    {
      title: 'Schedule',
      dataIndex: 'schedule',
      key: 'schedule',
      width: 150,
      render: (text: string) => (
        <Space size={4}>
          {text === 'Manual' ? <Play size={14} className="text-slate-500" /> : <Clock size={14} className="text-neon-cyan" />}
          <span className="font-mono text-xs text-slate-400">{text}</span>
        </Space>
      ),
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      width: 120,
      render: (status: string) => {
        const color = status === 'active' ? 'success' : status === 'running' ? 'processing' : 'default';
        return <Badge status={color} text={<span className="capitalize text-slate-400">{status}</span>} />;
      },
    },
    {
      title: 'Actions',
      key: 'actions',
      width: 100,
      render: (_: unknown, record: TestSuite) => (
        <Space onClick={(e) => e.stopPropagation()}>
          <Button 
            type="text" 
            size="small" 
            icon={<Play size={14} />} 
            className="text-emerald-400 hover:text-emerald-300 hover:bg-emerald-500/10" 
            title="Run Now"
          />
          <Button 
            type="text" 
            size="small" 
            icon={<Trash2 size={14} />} 
            className="text-slate-500 hover:text-red-400 hover:bg-red-500/10" 
            onClick={(e) => handleDelete(e, record.id)}
            title="Delete"
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
            <Form.Item name="name" label="Suite Name" rules={[{ required: true, message: 'Please enter a suite name' }]}>
              <Input placeholder="e.g. Nightly Regression" className="bg-slate-900 border-slate-700" />
            </Form.Item>
            <Form.Item name="description" label="Description">
              <TextArea rows={4} placeholder="Describe the purpose of this suite..." className="bg-slate-900 border-slate-700" />
            </Form.Item>
          </Form>
        );
      case 1: // Select Cases
        return (
          <div className="mt-4 h-[300px]">
            <Transfer
              dataSource={MOCK_ALL_CASES}
              titles={['Available Cases', 'Selected Cases']}
              targetKeys={targetKeys}
              selectedKeys={selectedKeys}
              onChange={handleTransferChange}
              onSelectChange={handleSelectChange}
              render={(item) => item.title}
              listStyle={{
                width: 250,
                height: 300,
                backgroundColor: '#0f172a',
                borderColor: '#334155'
              }}
              className="cyberpunk-transfer"
            />
          </div>
        );
      case 2: // Schedule
        return (
          <Form form={form} layout="vertical" className="mt-4">
            <Form.Item name="scheduleType" label="Trigger Type" initialValue="manual">
              <Select className="w-full">
                <Option value="manual">Manual Trigger Only</Option>
                <Option value="scheduled">Scheduled (Cron)</Option>
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
                    label="Cron Expression" 
                    rules={[{ required: true, message: 'Please enter cron expression' }]}
                    help="e.g. '0 0 * * *' for daily at midnight"
                  >
                    <Input prefix={<Clock size={16} className="text-slate-500" />} className="font-mono bg-slate-900 border-slate-700" placeholder="* * * * *" />
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
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-slate-100">Test Suite Orchestration</h1>
          <p className="text-slate-400">Manage and schedule automated test collections</p>
        </div>
        <Button 
          type="primary" 
          icon={<Plus size={16} />} 
          onClick={handleCreate}
          className="bg-neon-cyan hover:bg-neon-cyan border-none h-10 px-6"
        >
          Create Suite
        </Button>
      </div>

      <Table
        columns={columns}
        dataSource={suites}
        rowKey="id"
        onRow={(record) => ({
          onClick: () => handleRowClick(record),
          className: 'cursor-pointer hover:bg-slate-800/50 transition-colors'
        })}
        className="cyberpunk-table"
        pagination={false}
      />

      {/* Create Modal */}
      <Modal
        title={<span className="text-slate-200">Create Test Suite</span>}
        open={isModalOpen}
        onCancel={handleCloseModal}
        footer={
          <div className="flex justify-between w-full">
             <Button disabled={currentStep === 0} onClick={handlePrev}>
               Previous
             </Button>
             {currentStep < 2 ? (
               <Button type="primary" onClick={handleNext} className="bg-neon-cyan">
                 Next
               </Button>
             ) : (
               <Button type="primary" onClick={handleFinish} className="bg-emerald-600 hover:bg-emerald-500">
                 Finish
               </Button>
             )}
          </div>
        }
        width={700}
        className="cyberpunk-modal"
      >
        <Steps 
          current={currentStep} 
          size="small" 
          className="mb-6"
          items={[
            { title: 'Basic Info' },
            { title: 'Select Cases' },
            { title: 'Schedule' }
          ]}
        />
        <div className="py-4">
          {renderStepContent()}
        </div>
      </Modal>

      {/* Detail Drawer */}
      <Drawer
        title={<span className="text-slate-200">{selectedSuite?.name}</span>}
        placement="right"
        onClose={() => setIsDrawerOpen(false)}
        open={isDrawerOpen}
        size={500}
        className="cyberpunk-drawer"
        styles={{ 
          body: { background: '#0f172a' },
          header: { background: '#1e293b', borderBottom: '1px solid #334155' }
        }}
      >
        {selectedSuite && (
          <div className="space-y-6">
            <div className="flex justify-between items-center bg-slate-800/50 p-4 rounded-lg border border-slate-700/50">
              <Space direction="vertical" size={2}>
                <span className="text-xs text-slate-500 uppercase tracking-wider">Status</span>
                <Badge 
                  status={selectedSuite.status === 'active' ? 'success' : 'default'} 
                  text={<span className="text-slate-200 font-medium capitalize">{selectedSuite.status}</span>} 
                />
              </Space>
              <Button type="primary" icon={<Play size={16} />} className="bg-emerald-600 border-none">
                Run Now
              </Button>
            </div>

            <Descriptions column={1} layout="vertical" className="bg-slate-800/30 p-4 rounded-lg">
              <Descriptions.Item label={<span className="text-slate-500">Description</span>}>
                <span className="text-slate-300">{selectedSuite.description}</span>
              </Descriptions.Item>
              <Descriptions.Item label={<span className="text-slate-500">Schedule</span>}>
                <span className="text-neon-cyan font-mono">{selectedSuite.schedule}</span>
              </Descriptions.Item>
              <Descriptions.Item label={<span className="text-slate-500">Last Run</span>}>
                <span className="text-slate-300">{selectedSuite.lastRun}</span>
              </Descriptions.Item>
            </Descriptions>

            <div>
              <h4 className="text-sm font-bold text-slate-400 uppercase tracking-wider mb-3 flex items-center gap-2">
                <TestTube size={14} /> Included Test Cases ({selectedSuite.caseCount})
              </h4>
              <div className="border border-slate-700 rounded-lg overflow-hidden">
                {/* Mock list of cases in this suite */}
                {Array.from({ length: Math.min(5, selectedSuite.caseCount) }).map((_, i) => (
                  <div key={i} className="flex items-center justify-between p-3 border-b border-slate-800 bg-slate-900/50 last:border-0">
                    <span className="text-slate-300 text-sm">Test Case {i + 1}</span>
                    <Tag className="bg-slate-800 border-slate-700 text-slate-500 m-0">API</Tag>
                  </div>
                ))}
                {selectedSuite.caseCount > 5 && (
                  <div className="p-2 text-center text-xs text-slate-500 bg-slate-800/30">
                    + {selectedSuite.caseCount - 5} more cases...
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

