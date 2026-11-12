export type DiseaseClass =
  | "healthy"
  | "powdery_mildew"
  | "downy_mildew"
  | "fungal_leaf_spot"
  | "viral_symptoms"
  | "pest_damage"
  | "bunchy_top";

export type SeverityClass = "healthy" | "early" | "moderate" | "severe";

export interface DetectionResult {
  id: string;
  timestamp: string;
  rover_location: {
    row: number;
    section: string;
    distance_from_start_meters: number;
  };
  detection_result: {
    image_path: string;
    disease_class: DiseaseClass;
    confidence: number;
    severity_class: SeverityClass;
    affected_area_percentage: number;
    symptoms_detected: string[];
  };
  environmental_data: {
    temperature_celsius: number;
    humidity_percentage: number;
    soil_moisture_percentage: number;
    light_intensity_lux: number;
  };
}

export interface FarmCell {
  row: number;
  col: number;
  section: string;
  status: "healthy" | "attention" | "diseased";
  disease_class: DiseaseClass;
  severity: SeverityClass;
  last_checked: string;
  detection_id?: string;
}

// Latest detection (live)
export const latestDetection: DetectionResult = {
  id: "det_001",
  timestamp: "2026-09-11T14:30:00Z",
  rover_location: {
    row: 2,
    section: "B",
    distance_from_start_meters: 18,
  },
  detection_result: {
    image_path: "/images/detection_001.jpg",
    disease_class: "powdery_mildew",
    confidence: 0.94,
    severity_class: "moderate",
    affected_area_percentage: 25,
    symptoms_detected: ["white_coating", "leaf_curling"],
  },
  environmental_data: {
    temperature_celsius: 31,
    humidity_percentage: 78,
    soil_moisture_percentage: 62,
    light_intensity_lux: 720,
  },
};

