import { DiseaseClass, SeverityClass } from "./mock-data";

export interface DiseaseInfo {
  display_name: string;
  scientific_name: string;
  description: string;
  symptoms: string[];
  causes: string[];
  recommendations: {
    immediate: string[];
    preventive: string[];
  };
  farmer_summary: string;
}

export const DISEASE_INFO: Record<DiseaseClass, DiseaseInfo> = {
  healthy: {
    display_name: "Healthy",
    scientific_name: "No disease detected",
    description: "Your bitter gourd plant is healthy and growing well.",
    symptoms: [],
    causes: [],
    recommendations: {
      immediate: ["Continue regular watering schedule", "Maintain current nutrition plan"],
      preventive: [
        "Monitor plants every 3 days",
        "Keep the pandal area clean",
        "Ensure good air circulation between plants",
      ],
    },
    farmer_summary: "Great news! Your plant is healthy. Keep up the good farming practices.",
  },
  powdery_mildew: {
    display_name: "Powdery Mildew",
    scientific_name: "Podosphaera xanthii",
    description:
      "A fungal disease that appears as white powdery coating on leaves and stems. Spreads quickly in warm, dry conditions.",
    symptoms: ["White powder-like coating on leaf surface", "Leaf curling or distortion", "Yellowing of affected leaves", "Stunted growth in severe cases"],
    causes: ["High temperatures (25–35°C)", "Low humidity combined with warm nights", "Poor air circulation", "Overhead irrigation"],
    recommendations: {
      immediate: [
        "🌿 Remove and destroy heavily infected leaves immediately",
        "💧 Spray diluted neem oil (5ml per litre) on all leaf surfaces",
        "🧪 Apply potassium bicarbonate solution (1 tsp per litre) as organic fungicide",
        "📏 Increase spacing between plants to improve air flow",
      ],
      preventive: [
        "Avoid overhead watering — water at the base only",
        "Apply sulphur-based fungicide every 10 days as prevention",
        "Remove plant debris from the field regularly",
        "Ensure pandal nets allow good air circulation",
      ],
    },
    farmer_summary:
      "Powdery mildew has been spotted. Act quickly — remove infected leaves and spray neem oil to stop it spreading to healthy plants.",
  },
  downy_mildew: {
    display_name: "Downy Mildew",
    scientific_name: "Pseudoperonospora cubensis",
    description:
      "A water mould disease causing yellow and brown spots on the upper leaf surface with a greyish-purple fuzzy growth underneath.",
    symptoms: ["Angular yellow spots on upper leaf surface", "Purple-grey fuzzy growth on underside", "Brown dead patches", "Rapid leaf wilting"],
    causes: ["High humidity (above 80%)", "Cool nights with warm days", "Wet foliage from rain or irrigation", "Poor drainage"],
    recommendations: {
      immediate: [
        "🚫 Stop overhead irrigation immediately",
        "🌬️ Improve air circulation in the pandal",
        "🧪 Apply copper-based fungicide (Bordeaux mixture) on affected areas",
        "✂️ Prune overcrowded vines to reduce humidity build-up",
      ],
      preventive: [
        "Use drip irrigation instead of overhead watering",
        "Apply Bordeaux mixture spray every 7–10 days during humid season",
        "Space plants adequately (at least 60cm between plants)",
        "Monitor humidity levels — keep below 75% where possible",
      ],
    },
    farmer_summary:
      "Downy mildew detected. This disease loves wet conditions. Stop overhead watering and apply copper fungicide now.",
  },
  fungal_leaf_spot: {
    display_name: "Fungal Leaf Spot",
    scientific_name: "Cercospora citrullina / Alternaria sp.",
    description:
      "Circular or angular lesions with distinct borders on leaves, often with a yellow halo around the spot.",
    symptoms: ["Circular brown or grey spots", "Yellow halo around spots", "Spots merge in severe cases", "Premature leaf drop"],
    causes: ["High humidity and warm temperatures", "Splashing water spreading spores", "Poor plant nutrition", "Overcrowding"],
    recommendations: {
      immediate: [
        "🌿 Remove all visibly spotted leaves and dispose away from farm",
        "🚿 Avoid wetting leaves when watering",
        "🧪 Spray mancozeb or chlorothalonil fungicide (follow label dosage)",
        "🌱 Apply balanced NPK fertiliser to boost plant immunity",
      ],
      preventive: [
        "Use disease-resistant bitter gourd varieties",
        "Rotate crops — do not grow bitter gourd in same spot consecutively",
        "Mulch soil to prevent spore splash-up",
        "Apply fungicide spray before monsoon season",
      ],
    },
    farmer_summary:
      "Fungal leaf spots found. Remove infected leaves now and spray fungicide to prevent it spreading to more plants.",
  },
  viral_symptoms: {
    display_name: "Viral Disease",
    scientific_name: "Cucumber Mosaic Virus (CMV) / Papaya Ringspot Virus (PRSV)",
    description:
      "Viral infection causing mosaic or mottle patterns on leaves, distorted growth, and reduced fruit production.",
    symptoms: ["Mosaic or mottled yellow-green patterns on leaves", "Leaf deformation or crinkle", "Stunted plant growth", "Reduced and malformed fruit"],
    causes: [
      "Spread by aphids, whiteflies, and thrips insects",
      "Contaminated tools or hands",
      "Infected plant material",
    ],
    recommendations: {
      immediate: [
        "🚨 Remove and destroy infected plants to stop virus spread",
        "🐛 Control aphid and whitefly insects with insecticidal soap spray",
        "🧤 Wash hands and sanitise tools between plants",
        "⚠️ Mark infected area and monitor neighbouring plants closely",
      ],
      preventive: [
        "Use virus-free certified seeds",
        "Install yellow sticky traps to monitor and control aphids",
        "Apply reflective mulch to repel insects",
        "Avoid planting near cucurbit crops that may carry virus",
      ],
    },
    farmer_summary:
      "Viral disease detected — this is serious. There is no cure. Remove infected plants immediately to protect healthy ones. Control insects that spread this disease.",
  },
  pest_damage: {
    display_name: "Pest Damage",
    scientific_name: "Fruit fly (Bactrocera cucurbitae), Thrips, Aphids",
    description:
      "Visible damage from insect pests including fruit fly punctures, thrips silvering, and aphid colonies on young shoots.",
    symptoms: ["Small holes or punctures on fruits/leaves", "Silvering or bronzing of leaf surface", "Curled or distorted young shoots", "Sticky residue (honeydew) from aphids", "Visible insect colonies"],
    causes: ["High insect pressure during monsoon", "Absence of natural predators", "Dense planting reducing visibility", "Nearby wild cucurbit host plants"],
    recommendations: {
      immediate: [
        "🪤 Install fruit fly protein-bait traps immediately (1 trap per 20m²)",
        "🧪 Spray spinosad or neem-based insecticide on all plant surfaces",
        "✂️ Remove and destroy infested fruits and shoots",
        "🔍 Inspect undersides of leaves for aphid colonies daily",
      ],
      preventive: [
        "Use pheromone traps to monitor fruit fly population",
        "Wrap young fruits with paper or mesh bags",
        "Encourage natural enemies (ladybirds, parasitic wasps) in the farm",
        "Apply kaolin clay spray to deter fruit flies",
      ],
    },
    farmer_summary:
      "Pest damage found. Install fruit fly traps and spray neem oil now. Check all fruits and young shoots for insect activity.",
  },
  bunchy_top: {
    display_name: "Bunchy Top",
    scientific_name: "Bitter Gourd Bunchy Top Virus (BGT) / Phytoplasma",
    description:
      "Severe viral/phytoplasma stunting causing shortened internodes, dense rosette clustering at vine tips, and failure to fruit.",
    symptoms: ["Clustered rosette of stunted leaves at shoot tip", "Shortened internodes and bushy growth", "Upward leaf curling and mild chlorosis", "Stunted vine growth and flower abortion"],
    causes: ["Transmitted by insect vectors (leafhoppers and whiteflies)", "Infected vegetative planting material", "Warm humid conditions promoting vector proliferation"],
    recommendations: {
      immediate: [
        "🚨 Immediately rogue out and bury infected vines to prevent vector transmission",
        "🐛 Spray neem seed kernel extract (NSKE 5%) or insecticidal soap to control vectors",
        "🧤 Sanitize pruning shears and tools with 10% bleach solution",
        "⚠️ Monitor adjacent pandal rows every 48 hours for early clustering",
      ],
      preventive: [
        "Install yellow sticky traps (15–20 traps per acre) to trap insect vectors",
        "Use certified disease-free seeds and nursery stock",
        "Maintain clean border zones free of wild cucurbit weeds",
        "Spray systemic botanical repellents before flowering stage",
      ],
    },
    farmer_summary:
      "Bunchy top detected — affected vines will produce clustered leaves with zero fruit yield. Uproot infected plants immediately and spray neem extract to control insect vectors.",
  },
};

