import { Layout as AntLayout, Menu } from 'antd';
import { AppstoreOutlined, CalendarOutlined, WarningOutlined } from '@ant-design/icons';
import { useNavigate, useLocation } from 'react-router-dom';

const { Header, Content, Sider } = AntLayout;

interface LayoutProps {
  children: React.ReactNode;
}

function Layout({ children }: LayoutProps) {
  const navigate = useNavigate();
  const location = useLocation();

  const menuItems = [
    {
      key: '/equipment',
      icon: <AppstoreOutlined />,
      label: '设备档案',
    },
    {
      key: '/inspection',
      icon: <CalendarOutlined />,
      label: '巡检计划',
    },
    {
      key: '/repair',
      icon: <WarningOutlined />,
      label: '故障报修',
    },
  ];

  const handleMenuClick = ({ key }: { key: string }) => {
    navigate(key);
  };

  return (
    <AntLayout style={{ minHeight: '100vh' }}>
      <Header style={{ display: 'flex', alignItems: 'center', background: '#001529' }}>
        <h1 style={{ color: '#fff', margin: 0, fontSize: '18px' }}>医疗设备巡检管理系统</h1>
      </Header>
      <AntLayout>
        <Sider width={200} theme="dark">
          <Menu
            mode="inline"
            selectedKeys={[location.pathname]}
            items={menuItems}
            onClick={handleMenuClick}
          />
        </Sider>
        <Content style={{ padding: '24px', background: '#f0f2f5' }}>
          {children}
        </Content>
      </AntLayout>
    </AntLayout>
  );
}

export default Layout;
