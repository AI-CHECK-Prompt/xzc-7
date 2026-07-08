export interface Equipment {
  _id?: string;
  equipment_code: string;
  name: string;
  model: string;
  manufacturer: string;
  department: string;
  location: string;
  purchase_date: string;
  warranty_period?: number;
  status: string;
}

export interface InspectionPlan {
  _id?: string;
  plan_name: string;
  equipment_codes: string[];
  frequency: string;
  start_date: string;
  end_date: string;
  assignee: string;
  status: string;
  created_at?: string;
}

export interface InspectionTask {
  _id?: string;
  plan_id: string;
  equipment_code: string;
  scheduled_date: string;
  assignee: string;
  status: string;
  actual_date?: string;
  inspection_result?: string;
  issues_found?: string;
}

export interface InspectionRecord {
  _id?: string;
  equipment_code: string;
  inspector: string;
  inspection_date: string;
  items: Record<string, unknown>[];
  overall_status: string;
  remarks?: string;
}

export interface RepairOrder {
  _id?: string;
  equipment_code: string;
  equipment_name: string;
  reporter: string;
  department: string;
  description: string;
  priority: string;
  status: string;
  created_at?: string;
  updated_at?: string;
  assignee?: string;
  repair_date?: string;
  repair_result?: string;
  remarks?: string;
}

export interface MaintenanceCycle {
  _id?: string;
  cycle_name: string;
  equipment_code: string;
  cycle_type: string;
  interval_days: number;
  reminder_days: number;
  status: string;
  created_at?: string;
}

export interface MaintenancePlan {
  _id?: string;
  plan_name: string;
  equipment_codes: string[];
  cycle_type: string;
  start_date: string;
  end_date: string;
  assignee: string;
  status: string;
  created_at?: string;
  tasks?: MaintenanceTask[];
}

export interface MaintenanceTask {
  _id?: string;
  plan_id: string;
  equipment_code: string;
  equipment_name?: string;
  scheduled_date: string;
  assignee: string;
  status: string;
  actual_date?: string;
  maintenance_result?: string;
  remarks?: string;
  created_at?: string;
}

export interface MaintenanceRecord {
  _id?: string;
  equipment_code: string;
  equipment_name: string;
  maintainer: string;
  maintenance_date: string;
  maintenance_type: string;
  items: Record<string, unknown>[];
  overall_status: string;
  remarks?: string;
  created_at?: string;
}

export interface MaintenanceReminder {
  _id?: string;
  equipment_code: string;
  equipment_name: string;
  due_date: string;
  days_remaining: number;
  assignee: string;
  reminder_status: string;
  created_at?: string;
}

export interface PagedResponse<T> {
  data: T[];
  total: number;
  page: number;
  page_size: number;
}
