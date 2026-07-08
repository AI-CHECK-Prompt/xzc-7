import { useState, useEffect } from 'react';
import { Table, Button, Modal, Form, Input, Select, Space, message, Popconfirm, Tag } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons';
import dayjs from 'dayjs';
import { repairApi, equipmentApi } from '../api';
import type { RepairOrder, Equipment } from '../types';

function RepairOrderPage() {
  const [orders, setOrders] = useState<RepairOrder[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [equipmentList, setEquipmentList] = useState<Equipment[]>([]);
  const [filters, setFilters] = useState({ status: '', priority: '' });
  
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [form] = Form.useForm();
  const [editingId, setEditingId] = useState<string | null>(null);

  const fetchOrders = async () => {
    try {
      const response = await repairApi.list({ page, page_size: pageSize, ...filters });
      setOrders(response.data.data);
      setTotal(response.data.total);
    } catch (error) {
      message.error('获取报修单失败');
    }
  };

  const fetchEquipment = async () => {
    try {
      const response = await equipmentApi.list({ page_size: 100 });
      setEquipmentList(response.data.data);
    } catch (error) {
      console.error('获取设备列表失败');
    }
  };

  useEffect(() => {
    fetchOrders();
    fetchEquipment();
  }, [page, pageSize, filters]);

  const handleAdd = () => {
    form.resetFields();
    setEditingId(null);
    setIsModalOpen(true);
  };

  const handleEdit = (record: RepairOrder) => {
    form.setFieldsValue(record);
    setEditingId(record._id || '');
    setIsModalOpen(true);
  };

  const handleDelete = async (id: string) => {
    try {
      await repairApi.delete(id);
      message.success('删除成功');
      fetchOrders();
    } catch (error) {
      message.error('删除失败');
    }
  };

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      
      const equipment = equipmentList.find(eq => eq.equipment_code === values.equipment_code);
      
      const orderData: RepairOrder = {
        ...values,
        equipment_name: equipment?.name || '',
      };

      if (editingId) {
        await repairApi.update(editingId, orderData);
        message.success('更新成功');
      } else {
        await repairApi.create(orderData);
        message.success('创建成功');
      }
      setIsModalOpen(false);
      fetchOrders();
    } catch (error) {
      message.error('提交失败');
    }
  };

  const statusMap: Record<string, string> = {
    '待处理': 'warning',
    '已接单': 'info',
    '维修中': 'processing',
    '已完成': 'success',
    '已取消': 'default',
  };

  const priorityColors: Record<string, string> = {
    '紧急': 'red',
    '重要': 'orange',
    '一般': 'blue',
  };

  const columns = [
    {
      title: '报修单号',
      dataIndex: '_id',
      key: '_id',
      render: (id: string) => id.substring(0, 8) + '...',
    },
    {
      title: '设备编号',
      dataIndex: 'equipment_code',
      key: 'equipment_code',
    },
    {
      title: '设备名称',
      dataIndex: 'equipment_name',
      key: 'equipment_name',
    },
    {
      title: '报修人',
      dataIndex: 'reporter',
      key: 'reporter',
    },
    {
      title: '科室',
      dataIndex: 'department',
      key: 'department',
    },
    {
      title: '优先级',
      dataIndex: 'priority',
      key: 'priority',
      render: (priority: string) => (
        <Tag color={priorityColors[priority]}>{priority}</Tag>
      ),
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => (
        <Tag color={statusMap[status]}>{status}</Tag>
      ),
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date: string) => dayjs(date).format('YYYY-MM-DD HH:mm'),
    },
    {
      title: '操作',
      key: 'action',
      render: (_: unknown, record: RepairOrder) => (
        <Space>
          <Button type="link" icon={<EditOutlined />} onClick={() => handleEdit(record)} />
          <Popconfirm
            title="确定删除此报修单？"
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
          新建报修单
        </Button>
        <Select
          placeholder="选择状态"
          value={filters.status}
          onChange={(value) => setFilters({ ...filters, status: value })}
          style={{ width: 150 }}
          allowClear
        >
          <Select.Option value="待处理">待处理</Select.Option>
          <Select.Option value="已接单">已接单</Select.Option>
          <Select.Option value="维修中">维修中</Select.Option>
          <Select.Option value="已完成">已完成</Select.Option>
          <Select.Option value="已取消">已取消</Select.Option>
        </Select>
        <Select
          placeholder="选择优先级"
          value={filters.priority}
          onChange={(value) => setFilters({ ...filters, priority: value })}
          style={{ width: 150 }}
          allowClear
        >
          <Select.Option value="紧急">紧急</Select.Option>
          <Select.Option value="重要">重要</Select.Option>
          <Select.Option value="一般">一般</Select.Option>
        </Select>
      </Space>

      <Table
        columns={columns}
        dataSource={orders}
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
        title={editingId ? '编辑报修单' : '新建报修单'}
        open={isModalOpen}
        onCancel={() => setIsModalOpen(false)}
        onOk={handleSubmit}
        width={600}
      >
        <Form form={form} layout="vertical">
          <Form.Item
            name="equipment_code"
            label="设备编号"
            rules={[{ required: true, message: '请选择设备' }]}
          >
            <Select>
              {equipmentList.map((eq) => (
                <Select.Option key={eq.equipment_code} value={eq.equipment_code}>
                  {eq.equipment_code} - {eq.name} ({eq.department})
                </Select.Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item
            name="reporter"
            label="报修人"
            rules={[{ required: true, message: '请输入报修人' }]}
          >
            <Input />
          </Form.Item>
          <Form.Item
            name="department"
            label="报修科室"
            rules={[{ required: true, message: '请输入报修科室' }]}
          >
            <Input />
          </Form.Item>
          <Form.Item
            name="description"
            label="故障描述"
            rules={[{ required: true, message: '请输入故障描述' }]}
          >
            <Input.TextArea rows={4} />
          </Form.Item>
          <Form.Item
            name="priority"
            label="优先级"
            rules={[{ required: true, message: '请选择优先级' }]}
          >
            <Select defaultValue="一般">
              <Select.Option value="紧急">紧急</Select.Option>
              <Select.Option value="重要">重要</Select.Option>
              <Select.Option value="一般">一般</Select.Option>
            </Select>
          </Form.Item>
          <Form.Item name="status" label="状态">
            <Select>
              <Select.Option value="待处理">待处理</Select.Option>
              <Select.Option value="已接单">已接单</Select.Option>
              <Select.Option value="维修中">维修中</Select.Option>
              <Select.Option value="已完成">已完成</Select.Option>
              <Select.Option value="已取消">已取消</Select.Option>
            </Select>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}

export default RepairOrderPage;