// Historical detections (past 30 days)
export const historicalDetections: DetectionResult[] = [
  {
    id: "det_001",
    timestamp: "2026-09-11T14:30:00Z",
    rover_location: { row: 2, section: "B", distance_from_start_meters: 18 },
    detection_result: {
      image_path: "/images/det_001.jpg",
      disease_class: "powdery_mildew",
      confidence: 0.94,
      severity_class: "moderate",
      affected_area_percentage: 25,
      symptoms_detected: ["white_coating", "leaf_curling"],
    },
    environmental_data: {
      temperature_celsius: 31,
      humidity_percentage: 78,
      soil_moisture_percentage: 62,
      light_intensity_lux: 720,
    },
  },
  {
    id: "det_002",
    timestamp: "2026-09-10T09:15:00Z",
    rover_location: { row: 4, section: "A", distance_from_start_meters: 34 },
    detection_result: {
      image_path: "/images/det_002.jpg",
      disease_class: "downy_mildew",
      confidence: 0.87,
      severity_class: "early",
      affected_area_percentage: 12,
      symptoms_detected: ["yellow_spots", "brown_lesions"],
    },
    environmental_data: {
      temperature_celsius: 28,
      humidity_percentage: 85,
      soil_moisture_percentage: 70,
      light_intensity_lux: 540,
    },
  },
  {
    id: "det_003",
    timestamp: "2026-09-09T11:45:00Z",
    rover_location: { row: 1, section: "C", distance_from_start_meters: 8 },
    detection_result: {
      image_path: "/images/det_003.jpg",
      disease_class: "healthy",
      confidence: 0.98,
      severity_class: "healthy",
      affected_area_percentage: 0,
      symptoms_detected: [],
    },
    environmental_data: {
      temperature_celsius: 29,
      humidity_percentage: 72,
      soil_moisture_percentage: 58,
      light_intensity_lux: 890,
    },
  },
  {
    id: "det_004",
    timestamp: "2026-09-08T15:00:00Z",
    rover_location: { row: 3, section: "D", distance_from_start_meters: 28 },
    detection_result: {
      image_path: "/images/det_004.jpg",
      disease_class: "fungal_leaf_spot",
      confidence: 0.91,
      severity_class: "severe",
      affected_area_percentage: 65,
      symptoms_detected: ["circular_lesions", "yellow_halo"],
    },
    environmental_data: {
      temperature_celsius: 33,
      humidity_percentage: 82,
      soil_moisture_percentage: 74,
      light_intensity_lux: 420,
    },
  },
  {
    id: "det_005",
    timestamp: "2026-09-07T10:20:00Z",
    rover_location: { row: 5, section: "B", distance_from_start_meters: 42 },
    detection_result: {
      image_path: "/images/det_005.jpg",
      disease_class: "viral_symptoms",
      confidence: 0.79,
      severity_class: "moderate",
      affected_area_percentage: 38,
      symptoms_detected: ["mosaic_pattern", "mottle", "leaf_deformation"],
    },
    environmental_data: {
      temperature_celsius: 30,
      humidity_percentage: 76,
      soil_moisture_percentage: 60,
      light_intensity_lux: 680,
    },
  },
  {
    id: "det_006",
    timestamp: "2026-09-06T08:30:00Z",
    rover_location: { row: 6, section: "A", distance_from_start_meters: 50 },
    detection_result: {
      image_path: "/images/det_006.jpg",
      disease_class: "pest_damage",
      confidence: 0.88,
      severity_class: "early",
      affected_area_percentage: 15,
      symptoms_detected: ["fruit_fly_marks", "aphid_colonies"],
    },
    environmental_data: {
      temperature_celsius: 27,
      humidity_percentage: 68,
      soil_moisture_percentage: 52,
      light_intensity_lux: 950,
    },
  },
  {
    id: "det_007",
    timestamp: "2026-09-05T13:10:00Z",
    rover_location: { row: 2, section: "C", distance_from_start_meters: 16 },
    detection_result: {
      image_path: "/images/det_007.jpg",
      disease_class: "powdery_mildew",
      confidence: 0.96,
      severity_class: "severe",
      affected_area_percentage: 72,
      symptoms_detected: ["white_coating", "leaf_curling", "stunted_growth"],
    },
    environmental_data: {
      temperature_celsius: 35,
      humidity_percentage: 80,
      soil_moisture_percentage: 65,
      light_intensity_lux: 600,
    },
  },
  {
    id: "det_008",
    timestamp: "2026-09-04T09:00:00Z",
    rover_location: { row: 4, section: "D", distance_from_start_meters: 36 },
    detection_result: {
      image_path: "/images/det_008.jpg",
      disease_class: "healthy",
      confidence: 0.99,
      severity_class: "healthy",
      affected_area_percentage: 0,
      symptoms_detected: [],
    },
    environmental_data: {
      temperature_celsius: 26,
      humidity_percentage: 65,
      soil_moisture_percentage: 55,
      light_intensity_lux: 1100,
    },
  },
];

