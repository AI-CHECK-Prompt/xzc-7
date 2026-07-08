import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import EquipmentList from './pages/EquipmentList';
import EquipmentDetail from './pages/EquipmentDetail';
import InspectionPlan from './pages/InspectionPlan';
import RepairOrder from './pages/RepairOrder';

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
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;