export const SEVERITY_CONFIG: Record<
  SeverityClass,
  { label: string; color: string; bg: string; description: string; urgency: string }
> = {
  healthy: {
    label: "Healthy",
    color: "#22C55E",
    bg: "#F0FDF4",
    description: "No disease symptoms detected",
    urgency: "No action needed",
  },
  early: {
    label: "Early Stage",
    color: "#FBBF24",
    bg: "#FFFBEB",
    description: "Very few symptoms visible (1–20% affected area)",
    urgency: "Take preventive action within 2–3 days",
  },
  moderate: {
    label: "Moderate",
    color: "#F97316",
    bg: "#FFF7ED",
    description: "Clear symptoms present (21–60% affected area)",
    urgency: "Treatment needed within 24 hours",
  },
  severe: {
    label: "Severe — Urgent!",
    color: "#EF4444",
    bg: "#FEF2F2",
    description: "Extensive symptoms (61–100% affected area)",
    urgency: "Immediate intervention required today",
  },
};

export const DISEASE_DISPLAY_NAMES: Record<DiseaseClass, string> = {
  healthy: "Healthy",
  powdery_mildew: "Powdery Mildew",
  downy_mildew: "Downy Mildew",
  fungal_leaf_spot: "Fungal Leaf Spot",
  viral_symptoms: "Viral Disease",
  pest_damage: "Pest Damage",
  bunchy_top: "Bunchy Top",
};

export const SYMPTOM_LABELS: Record<string, string> = {
  white_coating: "White Powder Coating",
  leaf_curling: "Leaf Curling",
  yellow_spots: "Yellow Spots",
  brown_lesions: "Brown Lesions",
  circular_lesions: "Circular Lesions",
  yellow_halo: "Yellow Halo",
  mosaic_pattern: "Mosaic Pattern",
  mottle: "Mottling",
  leaf_deformation: "Leaf Deformation",
  fruit_fly_marks: "Fruit Fly Marks",
  aphid_colonies: "Aphid Colonies",
  stunted_growth: "Stunted Growth",
};
