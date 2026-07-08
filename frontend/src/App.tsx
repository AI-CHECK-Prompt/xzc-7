import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import EquipmentList from './pages/EquipmentList';
import EquipmentDetail from './pages/EquipmentDetail';
import InspectionPlan from './pages/InspectionPlan';
import RepairOrder from './pages/RepairOrder';
import MaintenancePlan from './pages/MaintenancePlan';
import MaintenanceRecord from './pages/MaintenanceRecord';

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<EquipmentList />} />
          <Route path="/equipment" element={<EquipmentList />} />
          <Route path="/equipment/:id" element={<EquipmentDetail />} />
          <Route path="/inspection" element={<InspectionPlan />} />
          <Route path="/repair" element={<RepairOrder />} />
          <Route path="/maintenance" element={<MaintenancePlan />} />
          <Route path="/maintenance/record" element={<MaintenanceRecord />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;
