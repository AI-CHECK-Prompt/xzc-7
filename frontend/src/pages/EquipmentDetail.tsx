import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, Descriptions, Button, Tabs, Table, Tag, message } from 'antd';
import { ArrowLeftOutlined, WarningOutlined } from '@ant-design/icons';
import dayjs from 'dayjs';
import { equipmentApi, repairApi, inspectionApi } from '../api';
import type { Equipment, RepairOrder, InspectionRecord } from '../types';

function EquipmentDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  
  const [equipment, setEquipment] = useState<Equipment | null>(null);
  const [repairRecords, setRepairRecords] = useState<RepairOrder[]>([]);
  const [inspectionRecords, setInspectionRecords] = useState<InspectionRecord[]>([]);

  const fetchEquipment = async () => {
    try {
      const response = await equipmentApi.detail(id || '');
      setEquipment(response.data);
    } catch (error) {
      message.error('获取设备详情失败');
    }
  };

  const fetchRepairRecords = async () => {
    try {
      if (equipment?.equipment_code) {
        const response = await repairApi.getRecords(equipment.equipment_code);
        setRepairRecords(response.data);
      }
    } catch (error) {
      console.error('获取维修记录失败');
    }
  };

  const fetchInspectionRecords = async () => {
    try {
      if (equipment?.equipment_code) {
        const response = await inspectionApi.getRecords(equipment.equipment_code);
        setInspectionRecords(response.data);
      }
    } catch (error) {
      console.error('获取巡检记录失败');
    }
  };

  useEffect(() => {
    fetchEquipment();
  }, [id]);

  useEffect(() => {
    fetchRepairRecords();
    fetchInspectionRecords();
  }, [equipment?.equipment_code]);

  const statusMap: Record<string, string> = {
    '正常': 'success',
    '故障': 'error',
    '维修中': 'processing',
    '停用': 'default',
  };

  const repairStatusColors: Record<string, string> = {
    '待处理': 'orange',
    '已接单': 'blue',
    '维修中': 'processing',
    '已完成': 'green',
    '已取消': 'gray',
  };

  const repairColumns = [
    {
      title: '报修单号',
      dataIndex: '_id',
      key: '_id',
      render: (id: string) => id.substring(0, 8) + '...',
    },
    {
      title: '报修人',
      dataIndex: 'reporter',
      key: 'reporter',
    },
    {
      title: '故障描述',
      dataIndex: 'description',
      key: 'description',
    },
    {
      title: '优先级',
      dataIndex: 'priority',
      key: 'priority',
      render: (priority: string) => (
        <Tag color={priority === '紧急' ? 'red' : priority === '重要' ? 'orange' : 'blue'}>
          {priority}
        </Tag>
      ),
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => (
        <span style={{ color: repairStatusColors[status] }}>{status}</span>
      ),
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date: string) => dayjs(date).format('YYYY-MM-DD HH:mm'),
    },
  ];

  const inspectionColumns = [
    {
      title: '巡检人员',
      dataIndex: 'inspector',
      key: 'inspector',
    },
    {
      title: '巡检日期',
      dataIndex: 'inspection_date',
      key: 'inspection_date',
      render: (date: string) => dayjs(date).format('YYYY-MM-DD HH:mm'),
    },
    {
      title: '总体状态',
      dataIndex: 'overall_status',
      key: 'overall_status',
      render: (status: string) => (
        <Tag color={status === '正常' ? 'green' : 'red'}>{status}</Tag>
      ),
    },
    {
      title: '备注',
      dataIndex: 'remarks',
      key: 'remarks',
    },
  ];

  if (!equipment) {
    return <div>加载中...</div>;
  }

  return (
    <div>
      <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/equipment')} style={{ marginBottom: 16 }}>
        返回
      </Button>

      <Card>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
          <div>
            <h2>{equipment.name}</h2>
            <span style={{ marginRight: 16 }}>设备编号: {equipment.equipment_code}</span>
            <Tag color={statusMap[equipment.status]}>{equipment.status}</Tag>
          </div>
          <Button 
            type="primary" 
            danger 
            icon={<WarningOutlined />}
            onClick={() => navigate('/repair')}
          >
            故障报修
          </Button>
        </div>

        <Descriptions bordered column={2} size="middle">
          <Descriptions.Item label="设备型号">{equipment.model}</Descriptions.Item>
          <Descriptions.Item label="生产厂家">{equipment.manufacturer}</Descriptions.Item>
          <Descriptions.Item label="所属科室">{equipment.department}</Descriptions.Item>
          <Descriptions.Item label="安装位置">{equipment.location}</Descriptions.Item>
          <Descriptions.Item label="采购日期">{dayjs(equipment.purchase_date).format('YYYY-MM-DD')}</Descriptions.Item>
          <Descriptions.Item label="保修期">{equipment.warranty_period ? `${equipment.warranty_period}个月` : '无'}</Descriptions.Item>
        </Descriptions>
      </Card>

      <Tabs style={{ marginTop: 24 }}>
        <Tabs.TabPane tab="维修记录" key="repair">
          <Table
            columns={repairColumns}
            dataSource={repairRecords}
            rowKey="_id"
            pagination={false}
            bordered
          />
        </Tabs.TabPane>
        <Tabs.TabPane tab="巡检记录" key="inspection">
          <Table
            columns={inspectionColumns}
            dataSource={inspectionRecords}
            rowKey="_id"
            pagination={false}
            bordered
          />
        </Tabs.TabPane>
      </Tabs>
    </div>
  );
}

export default EquipmentDetail;
