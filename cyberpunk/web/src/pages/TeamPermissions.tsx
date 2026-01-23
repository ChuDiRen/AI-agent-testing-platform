import React, { useState } from 'react';
import { Table, Avatar, Select, Button, Input, Modal, Typography, Tag, Dropdown, message, Card } from 'antd';
import {
  Users,
  UserPlus,
  MoreVertical,
  Mail,
  Shield,
  Clock,
  Trash2,
  Edit
} from 'lucide-react';
import dayjs from 'dayjs';
import relativeTime from 'dayjs/plugin/relativeTime';

dayjs.extend(relativeTime);

const { Title, Text } = Typography;
const { Option } = Select;

// --- Types ---
type Role = 'Admin' | 'Editor' | 'Viewer';

interface TeamMember {
  id: string;
  name: string;
  email: string;
  avatar: string;
  role: Role;
  lastActive: string; // ISO string
  status: 'active' | 'pending';
}

// --- Mock Data ---
const MOCK_MEMBERS: TeamMember[] = [
  {
    id: '1',
    name: '陈亚历克斯 (Alex Chen)',
    email: 'alex.chen@example.com',
    avatar: 'https://i.pravatar.cc/150?u=alex',
    role: 'Admin',
    lastActive: dayjs().subtract(5, 'minutes').toISOString(),
    status: 'active',
  },
  {
    id: '2',
    name: '莎拉·康纳 (Sarah Connor)',
    email: 'sarah.c@example.com',
    avatar: 'https://i.pravatar.cc/150?u=sarah',
    role: 'Editor',
    lastActive: dayjs().subtract(2, 'hours').toISOString(),
    status: 'active',
  },
  {
    id: '3',
    name: '约翰·多伊 (John Doe)',
    email: 'john.doe@example.com',
    avatar: 'https://i.pravatar.cc/150?u=john',
    role: 'Viewer',
    lastActive: dayjs().subtract(1, 'day').toISOString(),
    status: 'active',
  },
  {
    id: '4',
    name: '待入职用户 (Pending User)',
    email: 'new.guy@example.com',
    avatar: '',
    role: 'Viewer',
    lastActive: '',
    status: 'pending',
  },
];

