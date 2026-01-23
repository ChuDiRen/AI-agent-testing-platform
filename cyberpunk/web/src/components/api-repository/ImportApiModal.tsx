import React, { useState } from 'react';
import { Modal, Tabs, Form, Input, Upload } from 'antd';
import { Link, Upload as UploadIcon, FileJson, Globe } from 'lucide-react';
import type { UploadProps } from 'antd';
import type { RcFile } from 'antd/es/upload';

interface ImportApiModalProps {
  open: boolean;
  onCancel: () => void;
  onImport: (values: ImportValues) => void;
}

interface ImportValues {
  url?: string;
  type: string;
  file?: RcFile;
}

export const ImportApiModal: React.FC<ImportApiModalProps> = ({ open, onCancel, onImport }) => {
  const [activeTab, setActiveTab] = useState('url');
  const [form] = Form.useForm();
  const [fileList, setFileList] = useState<UploadProps['fileList']>([]);

  const handleOk = async () => {
    try {
      const values = await form.validateFields();
      onImport({ ...values, type: activeTab, file: fileList?.[0] });
      form.resetFields();
      setFileList([]);
    } catch (error) {
      console.error('Validation failed:', error);
    }
  };

  const uploadProps: UploadProps = {
    onRemove: (file) => {
      const index = (fileList || []).indexOf(file);
      const newFileList = (fileList || []).slice();
      newFileList.splice(index, 1);
      setFileList(newFileList);
    },
    beforeUpload: (file) => {
      setFileList([file]);
      return false;
    },
    fileList: fileList || [],
    maxCount: 1,
  };

  const items = [
    {
      key: 'url',
      label: (
        <span className="flex items-center gap-2">
          <Globe size={16} />
          从 URL 导入
        </span>
      ),
      children: (
        <Form form={form} layout="vertical" className="mt-4">
          <Form.Item
            name="url"
            label="OpenAPI / Swagger 规范 URL"
            rules={[{ required: true, message: '请输入 URL' }, { type: 'url', message: '请输入有效的 URL' }]}
          >
            <Input
              prefix={<Link size={16} className="text-slate-400" />}
              placeholder="https://api.example.com/openapi.json"
            />
          </Form.Item>
        </Form>
      ),
    },
    {
      key: 'file',
      label: (
        <span className="flex items-center gap-2">
          <FileJson size={16} />
          上传文件
        </span>
      ),
      children: (
        <div className="mt-4">
          <Upload.Dragger {...uploadProps} className="hover:border-primary">
            <p className="ant-upload-drag-icon flex justify-center text-primary mb-2">
              <UploadIcon size={32} />
            </p>
            <p className="ant-upload-text text-slate-700">点击或拖拽文件到此区域上传</p>
            <p className="ant-upload-hint text-slate-500">
              支持 JSON 或 YAML 格式的 OpenAPI 规范文件。
            </p>
          </Upload.Dragger>
        </div>
      ),
    },
  ];

  return (
    <Modal
      title="导入 API 定义"
      open={open}
      onOk={handleOk}
      onCancel={onCancel}
      okText="导入"
    >
      <Tabs
        activeKey={activeTab}
        onChange={setActiveTab}
        items={items}
      />
    </Modal>
  );
};
