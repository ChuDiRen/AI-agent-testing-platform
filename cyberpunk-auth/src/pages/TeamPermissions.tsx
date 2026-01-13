import React, { useState } from 'react';
import { Table, Avatar, Select, Button, Input, Modal, Typography, Tag, Dropdown, message } from 'antd';
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
type Role = '管理员' | '编辑者' | '查看者';

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
    name: 'Alex Chen',
    email: 'alex.chen@cyberpunk.io',
    avatar: 'https://i.pravatar.cc/150?u=alex',
    role: '管理员',
    lastActive: dayjs().subtract(5, 'minutes').toISOString(),
    status: 'active',
  },
  {
    id: '2',
    name: 'Sarah Connor',
    email: 'sarah.c@cyberpunk.io',
    avatar: 'https://i.pravatar.cc/150?u=sarah',
    role: '编辑者',
    lastActive: dayjs().subtract(2, 'hours').toISOString(),
    status: 'active',
  },
  {
    id: '3',
    name: 'John Doe',
    email: 'john.doe@cyberpunk.io',
    avatar: 'https://i.pravatar.cc/150?u=john',
    role: '查看者',
    lastActive: dayjs().subtract(1, 'day').toISOString(),
    status: 'active',
  },
  {
    id: '4',
    name: 'Pending User',
    email: 'new.guy@cyberpunk.io',
    avatar: '',
    role: '查看者',
    lastActive: '',
    status: 'pending',
  },
];

const TeamPermissions: React.FC = () => {
  const [members, setMembers] = useState<TeamMember[]>(MOCK_MEMBERS);
  const [isInviteModalOpen, setIsInviteModalOpen] = useState(false);
  const [inviteEmail, setInviteEmail] = useState('');
  const [inviteRole, setInviteRole] = useState<Role>('查看者');

  const handleRoleChange = (memberId: string, newRole: Role) => {
    setMembers(prev => prev.map(m => m.id === memberId ? { ...m, role: newRole } : m));
    message.success('Role updated successfully');
  };

  const handleDeleteMember = (memberId: string) => {
    setMembers(prev => prev.filter(m => m.id !== memberId));
    message.success('Member removed');
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
    message.success(`Invitation sent to ${inviteEmail}`);
  };

  const columns = [
    {
      title: 'User Info',
      key: 'user',
      render: (_: unknown, record: TeamMember) => (
        <div className="flex items-center gap-3">
          <Avatar src={record.avatar} icon={!record.avatar && <Users size={16} />} className="bg-slate-700" />
          <div className="flex flex-col">
            <span className="text-slate-200 font-medium">
              {record.name}
              {record.status === 'pending' && <Tag className="ml-2 text-[10px] bg-slate-800 border-slate-700 text-slate-400">Pending</Tag>}
            </span>
            <span className="text-slate-500 text-xs">{record.email}</span>
          </div>
        </div>
      ),
    },
    {
      title: 'Role',
      key: 'role',
      render: (_: unknown, record: TeamMember) => (
        <Select
          defaultValue={record.role}
          style={{ width: 120 }}
          onChange={(value) => handleRoleChange(record.id, value)}
          bordered={false}
          className="bg-transparent hover:bg-slate-800/50 rounded transition-colors"
          dropdownStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155' }}
        >
          <Option value="Admin">
            <Tag color="purple" className="mr-0">Admin</Tag>
          </Option>
          <Option value="Editor">
            <Tag color="blue" className="mr-0">Editor</Tag>
          </Option>
          <Option value="Viewer">
            <Tag color="default" className="mr-0">Viewer</Tag>
          </Option>
        </Select>
      ),
    },
    {
      title: 'Last Active',
      dataIndex: 'lastActive',
      key: 'lastActive',
      render: (text: string, record: TeamMember) => (
        <div className="flex items-center gap-2 text-slate-400 text-sm">
          <Clock size={14} />
          {record.status === 'pending' ? 'Not joined yet' : dayjs(text).fromNow()}
        </div>
      ),
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_: unknown, record: TeamMember) => (
        <Dropdown
          menu={{
            items: [
              { key: 'edit', label: 'Edit Profile', icon: <Edit size={14} /> },
              { type: 'divider' },
              { key: 'delete', label: 'Remove Member', icon: <Trash2 size={14} />, danger: true, onClick: () => handleDeleteMember(record.id) },
            ],
          }}
          trigger={['click']}
        >
          <Button type="text" icon={<MoreVertical size={16} />} className="text-slate-500 hover:text-white" />
        </Dropdown>
      ),
    },
  ];

  return (
    <div className="animate-fade-in space-y-6">
      <div className="flex justify-between items-center mb-6">
        <div>
          <Title level={2} className="!text-slate-100 !mb-1 flex items-center gap-3">
            <Users className="text-indigo-400" />
            Team & Permissions
          </Title>
          <Text className="text-slate-400">Manage your team members and their access levels.</Text>
        </div>
        <Button 
          type="primary" 
          icon={<UserPlus size={16} />} 
          className="bg-indigo-600 hover:bg-indigo-500 border-none h-10 px-6"
          onClick={() => setIsInviteModalOpen(true)}
        >
          Invite Member
        </Button>
      </div>

      <div className="bg-slate-900/50 rounded-xl border border-slate-800 backdrop-blur-sm overflow-hidden">
        <Table 
          dataSource={members} 
          columns={columns} 
          rowKey="id"
          pagination={false}
          className="cyberpunk-table"
        />
      </div>

      <Modal
        title="Invite New Member"
        open={isInviteModalOpen}
        onOk={handleInvite}
        onCancel={() => setIsInviteModalOpen(false)}
        okText="Send Invitation"
        className="cyberpunk-modal"
      >
        <div className="space-y-4 mt-4">
          <div>
            <label className="text-slate-400 text-sm mb-1 block">Email Address</label>
            <Input 
              prefix={<Mail size={16} className="text-slate-500" />}
              placeholder="colleague@cyberpunk.io" 
              value={inviteEmail}
              onChange={(e) => setInviteEmail(e.target.value)}
              className="bg-slate-950 border-slate-700 text-slate-200"
            />
          </div>
          <div>
            <label className="text-slate-400 text-sm mb-1 block">Role</label>
            <Select 
              value={inviteRole} 
              onChange={setInviteRole} 
              className="w-full"
              dropdownStyle={{ backgroundColor: '#0f172a', border: '1px solid #1e293b' }}
            >
               <Option value="Admin">
                 <div className="flex items-center gap-2">
                   <Shield size={14} className="text-purple-400" />
                   <span>Admin (Full Access)</span>
                 </div>
               </Option>
               <Option value="Editor">
                 <div className="flex items-center gap-2">
                   <Edit size={14} className="text-blue-400" />
                   <span>Editor (Can edit resources)</span>
                 </div>
               </Option>
               <Option value="Viewer">
                 <div className="flex items-center gap-2">
                   <Users size={14} className="text-slate-400" />
                   <span>Viewer (Read-only)</span>
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
