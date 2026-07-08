import { useState, useEffect } from 'react';
import { Table, Button, Modal, Form, Input, Select, DatePicker, Space, message, Row, Col, Card } from 'antd';
import { PlusOutlined, SearchOutlined, FileTextOutlined, CheckCircleOutlined, ExclamationCircleOutlined } from '@ant-design/icons';
import dayjs from 'dayjs';
import { maintenanceApi, equipmentApi } from '../api';
import type { MaintenanceRecord, Equipment } from '../types';

function MaintenanceRecordPage() {
  const [records, setRecords] = useState<MaintenanceRecord[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [equipmentList, setEquipmentList] = useState<Equipment[]>([]);
  
  const [searchKeyword, setSearchKeyword] = useState('');
  const [filters, setFilters] = useState({ equipment_code: '', overall_status: '' });
  
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isDetailModalOpen, setIsDetailModalOpen] = useState(false);
  const [form] = Form.useForm();
  const [selectedRecord, setSelectedRecord] = useState<MaintenanceRecord | null>(null);

  const fetchRecords = async () => {
    try {
      const response = await maintenanceApi.listRecords({ page, page_size: pageSize, ...filters });
      setRecords(response.data.data);
      setTotal(response.data.total);
    } catch (error) {
      message.error('获取维保记录失败');
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
    fetchRecords();
    fetchEquipment();
  }, [page, pageSize, filters]);

  const handleSearch = async () => {
    if (searchKeyword) {
      try {
        const response = await maintenanceApi.listRecords({ equipment_code: searchKeyword });
        setRecords(response.data.data);
        setTotal(response.data.total);
      } catch (error) {
        message.error('搜索失败');
      }
    } else {
      fetchRecords();
    }
  };

  const handleAdd = () => {
    form.resetFields();
    setIsModalOpen(true);
  };

  const handleViewDetail = (record: MaintenanceRecord) => {
    setSelectedRecord(record);
    setIsDetailModalOpen(true);
  };

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      const recordData: MaintenanceRecord = {
        ...values,
        maintenance_date: values.maintenance_date ? values.maintenance_date.toISOString() : '',
        items: values.items ? JSON.parse(values.items) : [],
      };

      await maintenanceApi.submitRecord(recordData);
      message.success('记录提交成功');
      setIsModalOpen(false);
      fetchRecords();
    } catch (error) {
      message.error('提交失败');
    }
  };

  const maintenanceTypeMap: Record<string, string> = {
    '日常保养': 'daily',
    '定期维护': 'regular',
    '专项检修': 'special',
  };

  const statusColors: Record<string, string> = {
    '正常': '#52c41a',
    '异常': '#ff4d4f',
  };

  const columns = [
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
      title: '维保日期',
      dataIndex: 'maintenance_date',
      key: 'maintenance_date',
      render: (date: string) => dayjs(date).format('YYYY-MM-DD'),
    },
    {
      title: '维保类型',
      dataIndex: 'maintenance_type',
      key: 'maintenance_type',
    },
    {
      title: '维保人员',
      dataIndex: 'maintainer',
      key: 'maintainer',
    },
    {
      title: '总体状态',
      dataIndex: 'overall_status',
      key: 'overall_status',
      render: (status: string) => (
        <span style={{ color: statusColors[status], fontWeight: 'bold' }}>
          {status === '正常' ? <><CheckCircleOutlined /> {status}</> : <><ExclamationCircleOutlined /> {status}</>}
        </span>
      ),
    },
    {
      title: '维保项目数',
      dataIndex: 'items',
      key: 'items',
      render: (items: Record<string, unknown>[]) => items.length,
    },
    {
      title: '操作',
      key: 'action',
      render: (_: unknown, record: MaintenanceRecord) => (
        <Space>
          <Button type="link" icon={<FileTextOutlined />} onClick={() => handleViewDetail(record)}>
            详情
          </Button>
        </Space>
      ),
    },
  ];

  const getStats = () => {
    const totalRecords = records.length;
    const normalCount = records.filter(r => r.overall_status === '正常').length;
    const abnormalCount = records.filter(r => r.overall_status === '异常').length;
    const normalRate = totalRecords > 0 ? ((normalCount / totalRecords) * 100).toFixed(1) : '0';
    return { totalRecords, normalCount, abnormalCount, normalRate };
  };

  const stats = getStats();

  return (
    <div>
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={6}>
          <Card>
            <div style={{ fontSize: 24, fontWeight: 'bold', color: '#1890ff' }}>{total}</div>
            <div style={{ color: '#666' }}>维保记录总数</div>
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <div style={{ fontSize: 24, fontWeight: 'bold', color: '#52c41a' }}>{stats.normalCount}</div>
            <div style={{ color: '#666' }}>正常</div>
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <div style={{ fontSize: 24, fontWeight: 'bold', color: '#ff4d4f' }}>{stats.abnormalCount}</div>
            <div style={{ color: '#666' }}>异常</div>
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <div style={{ fontSize: 24, fontWeight: 'bold', color: '#faad14' }}>{stats.normalRate}%</div>
            <div style={{ color: '#666' }}>合格率</div>
          </Card>
        </Col>
      </Row>

      <Space style={{ marginBottom: 16 }}>
        <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
          新增维保记录
        </Button>
        <Input
          placeholder="搜索设备编号"
          prefix={<SearchOutlined />}
          value={searchKeyword}
          onChange={(e) => setSearchKeyword(e.target.value)}
          onPressEnter={handleSearch}
          style={{ width: 200 }}
        />
        <Select
          placeholder="选择设备"
          value={filters.equipment_code}
          onChange={(value) => setFilters({ ...filters, equipment_code: value })}
          style={{ width: 200 }}
          allowClear
        >
          {equipmentList.map((eq) => (
            <Select.Option key={eq.equipment_code} value={eq.equipment_code}>
              {eq.equipment_code} - {eq.name}
            </Select.Option>
          ))}
        </Select>
        <Select
          placeholder="选择状态"
          value={filters.overall_status}
          onChange={(value) => setFilters({ ...filters, overall_status: value })}
          style={{ width: 150 }}
          allowClear
        >
          <Select.Option value="正常">正常</Select.Option>
          <Select.Option value="异常">异常</Select.Option>
        </Select>
      </Space>

      <Table
        columns={columns}
        dataSource={records}
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
        title="新增维保记录"
        open={isModalOpen}
        onCancel={() => setIsModalOpen(false)}
        onOk={handleSubmit}
        width={600}
      >
        <Form form={form} layout="vertical">
          <Form.Item
            name="equipment_code"
            label="设备编号"
            rules={[{ required: true, message: '请选择设备编号' }]}
          >
            <Select>
              {equipmentList.map((eq) => (
                <Select.Option key={eq.equipment_code} value={eq.equipment_code}>
                  {eq.equipment_code} - {eq.name}
                </Select.Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item
            name="equipment_name"
            label="设备名称"
            rules={[{ required: true, message: '请输入设备名称' }]}
          >
            <Input />
          </Form.Item>
          <Form.Item
            name="maintenance_date"
            label="维保日期"
            rules={[{ required: true, message: '请选择维保日期' }]}
          >
            <DatePicker style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item
            name="maintenance_type"
            label="维保类型"
            rules={[{ required: true, message: '请选择维保类型' }]}
          >
            <Select>
              {Object.keys(maintenanceTypeMap).map((key) => (
                <Select.Option key={key} value={key}>
                  {key}
                </Select.Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item
            name="maintainer"
            label="维保人员"
            rules={[{ required: true, message: '请输入维保人员' }]}
          >
            <Input />
          </Form.Item>
          <Form.Item
            name="overall_status"
            label="总体状态"
            rules={[{ required: true, message: '请选择总体状态' }]}
          >
            <Select>
              <Select.Option value="正常">正常</Select.Option>
              <Select.Option value="异常">异常</Select.Option>
            </Select>
          </Form.Item>
          <Form.Item
            name="items"
            label="维保项目（JSON格式）"
            rules={[{ required: true, message: '请输入维保项目' }]}
          >
            <Input.TextArea rows={4} placeholder='[{"item": "检查项目1", "result": "正常"}, {"item": "检查项目2", "result": "异常"}]' />
          </Form.Item>
          <Form.Item name="remarks" label="备注">
            <Input.TextArea />
          </Form.Item>
        </Form>
      </Modal>

      <Modal
        title="维保记录详情"
        open={isDetailModalOpen}
        onCancel={() => setIsDetailModalOpen(false)}
        footer={null}
        width={600}
      >
        {selectedRecord && (
          <div>
            <Row gutter={16} style={{ marginBottom: 16 }}>
              <Col span={12}>
                <div><strong>设备编号：</strong>{selectedRecord.equipment_code}</div>
              </Col>
              <Col span={12}>
                <div><strong>设备名称：</strong>{selectedRecord.equipment_name}</div>
              </Col>
              <Col span={12}>
                <div><strong>维保日期：</strong>{dayjs(selectedRecord.maintenance_date).format('YYYY-MM-DD')}</div>
              </Col>
              <Col span={12}>
                <div><strong>维保类型：</strong>{selectedRecord.maintenance_type}</div>
              </Col>
              <Col span={12}>
                <div><strong>维保人员：</strong>{selectedRecord.maintainer}</div>
              </Col>
              <Col span={12}>
                <div><strong>总体状态：</strong>
                  <span style={{ color: statusColors[selectedRecord.overall_status], fontWeight: 'bold', marginLeft: 8 }}>
                    {selectedRecord.overall_status}
                  </span>
                </div>
              </Col>
            </Row>
            
            <div style={{ marginBottom: 16 }}>
              <strong>维保项目：</strong>
              <Table
                dataSource={selectedRecord.items}
                rowKey={(_item, index) => String(index)}
                columns={[
                  { title: '项目名称', dataIndex: 'item', key: 'item' },
                  { title: '检查结果', dataIndex: 'result', key: 'result' },
                ]}
                pagination={false}
                size="small"
              />
            </div>
            
            {selectedRecord.remarks && (
              <div>
                <strong>备注：</strong>
                <p>{selectedRecord.remarks}</p>
              </div>
            )}
          </div>
        )}
      </Modal>
    </div>
  );
}

export default MaintenanceRecordPage;