import { useState, useEffect } from 'react';
import { Table, Button, Modal, Form, Input, Select, DatePicker, Space, message, Popconfirm, Tabs } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons';
import dayjs from 'dayjs';
import { inspectionApi, equipmentApi } from '../api';
import type { InspectionPlan, Equipment } from '../types';

function InspectionPlanPage() {
  const [plans, setPlans] = useState<InspectionPlan[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [equipmentList, setEquipmentList] = useState<Equipment[]>([]);
  
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [form] = Form.useForm();
  const [editingId, setEditingId] = useState<string | null>(null);

  const fetchPlans = async () => {
    try {
      const response = await inspectionApi.listPlans({ page, page_size: pageSize });
      setPlans(response.data.data);
      setTotal(response.data.total);
    } catch (error) {
      message.error('获取巡检计划失败');
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
    fetchPlans();
    fetchEquipment();
  }, [page, pageSize]);

  const handleAdd = () => {
    form.resetFields();
    setEditingId(null);
    setIsModalOpen(true);
  };

  const handleEdit = (record: InspectionPlan) => {
    form.setFieldsValue({
      ...record,
      start_date: record.start_date ? dayjs(record.start_date) : null,
      end_date: record.end_date ? dayjs(record.end_date) : null,
    });
    setEditingId(record._id || '');
    setIsModalOpen(true);
  };

  const handleDelete = async (id: string) => {
    try {
      await inspectionApi.deletePlan(id);
      message.success('删除成功');
      fetchPlans();
    } catch (error) {
      message.error('删除失败');
    }
  };

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      
      if (values.start_date && values.end_date && values.end_date.isBefore(values.start_date)) {
        message.error('结束日期必须晚于开始日期');
        return;
      }

      const planData: InspectionPlan = {
        ...values,
        start_date: values.start_date ? values.start_date.toISOString() : '',
        end_date: values.end_date ? values.end_date.toISOString() : '',
      };

      if (editingId) {
        await inspectionApi.updatePlan(editingId, planData);
        message.success('更新成功');
      } else {
        await inspectionApi.createPlan(planData);
        message.success('创建成功');
      }
      setIsModalOpen(false);
      fetchPlans();
    } catch (error: any) {
      const errorMessage = error?.response?.data?.detail || error?.message || '提交失败';
      message.error(errorMessage);
    }
  };

  const statusColors: Record<string, string> = {
    '待执行': 'blue',
    '执行中': 'orange',
    '已完成': 'green',
    '已取消': 'gray',
  };

  const frequencyMap: Record<string, string> = {
    '每日': 'day',
    '每周': 'week',
    '每月': 'month',
    '每季度': 'quarter',
    '每年': 'year',
  };

  const planColumns = [
    {
      title: '计划名称',
      dataIndex: 'plan_name',
      key: 'plan_name',
    },
    {
      title: '关联设备数',
      dataIndex: 'equipment_codes',
      key: 'equipment_codes',
      render: (codes: string[]) => codes.length,
    },
    {
      title: '巡检频率',
      dataIndex: 'frequency',
      key: 'frequency',
    },
    {
      title: '负责人',
      dataIndex: 'assignee',
      key: 'assignee',
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => (
        <span style={{ color: statusColors[status] }}>{status}</span>
      ),
    },
    {
      title: '开始日期',
      dataIndex: 'start_date',
      key: 'start_date',
      render: (date: string) => dayjs(date).format('YYYY-MM-DD'),
    },
    {
      title: '结束日期',
      dataIndex: 'end_date',
      key: 'end_date',
      render: (date: string) => dayjs(date).format('YYYY-MM-DD'),
    },
    {
      title: '操作',
      key: 'action',
      render: (_: unknown, record: InspectionPlan) => (
        <Space>
          <Button type="link" icon={<EditOutlined />} onClick={() => handleEdit(record)} />
          <Popconfirm
            title="确定删除此计划？"
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
      <Tabs defaultActiveKey="plan">
        <Tabs.TabPane tab="巡检计划" key="plan">
          <Space style={{ marginBottom: 16 }}>
            <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
              新增计划
            </Button>
          </Space>

          <Table
            columns={planColumns}
            dataSource={plans}
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
        </Tabs.TabPane>
      </Tabs>

      <Modal
        title={editingId ? '编辑巡检计划' : '新增巡检计划'}
        open={isModalOpen}
        onCancel={() => setIsModalOpen(false)}
        onOk={handleSubmit}
        width={600}
      >
        <Form form={form} layout="vertical">
          <Form.Item
            name="plan_name"
            label="计划名称"
            rules={[{ required: true, message: '请输入计划名称' }]}
          >
            <Input />
          </Form.Item>
          <Form.Item
            name="equipment_codes"
            label="关联设备"
            rules={[{ required: true, message: '请选择关联设备' }]}
          >
            <Select mode="multiple" style={{ width: '100%' }}>
              {equipmentList.map((eq) => (
                <Select.Option key={eq.equipment_code} value={eq.equipment_code}>
                  {eq.equipment_code} - {eq.name}
                </Select.Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item
            name="frequency"
            label="巡检频率"
            rules={[{ required: true, message: '请选择巡检频率' }]}
          >
            <Select>
              {Object.keys(frequencyMap).map((key) => (
                <Select.Option key={key} value={key}>
                  {key}
                </Select.Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item
            name="start_date"
            label="开始日期"
            rules={[{ required: true, message: '请选择开始日期' }]}
          >
            <DatePicker style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item
            name="end_date"
            label="结束日期"
            rules={[{ required: true, message: '请选择结束日期' }]}
          >
            <DatePicker style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item
            name="assignee"
            label="负责人"
            rules={[{ required: true, message: '请输入负责人' }]}
          >
            <Input />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}

export default InspectionPlanPage;