// 5x4 farm grid (5 rows, 4 sections A-D)
export const farmGrid: FarmCell[] = [
  { row: 1, col: 1, section: "A", status: "healthy", disease_class: "healthy", severity: "healthy", last_checked: "2026-09-11T09:00:00Z" },
  { row: 1, col: 2, section: "B", status: "healthy", disease_class: "healthy", severity: "healthy", last_checked: "2026-09-11T09:10:00Z" },
  { row: 1, col: 3, section: "C", status: "healthy", disease_class: "healthy", severity: "healthy", last_checked: "2026-09-11T09:20:00Z", detection_id: "det_003" },
  { row: 1, col: 4, section: "D", status: "attention", disease_class: "pest_damage", severity: "early", last_checked: "2026-09-11T09:30:00Z", detection_id: "det_006" },
  { row: 2, col: 1, section: "A", status: "healthy", disease_class: "healthy", severity: "healthy", last_checked: "2026-09-11T10:00:00Z" },
  { row: 2, col: 2, section: "B", status: "diseased", disease_class: "powdery_mildew", severity: "moderate", last_checked: "2026-09-11T14:30:00Z", detection_id: "det_001" },
  { row: 2, col: 3, section: "C", status: "diseased", disease_class: "powdery_mildew", severity: "severe", last_checked: "2026-09-11T10:20:00Z", detection_id: "det_007" },
  { row: 2, col: 4, section: "D", status: "healthy", disease_class: "healthy", severity: "healthy", last_checked: "2026-09-11T10:30:00Z" },
  { row: 3, col: 1, section: "A", status: "healthy", disease_class: "healthy", severity: "healthy", last_checked: "2026-09-11T11:00:00Z" },
  { row: 3, col: 2, section: "B", status: "attention", disease_class: "downy_mildew", severity: "early", last_checked: "2026-09-11T11:10:00Z" },
  { row: 3, col: 3, section: "C", status: "healthy", disease_class: "healthy", severity: "healthy", last_checked: "2026-09-11T11:20:00Z" },
  { row: 3, col: 4, section: "D", status: "diseased", disease_class: "fungal_leaf_spot", severity: "severe", last_checked: "2026-09-11T11:30:00Z", detection_id: "det_004" },
  { row: 4, col: 1, section: "A", status: "attention", disease_class: "downy_mildew", severity: "early", last_checked: "2026-09-11T12:00:00Z", detection_id: "det_002" },
  { row: 4, col: 2, section: "B", status: "healthy", disease_class: "healthy", severity: "healthy", last_checked: "2026-09-11T12:10:00Z" },
  { row: 4, col: 3, section: "C", status: "healthy", disease_class: "healthy", severity: "healthy", last_checked: "2026-09-11T12:20:00Z" },
  { row: 4, col: 4, section: "D", status: "healthy", disease_class: "healthy", severity: "healthy", last_checked: "2026-09-11T12:30:00Z", detection_id: "det_008" },
  { row: 5, col: 1, section: "A", status: "healthy", disease_class: "healthy", severity: "healthy", last_checked: "2026-09-11T13:00:00Z" },
  { row: 5, col: 2, section: "B", status: "diseased", disease_class: "viral_symptoms", severity: "moderate", last_checked: "2026-09-11T13:10:00Z", detection_id: "det_005" },
  { row: 5, col: 3, section: "C", status: "healthy", disease_class: "healthy", severity: "healthy", last_checked: "2026-09-11T13:20:00Z" },
  { row: 5, col: 4, section: "D", status: "attention", disease_class: "pest_damage", severity: "early", last_checked: "2026-09-11T13:30:00Z" },
];

// Farm health summary
export const farmHealthSummary = {
  total_cells: farmGrid.length,
  healthy: farmGrid.filter((c) => c.status === "healthy").length,
  attention: farmGrid.filter((c) => c.status === "attention").length,
  diseased: farmGrid.filter((c) => c.status === "diseased").length,
  healthy_pct: Math.round((farmGrid.filter((c) => c.status === "healthy").length / farmGrid.length) * 100),
  attention_pct: Math.round((farmGrid.filter((c) => c.status === "attention").length / farmGrid.length) * 100),
  diseased_pct: Math.round((farmGrid.filter((c) => c.status === "diseased").length / farmGrid.length) * 100),
};

// Trend data for charts (daily disease counts for past 14 days)
export const trendData = [
  { date: "Aug 29", healthy: 18, attention: 1, diseased: 1 },
  { date: "Aug 30", healthy: 17, attention: 2, diseased: 1 },
  { date: "Aug 31", healthy: 16, attention: 3, diseased: 1 },
  { date: "Sep 1",  healthy: 15, attention: 3, diseased: 2 },
  { date: "Sep 2",  healthy: 15, attention: 2, diseased: 3 },
  { date: "Sep 3",  healthy: 14, attention: 3, diseased: 3 },
  { date: "Sep 4",  healthy: 16, attention: 2, diseased: 2 },
  { date: "Sep 5",  healthy: 14, attention: 3, diseased: 3 },
  { date: "Sep 6",  healthy: 15, attention: 3, diseased: 2 },
  { date: "Sep 7",  healthy: 14, attention: 2, diseased: 4 },
  { date: "Sep 8",  healthy: 13, attention: 3, diseased: 4 },
  { date: "Sep 9",  healthy: 14, attention: 3, diseased: 3 },
  { date: "Sep 10", healthy: 13, attention: 3, diseased: 4 },
  { date: "Sep 11", healthy: 12, attention: 4, diseased: 4 },
];

// Disease distribution for pie chart
export const diseaseDistribution = [
  { name: "Powdery Mildew", value: 3, color: "#F59E0B" },
  { name: "Downy Mildew", value: 2, color: "#3B82F6" },
  { name: "Fungal Leaf Spot", value: 2, color: "#8B5CF6" },
  { name: "Viral Symptoms", value: 1, color: "#EF4444" },
  { name: "Pest Damage", value: 2, color: "#F97316" },
  { name: "Healthy", value: 10, color: "#22C55E" },
];