const TeamPermissions: React.FC = () => {
  const [members, setMembers] = useState<TeamMember[]>(MOCK_MEMBERS);
  const [isInviteModalOpen, setIsInviteModalOpen] = useState(false);
  const [inviteEmail, setInviteEmail] = useState('');
  const [inviteRole, setInviteRole] = useState<Role>('Viewer');

  const handleRoleChange = (memberId: string, newRole: Role) => {
    setMembers(prev => prev.map(m => m.id === memberId ? { ...m, role: newRole } : m));
    message.success('角色更新成功');
  };

  const handleDeleteMember = (memberId: string) => {
    setMembers(prev => prev.filter(m => m.id !== memberId));
    message.success('成员已移除');
  };

  const handleInvite = () => {
    if (!inviteEmail) return;

    const newMember: TeamMember = {
      id: Date.now().toString(),
      name: inviteEmail.split('@')[0], // simplistic name derivation
      email: inviteEmail,
      avatar: '',
      role: inviteRole,
      lastActive: '',
      status: 'pending',
    };

    setMembers([...members, newMember]);
    setIsInviteModalOpen(false);
    setInviteEmail('');
    setInviteRole('Viewer');
    message.success(`邀请邮件已发送至 ${inviteEmail}`);
  };

  const columns = [
    {
      title: '用户信息',
      key: 'user',
      render: (_: unknown, record: TeamMember) => (
        <div className="flex items-center gap-3">
          <Avatar src={record.avatar || undefined} icon={!record.avatar && <Users size={16} />} className="bg-slate-200 text-slate-500" />
          <div className="flex flex-col">
            <span className="text-slate-800 font-medium">
              {record.name}
              {record.status === 'pending' && <Tag className="ml-2 text-[10px] bg-slate-100 border-slate-200 text-slate-500">待处理</Tag>}
            </span>
            <span className="text-slate-500 text-xs">{record.email}</span>
          </div>
        </div>
      ),
    },
    {
      title: '角色',
      key: 'role',
      render: (_: unknown, record: TeamMember) => (
        <Select
          defaultValue={record.role}
          style={{ width: 120 }}
          onChange={(value) => handleRoleChange(record.id, value)}
          variant="borderless"
          className="bg-transparent hover:bg-slate-100 rounded transition-colors"
        >
          <Option value="Admin">
            <Tag color="purple" className="mr-0">管理员</Tag>
          </Option>
          <Option value="Editor">
            <Tag color="blue" className="mr-0">编辑器</Tag>
          </Option>
          <Option value="Viewer">
            <Tag color="default" className="mr-0">观察者</Tag>
          </Option>
        </Select>
      ),
    },
    {
      title: '最后活跃',
      dataIndex: 'lastActive',
      key: 'lastActive',
      render: (text: string, record: TeamMember) => (
        <div className="flex items-center gap-2 text-slate-500 text-sm">
          <Clock size={14} />
          {record.status === 'pending' ? '尚未加入' : dayjs(text).fromNow()}
        </div>
      ),
    },
    {
      title: '操作',
      key: 'actions',
      render: (_: unknown, record: TeamMember) => (
        <Dropdown
          menu={{
            items: [
              { key: 'edit', label: '编辑资料', icon: <Edit size={14} /> },
              { type: 'divider' },
              { key: 'delete', label: '移除成员', icon: <Trash2 size={14} />, danger: true, onClick: () => handleDeleteMember(record.id) },
            ],
          }}
          trigger={['click']}
        >
          <Button type="text" icon={<MoreVertical size={16} />} className="text-slate-400 hover:text-slate-600" />
        </Dropdown>
      ),
    },
  ];

  return (
    <div className="animate-fade-in space-y-6 max-w-7xl mx-auto p-6">
      <div className="flex justify-between items-center mb-6">
        <div>
          <Title level={2} className="!text-slate-900 !mb-1 flex items-center gap-3 tracking-tight">
            <Users className="text-blue-600" />
            团队与权限管理
          </Title>
          <Text className="text-slate-500">管理您的团队成员及其访问级别。</Text>
        </div>
        <Button
          type="primary"
          icon={<UserPlus size={16} />}
          className="bg-blue-600 hover:bg-blue-500 border-none h-10 px-6"
          onClick={() => setIsInviteModalOpen(true)}
        >
          邀请成员
        </Button>
      </div>

      <Card bordered={false} className="shadow-sm overflow-hidden" styles={{ body: { padding: 0 } }}>
        <Table
          dataSource={members}
          columns={columns}
          rowKey="id"
          pagination={false}
          className="ant-table-clean"
        />
      </Card>

      <Modal
        title="邀请新成员"
        open={isInviteModalOpen}
        onOk={handleInvite}
        onCancel={() => setIsInviteModalOpen(false)}
        okText="发送邀请"
        cancelText="取消"
      >
        <div className="space-y-4 mt-4">
          <div>
            <label className="text-slate-600 text-sm mb-1 block font-medium">邮箱地址</label>
            <Input
              prefix={<Mail size={16} className="text-slate-400" />}
              placeholder="colleague@example.com"
              value={inviteEmail}
              onChange={(e) => setInviteEmail(e.target.value)}
            />
          </div>
          <div>
            <label className="text-slate-600 text-sm mb-1 block font-medium">角色</label>
            <Select
              value={inviteRole}
              onChange={setInviteRole}
              className="w-full"
            >
              <Option value="Admin">
                <div className="flex items-center gap-2">
                  <Shield size={14} className="text-purple-600" />
                  <span>管理员 (完全访问权限)</span>
                </div>
              </Option>
              <Option value="Editor">
                <div className="flex items-center gap-2">
                  <Edit size={14} className="text-blue-600" />
                  <span>编辑器 (可编辑资源)</span>
                </div>
              </Option>
              <Option value="Viewer">
                <div className="flex items-center gap-2">
                  <Users size={14} className="text-slate-400" />
                  <span>观察者 (只读)</span>
                </div>
              </Option>
            </Select>
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default TeamPermissions;
