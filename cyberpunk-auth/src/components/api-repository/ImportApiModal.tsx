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
          From URL
        </span>
      ),
      children: (
        <Form form={form} layout="vertical" className="mt-4">
          <Form.Item
            name="url"
            label="OpenAPI / Swagger Spec URL"
            rules={[{ required: true, message: 'Please enter the URL' }, { type: 'url', message: 'Please enter a valid URL' }]}
          >
            <Input 
              prefix={<Link size={16} className="text-slate-500" />} 
              placeholder="https://api.example.com/openapi.json" 
              className="bg-slate-900 border-slate-700"
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
          Upload File
        </span>
      ),
      children: (
        <div className="mt-4">
          <Upload.Dragger {...uploadProps} className="bg-slate-900/50 border-slate-700 hover:border-indigo-500">
            <p className="ant-upload-drag-icon flex justify-center text-indigo-500 mb-2">
              <UploadIcon size={32} />
            </p>
            <p className="ant-upload-text text-slate-300">Click or drag file to this area to upload</p>
            <p className="ant-upload-hint text-slate-500">
              Support for JSON or YAML OpenAPI specification files.
            </p>
          </Upload.Dragger>
        </div>
      ),
    },
  ];

  return (
    <Modal
      title="Import API Definition"
      open={open}
      onOk={handleOk}
      onCancel={onCancel}
      okText="Import"
      cancelButtonProps={{ className: 'text-slate-400 hover:text-slate-200' }}
      className="cyberpunk-modal"
      width={600}
    >
      <Tabs 
        activeKey={activeTab} 
        onChange={setActiveTab} 
        items={items} 
        className="text-slate-300"
      />
    </Modal>
  );
};
