import { useState, useEffect } from 'react';
import { Table, Button, Modal, Form, Input, Select, DatePicker, Space, message, Popconfirm, Tabs, Row, Col } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, CheckCircleOutlined, ClockCircleOutlined, ExclamationCircleOutlined } from '@ant-design/icons';
import dayjs from 'dayjs';
import { maintenanceApi, equipmentApi } from '../api';
import type { MaintenanceCycle, MaintenancePlan, MaintenanceTask, MaintenanceReminder, Equipment } from '../types';

function MaintenancePlanPage() {
  const [cycles, setCycles] = useState<MaintenanceCycle[]>([]);
  const [plans, setPlans] = useState<MaintenancePlan[]>([]);
  const [tasks, setTasks] = useState<MaintenanceTask[]>([]);
  const [reminders, setReminders] = useState<MaintenanceReminder[]>([]);
  const [equipmentList, setEquipmentList] = useState<Equipment[]>([]);
  
  const [cycleTotal, setCycleTotal] = useState(0);
  const [planTotal, setPlanTotal] = useState(0);
  const [taskTotal, setTaskTotal] = useState(0);
  const [reminderTotal, setReminderTotal] = useState(0);
  
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  
  const [cycleModalOpen, setCycleModalOpen] = useState(false);
  const [planModalOpen, setPlanModalOpen] = useState(false);
  const [taskModalOpen, setTaskModalOpen] = useState(false);
  
  const [cycleForm] = Form.useForm();
  const [planForm] = Form.useForm();
  const [taskForm] = Form.useForm();
  
  const [editingCycleId, setEditingCycleId] = useState<string | null>(null);
  const [editingPlanId, setEditingPlanId] = useState<string | null>(null);
  const [editingTaskId, setEditingTaskId] = useState<string | null>(null);

  const fetchCycles = async () => {
    try {
      const response = await maintenanceApi.listCycles({ page, page_size: pageSize });
      setCycles(response.data.data);
      setCycleTotal(response.data.total);
    } catch (error) {
      message.error('获取维保周期配置失败');
    }
  };

  const fetchPlans = async () => {
    try {
      const response = await maintenanceApi.listPlans({ page, page_size: pageSize });
      setPlans(response.data.data);
      setPlanTotal(response.data.total);
    } catch (error) {
      message.error('获取维保计划失败');
    }
  };

  const fetchTasks = async () => {
    try {
      const response = await maintenanceApi.listTasks({ page, page_size: pageSize });
      setTasks(response.data.data);
      setTaskTotal(response.data.total);
    } catch (error) {
      message.error('获取维保任务失败');
    }
  };

  const fetchReminders = async () => {
    try {
      const response = await maintenanceApi.listReminders({ page, page_size: pageSize });
      setReminders(response.data.data);
      setReminderTotal(response.data.total);
    } catch (error) {
      message.error('获取维保提醒失败');
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
    fetchCycles();
    fetchPlans();
    fetchTasks();
    fetchReminders();
    fetchEquipment();
  }, [page, pageSize]);

  const handleAddCycle = () => {
    cycleForm.resetFields();
    setEditingCycleId(null);
    setCycleModalOpen(true);
  };

  const handleEditCycle = (record: MaintenanceCycle) => {
    cycleForm.setFieldsValue(record);
    setEditingCycleId(record._id || '');
    setCycleModalOpen(true);
  };

  const handleDeleteCycle = async (id: string) => {
    try {
      await maintenanceApi.deleteCycle(id);
      message.success('删除成功');
      fetchCycles();
    } catch (error) {
      message.error('删除失败');
    }
  };

  const handleSubmitCycle = async () => {
    try {
      const values = await cycleForm.validateFields();
      const cycleData: MaintenanceCycle = { ...values };

      if (editingCycleId) {
        await maintenanceApi.updateCycle(editingCycleId, cycleData);
        message.success('更新成功');
      } else {
        await maintenanceApi.createCycle(cycleData);
        message.success('创建成功');
      }
      setCycleModalOpen(false);
      fetchCycles();
    } catch (error) {
      message.error('提交失败');
    }
  };

  const handleAddPlan = () => {
    planForm.resetFields();
    setEditingPlanId(null);
    setPlanModalOpen(true);
  };

  const handleEditPlan = (record: MaintenancePlan) => {
    planForm.setFieldsValue({
      ...record,
      start_date: record.start_date ? dayjs(record.start_date) : null,
      end_date: record.end_date ? dayjs(record.end_date) : null,
    });
    setEditingPlanId(record._id || '');
    setPlanModalOpen(true);
  };

  const handleDeletePlan = async (id: string) => {
    try {
      await maintenanceApi.deletePlan(id);
      message.success('删除成功');
      fetchPlans();
      fetchTasks();
    } catch (error) {
      message.error('删除失败');
    }
  };

  const handleSubmitPlan = async () => {
    try {
      const values = await planForm.validateFields();
      const planData: MaintenancePlan = {
        ...values,
        start_date: values.start_date ? values.start_date.toISOString() : '',
        end_date: values.end_date ? values.end_date.toISOString() : '',
      };

      if (editingPlanId) {
        await maintenanceApi.updatePlan(editingPlanId, planData);
        message.success('更新成功');
      } else {
        await maintenanceApi.createPlan(planData);
        message.success('创建成功');
      }
      setPlanModalOpen(false);
      fetchPlans();
      fetchTasks();
    } catch (error) {
      message.error('提交失败');
    }
  };

  const handleEditTask = (record: MaintenanceTask) => {
    taskForm.setFieldsValue({
      ...record,
      scheduled_date: record.scheduled_date ? dayjs(record.scheduled_date) : null,
    });
    setEditingTaskId(record._id || '');
    setTaskModalOpen(true);
  };

  const handleSubmitTask = async () => {
    try {
      const values = await taskForm.validateFields();
      const taskData: Partial<MaintenanceTask> = {
        ...values,
        scheduled_date: values.scheduled_date ? values.scheduled_date.toISOString() : undefined,
      };

      await maintenanceApi.updateTask(editingTaskId || '', taskData);
      message.success('更新成功');
      setTaskModalOpen(false);
      fetchTasks();
    } catch (error) {
      message.error('提交失败');
    }
  };

  const handleCompleteTask = async (id: string) => {
    try {
      await maintenanceApi.updateTask(id, { status: '已完成', actual_date: new Date().toISOString() });
      message.success('任务已完成');
      fetchTasks();
    } catch (error) {
      message.error('操作失败');
    }
  };

  const handleGenerateReminders = async () => {
    try {
      await maintenanceApi.generateReminders();
      message.success('维保提醒生成成功');
      fetchReminders();
    } catch (error) {
      message.error('生成提醒失败');
    }
  };

  const handleProcessReminder = async (id: string) => {
    try {
      await maintenanceApi.handleReminder(id, { reminder_status: '已处理' });
      message.success('提醒已处理');
      fetchReminders();
    } catch (error) {
      message.error('操作失败');
    }
  };

  const cycleTypeMap: Record<string, string> = {
    '每日': 'day',
    '每周': 'week',
    '每月': 'month',
    '每季度': 'quarter',
    '每年': 'year',
  };

  const statusColors: Record<string, string> = {
    '待执行': 'blue',
    '执行中': 'orange',
    '已完成': 'green',
    '已取消': 'gray',
    '逾期': 'red',
    '启用': 'green',
    '停用': 'gray',
    '未处理': 'red',
    '已处理': 'green',
    '已过期': 'orange',
  };

  const cycleColumns = [
    { title: '周期名称', dataIndex: 'cycle_name', key: 'cycle_name' },
    { title: '设备编号', dataIndex: 'equipment_code', key: 'equipment_code' },
    { title: '周期类型', dataIndex: 'cycle_type', key: 'cycle_type' },
    { title: '间隔天数', dataIndex: 'interval_days', key: 'interval_days' },
    { title: '提前提醒', dataIndex: 'reminder_days', key: 'reminder_days', render: (days: number) => `${days}天` },
    { title: '状态', dataIndex: 'status', key: 'status', render: (status: string) => (<span style={{ color: statusColors[status] }}>{status}</span>) },
    { title: '操作', key: 'action', render: (_: unknown, record: MaintenanceCycle) => (<Space><Button type="link" icon={<EditOutlined />} onClick={() => handleEditCycle(record)} /><Popconfirm title="确定删除此周期配置？" onConfirm={() => handleDeleteCycle(record._id || '')} okText="确定" cancelText="取消"><Button type="link" danger icon={<DeleteOutlined />} /></Popconfirm></Space>) },
  ];

  const planColumns = [
    { title: '计划名称', dataIndex: 'plan_name', key: 'plan_name' },
    { title: '关联设备数', dataIndex: 'equipment_codes', key: 'equipment_codes', render: (codes: string[]) => codes.length },
    { title: '周期类型', dataIndex: 'cycle_type', key: 'cycle_type' },
    { title: '负责人', dataIndex: 'assignee', key: 'assignee' },
    { title: '状态', dataIndex: 'status', key: 'status', render: (status: string) => (<span style={{ color: statusColors[status] }}>{status}</span>) },
    { title: '开始日期', dataIndex: 'start_date', key: 'start_date', render: (date: string) => dayjs(date).format('YYYY-MM-DD') },
    { title: '结束日期', dataIndex: 'end_date', key: 'end_date', render: (date: string) => dayjs(date).format('YYYY-MM-DD') },
    { title: '操作', key: 'action', render: (_: unknown, record: MaintenancePlan) => (<Space><Button type="link" icon={<EditOutlined />} onClick={() => handleEditPlan(record)} /><Popconfirm title="确定删除此计划？" onConfirm={() => handleDeletePlan(record._id || '')} okText="确定" cancelText="取消"><Button type="link" danger icon={<DeleteOutlined />} /></Popconfirm></Space>) },
  ];

  const taskColumns = [
    { title: '设备编号', dataIndex: 'equipment_code', key: 'equipment_code' },
    { title: '设备名称', dataIndex: 'equipment_name', key: 'equipment_name' },
    { title: '计划日期', dataIndex: 'scheduled_date', key: 'scheduled_date', render: (date: string) => dayjs(date).format('YYYY-MM-DD') },
    { title: '执行人', dataIndex: 'assignee', key: 'assignee' },
    { title: '状态', dataIndex: 'status', key: 'status', render: (status: string) => (<span style={{ color: statusColors[status] }}>{status}</span>) },
    { title: '操作', key: 'action', render: (_: unknown, record: MaintenanceTask) => (<Space><Button type="link" icon={<EditOutlined />} onClick={() => handleEditTask(record)} /><Button type="link" icon={<CheckCircleOutlined />} onClick={() => handleCompleteTask(record._id || '')} disabled={record.status === '已完成'} /></Space>) },
  ];

  const reminderColumns = [
    { title: '设备编号', dataIndex: 'equipment_code', key: 'equipment_code' },
    { title: '设备名称', dataIndex: 'equipment_name', key: 'equipment_name' },
    { title: '到期日期', dataIndex: 'due_date', key: 'due_date', render: (date: string) => dayjs(date).format('YYYY-MM-DD') },
    { title: '剩余天数', dataIndex: 'days_remaining', key: 'days_remaining', render: (days: number) => (<span style={{ color: days <= 3 ? 'red' : days <= 7 ? 'orange' : 'black' }}>{days}天</span>) },
    { title: '负责人', dataIndex: 'assignee', key: 'assignee' },
    { title: '状态', dataIndex: 'reminder_status', key: 'reminder_status', render: (status: string) => (<span style={{ color: statusColors[status] }}>{status}</span>) },
    { title: '操作', key: 'action', render: (_: unknown, record: MaintenanceReminder) => (<Button type="link" icon={<CheckCircleOutlined />} onClick={() => handleProcessReminder(record._id || '')} disabled={record.reminder_status !== '未处理'} />) },
  ];

  const getReminderStats = () => {
    const pending = reminders.filter(r => r.reminder_status === '未处理').length;
    const processed = reminders.filter(r => r.reminder_status === '已处理').length;
    const expired = reminders.filter(r => r.reminder_status === '已过期').length;
    return { pending, processed, expired };
  };

  const stats = getReminderStats();

  return (<div>
    <Row gutter={16} style={{ marginBottom: 16 }}>
      <Col span={8}>
        <div style={{ background: '#fff', padding: '16px', borderRadius: '8px', textAlign: 'center' }}>
          <ExclamationCircleOutlined style={{ fontSize: 24, color: '#ff4d4f', marginBottom: 8 }} />
          <div style={{ fontSize: 24, fontWeight: 'bold', color: '#ff4d4f' }}>{stats.pending}</div>
          <div style={{ color: '#666' }}>待处理提醒</div>
        </div>
      </Col>
      <Col span={8}>
        <div style={{ background: '#fff', padding: '16px', borderRadius: '8px', textAlign: 'center' }}>
          <ClockCircleOutlined style={{ fontSize: 24, color: '#faad14', marginBottom: 8 }} />
          <div style={{ fontSize: 24, fontWeight: 'bold', color: '#faad14' }}>{tasks.filter(t => t.status === '待执行').length}</div>
          <div style={{ color: '#666' }}>待执行任务</div>
        </div>
      </Col>
      <Col span={8}>
        <div style={{ background: '#fff', padding: '16px', borderRadius: '8px', textAlign: 'center' }}>
          <CheckCircleOutlined style={{ fontSize: 24, color: '#52c41a', marginBottom: 8 }} />
          <div style={{ fontSize: 24, fontWeight: 'bold', color: '#52c41a' }}>{plans.filter(p => p.status === '已完成').length}</div>
          <div style={{ color: '#666' }}>已完成计划</div>
        </div>
      </Col>
    </Row>

    <Tabs defaultActiveKey="plan">
      <Tabs.TabPane tab="维保周期" key="cycle">
        <Space style={{ marginBottom: 16 }}>
          <Button type="primary" icon={<PlusOutlined />} onClick={handleAddCycle}>新增周期</Button>
        </Space>
        <Table columns={cycleColumns} dataSource={cycles} rowKey="_id" pagination={{ current: page, pageSize, total: cycleTotal, onChange: (p, s) => { setPage(p); setPageSize(s); } }} />
      </Tabs.TabPane>

      <Tabs.TabPane tab="维保计划" key="plan">
        <Space style={{ marginBottom: 16 }}>
          <Button type="primary" icon={<PlusOutlined />} onClick={handleAddPlan}>新增计划</Button>
        </Space>
        <Table columns={planColumns} dataSource={plans} rowKey="_id" pagination={{ current: page, pageSize, total: planTotal, onChange: (p, s) => { setPage(p); setPageSize(s); } }} />
      </Tabs.TabPane>

      <Tabs.TabPane tab="维保任务" key="task">
        <Table columns={taskColumns} dataSource={tasks} rowKey="_id" pagination={{ current: page, pageSize, total: taskTotal, onChange: (p, s) => { setPage(p); setPageSize(s); } }} />
      </Tabs.TabPane>

      <Tabs.TabPane tab="维保提醒" key="reminder">
        <Space style={{ marginBottom: 16 }}>
          <Button type="primary" icon={<ClockCircleOutlined />} onClick={handleGenerateReminders}>生成提醒</Button>
        </Space>
        <Table columns={reminderColumns} dataSource={reminders} rowKey="_id" pagination={{ current: page, pageSize, total: reminderTotal, onChange: (p, s) => { setPage(p); setPageSize(s); } }} />
      </Tabs.TabPane>
    </Tabs>

    <Modal title={editingCycleId ? '编辑维保周期' : '新增维保周期'} open={cycleModalOpen} onCancel={() => setCycleModalOpen(false)} onOk={handleSubmitCycle}>
      <Form form={cycleForm} layout="vertical">
        <Form.Item name="cycle_name" label="周期名称" rules={[{ required: true, message: '请输入周期名称' }]}><Input /></Form.Item>
        <Form.Item name="equipment_code" label="设备编号" rules={[{ required: true, message: '请选择设备编号' }]}><Select>
            {equipmentList.map((eq) => (<Select.Option key={eq.equipment_code} value={eq.equipment_code}>
                {eq.equipment_code} - {eq.name}
              </Select.Option>))}
          </Select></Form.Item>
        <Form.Item name="cycle_type" label="周期类型" rules={[{ required: true, message: '请选择周期类型' }]}><Select>
            {Object.keys(cycleTypeMap).map((key) => (<Select.Option key={key} value={key}>{key}</Select.Option>))}
          </Select></Form.Item>
        <Form.Item name="interval_days" label="间隔天数" rules={[{ required: true, message: '请输入间隔天数' }]}><Input type="number" /></Form.Item>
        <Form.Item name="reminder_days" label="提前提醒天数" rules={[{ required: true, message: '请输入提前提醒天数' }]}><Input type="number" /></Form.Item>
        <Form.Item name="status" label="状态"><Select>
            <Select.Option value="启用">启用</Select.Option>
            <Select.Option value="停用">停用</Select.Option>
          </Select></Form.Item>
      </Form>
    </Modal>

    <Modal title={editingPlanId ? '编辑维保计划' : '新增维保计划'} open={planModalOpen} onCancel={() => setPlanModalOpen(false)} onOk={handleSubmitPlan} width={600}>
      <Form form={planForm} layout="vertical">
        <Form.Item name="plan_name" label="计划名称" rules={[{ required: true, message: '请输入计划名称' }]}><Input /></Form.Item>
        <Form.Item name="equipment_codes" label="关联设备" rules={[{ required: true, message: '请选择关联设备' }]}><Select mode="multiple" style={{ width: '100%' }}>
            {equipmentList.map((eq) => (<Select.Option key={eq.equipment_code} value={eq.equipment_code}>
                {eq.equipment_code} - {eq.name}
              </Select.Option>))}
          </Select></Form.Item>
        <Form.Item name="cycle_type" label="周期类型" rules={[{ required: true, message: '请选择周期类型' }]}><Select>
            {Object.keys(cycleTypeMap).map((key) => (<Select.Option key={key} value={key}>{key}</Select.Option>))}
          </Select></Form.Item>
        <Form.Item name="start_date" label="开始日期" rules={[{ required: true, message: '请选择开始日期' }]}><DatePicker style={{ width: '100%' }} /></Form.Item>
        <Form.Item name="end_date" label="结束日期" rules={[{ required: true, message: '请选择结束日期' }]}><DatePicker style={{ width: '100%' }} /></Form.Item>
        <Form.Item name="assignee" label="负责人" rules={[{ required: true, message: '请输入负责人' }]}><Input /></Form.Item>
      </Form>
    </Modal>

    <Modal title="编辑维保任务" open={taskModalOpen} onCancel={() => setTaskModalOpen(false)} onOk={handleSubmitTask}>
      <Form form={taskForm} layout="vertical">
        <Form.Item name="equipment_code" label="设备编号"><Input disabled /></Form.Item>
        <Form.Item name="equipment_name" label="设备名称"><Input disabled /></Form.Item>
        <Form.Item name="scheduled_date" label="计划日期"><DatePicker style={{ width: '100%' }} /></Form.Item>
        <Form.Item name="assignee" label="执行人"><Input /></Form.Item>
        <Form.Item name="status" label="状态"><Select>
            <Select.Option value="待执行">待执行</Select.Option>
            <Select.Option value="执行中">执行中</Select.Option>
            <Select.Option value="已完成">已完成</Select.Option>
            <Select.Option value="逾期">逾期</Select.Option>
          </Select></Form.Item>
        <Form.Item name="maintenance_result" label="维保结果"><Input.TextArea /></Form.Item>
        <Form.Item name="remarks" label="备注"><Input.TextArea /></Form.Item>
      </Form>
    </Modal>
  </div>);
}

export default MaintenancePlanPage;