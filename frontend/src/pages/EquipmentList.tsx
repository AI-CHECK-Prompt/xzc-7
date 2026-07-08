import { useState, useEffect } from 'react';
import { Table, Button, Modal, Form, Input, Select, DatePicker, Space, message, Popconfirm } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, SearchOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import dayjs from 'dayjs';
import { equipmentApi } from '../api';
import type { Equipment } from '../types';

function EquipmentList() {
  const [data, setData] = useState<Equipment[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [departments, setDepartments] = useState<string[]>([]);
  const [searchKeyword, setSearchKeyword] = useState('');
  const [filters, setFilters] = useState({ department: '', status: '' });
  
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [form] = Form.useForm();
  const [editingId, setEditingId] = useState<string | null>(null);
  
  const navigate = useNavigate();

  const fetchData = async () => {
    try {
      const response = await equipmentApi.list({ page, page_size: pageSize, ...filters });
      setData(response.data.data);
      setTotal(response.data.total);
    } catch (error) {
      message.error('获取设备列表失败');
    }
  };

  const fetchDepartments = async () => {
    try {
      const response = await equipmentApi.departments();
      setDepartments(response.data);
    } catch (error) {
      console.error('获取科室列表失败');
    }
  };

  useEffect(() => {
    fetchData();
    fetchDepartments();
  }, [page, pageSize, filters]);

  const handleSearch = async () => {
    if (searchKeyword) {
      try {
        const response = await equipmentApi.search(searchKeyword);
        setData(response.data);
        setTotal(response.data.length);
      } catch (error) {
        message.error('搜索失败');
      }
    } else {
      fetchData();
    }
  };

  const handleAdd = () => {
    form.resetFields();
    setEditingId(null);
    setIsModalOpen(true);
  };

  const handleEdit = (record: Equipment) => {
    form.setFieldsValue({
      ...record,
      purchase_date: record.purchase_date ? dayjs(record.purchase_date) : null,
    });
    setEditingId(record._id || '');
    setIsModalOpen(true);
  };

  const handleDelete = async (id: string) => {
    try {
      await equipmentApi.delete(id);
      message.success('删除成功');
      fetchData();
    } catch (error) {
      message.error('删除失败');
    }
  };

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      const equipmentData: Equipment = {
        ...values,
        purchase_date: values.purchase_date ? values.purchase_date.toISOString() : '',
      };

      if (editingId) {
        await equipmentApi.update(editingId, equipmentData);
        message.success('更新成功');
      } else {
        await equipmentApi.create(equipmentData);
        message.success('创建成功');
      }
      setIsModalOpen(false);
      fetchData();
    } catch (error) {
      message.error('提交失败');
    }
  };

  const statusColors: Record<string, string> = {
    '正常': 'green',
    '故障': 'red',
    '维修中': 'orange',
    '停用': 'gray',
    '巡检中': 'blue',
  };

  const columns = [
    {
      title: '设备编号',
      dataIndex: 'equipment_code',
      key: 'equipment_code',
    },
    {
      title: '设备名称',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: '型号',
      dataIndex: 'model',
      key: 'model',
    },
    {
      title: '科室',
      dataIndex: 'department',
      key: 'department',
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => (
        <span style={{ color: statusColors[status] || 'black' }}>{status}</span>
      ),
    },
    {
      title: '采购日期',
      dataIndex: 'purchase_date',
      key: 'purchase_date',
      render: (date: string) => dayjs(date).format('YYYY-MM-DD'),
    },
    {
      title: '操作',
      key: 'action',
      render: (_: unknown, record: Equipment) => (
        <Space>
          <Button 
            type="link" 
            onClick={() => navigate(`/equipment/${record._id}`)}
          >
            详情
          </Button>
          <Button type="link" icon={<EditOutlined />} onClick={() => handleEdit(record)} />
          <Popconfirm
            title="确定删除此设备？"
            onConfirm={() => handleDelete(record._id || '')}
            okText="确定"
            cancelText="取消"
          >
            <Button type="link" danger icon={<DeleteOutlined />} />
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <Space style={{ marginBottom: 16 }}>
        <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
          新增设备
        </Button>
        <Input
          placeholder="搜索设备"
          prefix={<SearchOutlined />}
          value={searchKeyword}
          onChange={(e) => setSearchKeyword(e.target.value)}
          onPressEnter={handleSearch}
          style={{ width: 200 }}
        />
        <Select
          placeholder="选择科室"
          value={filters.department}
          onChange={(value) => setFilters({ ...filters, department: value })}
          style={{ width: 150 }}
          allowClear
        >
          {departments.map((dept) => (
            <Select.Option key={dept} value={dept}>
              {dept}
            </Select.Option>
          ))}
        </Select>
        <Select
          placeholder="选择状态"
          value={filters.status}
          onChange={(value) => setFilters({ ...filters, status: value })}
          style={{ width: 150 }}
          allowClear
        >
          <Select.Option value="正常">正常</Select.Option>
          <Select.Option value="故障">故障</Select.Option>
          <Select.Option value="维修中">维修中</Select.Option>
          <Select.Option value="停用">停用</Select.Option>
          <Select.Option value="巡检中">巡检中</Select.Option>
        </Select>
      </Space>

      <Table
        columns={columns}
        dataSource={data}
        rowKey="_id"
        pagination={{
          current: page,
          pageSize,
          total,
          onChange: (p, s) => {
            setPage(p);
            setPageSize(s);
          },
        }}
      />

      <Modal
        title={editingId ? '编辑设备' : '新增设备'}
        open={isModalOpen}
        onCancel={() => setIsModalOpen(false)}
        onOk={handleSubmit}
      >
        <Form form={form} layout="vertical">
          <Form.Item
            name="equipment_code"
            label="设备编号"
            rules={[{ required: true, message: '请输入设备编号' }]}
          >
            <Input disabled={!!editingId} />
          </Form.Item>
          <Form.Item
            name="name"
            label="设备名称"
            rules={[{ required: true, message: '请输入设备名称' }]}
          >
            <Input />
          </Form.Item>
          <Form.Item
            name="model"
            label="设备型号"
            rules={[{ required: true, message: '请输入设备型号' }]}
          >
            <Input />
          </Form.Item>
          <Form.Item
            name="manufacturer"
            label="生产厂家"
            rules={[{ required: true, message: '请输入生产厂家' }]}
          >
            <Input />
          </Form.Item>
          <Form.Item
            name="department"
            label="所属科室"
            rules={[{ required: true, message: '请选择科室' }]}
          >
            <Select>
              {departments.map((dept) => (
                <Select.Option key={dept} value={dept}>
                  {dept}
                </Select.Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item
            name="location"
            label="安装位置"
            rules={[{ required: true, message: '请输入安装位置' }]}
          >
            <Input />
          </Form.Item>
          <Form.Item
            name="purchase_date"
            label="采购日期"
            rules={[{ required: true, message: '请选择采购日期' }]}
          >
            <DatePicker style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item name="warranty_period" label="保修期(月)">
            <Input type="number" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}

export default EquipmentList;
