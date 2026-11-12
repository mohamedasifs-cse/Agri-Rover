"use client";

import React, { useState, useEffect, useRef, useCallback } from "react";
import {
  Camera,
  Video,
  VideoOff,
  RefreshCw,
  Upload,
  AlertCircle,
  CheckCircle2,
  Sparkles,
  Info,
  Layers,
  ChevronRight,
  ShieldCheck,
  AlertTriangle,
  RotateCcw,
} from "lucide-react";
import {
  cameraApi,
  predictApi,
  PredictionResult,
  CameraStatus,
  CAMERA_BASE_URL,
} from "@/lib/api";
import { cn } from "@/lib/utils";

interface WebcamCaptureCardProps {
  onPredictionComplete?: (result: PredictionResult) => void;
}

export default function WebcamCaptureCard({ onPredictionComplete }: WebcamCaptureCardProps) {
  // Camera state
  const [isCameraRunning, setIsCameraRunning] = useState<boolean>(false);
  const [connectionStatus, setConnectionStatus] = useState<"offline" | "connecting" | "streaming" | "error">("offline");
  const [cameraInfo, setCameraInfo] = useState<CameraStatus | null>(null);
  const [cameraError, setCameraError] = useState<string | null>(null);
  const [streamKey, setStreamKey] = useState<number>(Date.now());

  // Prediction state
  const [isAnalyzing, setIsAnalyzing] = useState<boolean>(false);
  const [prediction, setPrediction] = useState<PredictionResult | null>(null);
  const [predictionError, setPredictionError] = useState<string | null>(null);
  const [capturedPreviewUrl, setCapturedPreviewUrl] = useState<string | null>(null);

  // File upload state
  const [isDragging, setIsDragging] = useState<boolean>(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const isMountedRef = useRef<boolean>(true);

  // Poll camera status safely
  const checkStatus = useCallback(async () => {
    try {
      const status = await cameraApi.getStatus();
      if (!isMountedRef.current) return;
      setCameraInfo(status);
      if (status.running) {
        setIsCameraRunning(true);
        setConnectionStatus("streaming");
        setCameraError(null);
      } else {
        setIsCameraRunning(false);
        setConnectionStatus(prev => (prev === "streaming" ? "offline" : prev));
      }
    } catch {
      if (!isMountedRef.current) return;
      setIsCameraRunning(false);
      setConnectionStatus("offline");
    }
  }, []);

  useEffect(() => {
    isMountedRef.current = true;
    checkStatus();

    // Gentle polling interval (every 6 seconds) to maintain connection state without overwhelming the Pi
    const interval = setInterval(() => {
      if (isMountedRef.current) {
        checkStatus();
      }
    }, 6000);

    return () => {
      isMountedRef.current = false;
      clearInterval(interval);
    };
  }, [checkStatus]);

  // Start Camera
  const handleStartCamera = async () => {
    setConnectionStatus("connecting");
    setCameraError(null);
    try {
      const res = await cameraApi.start();
      if (res.success) {
        setIsCameraRunning(true);
        setConnectionStatus("streaming");
        setStreamKey(Date.now());
        setCameraInfo(res.status);
      } else {
        setConnectionStatus("error");
        setCameraError(res.message || "Failed to start camera device.");
      }
    } catch (err: unknown) {
      setConnectionStatus("error");
      const msg = err instanceof Error ? err.message : "Cannot reach Raspberry Pi camera microservice.";
      setCameraError(`${msg} Ensure Pi 5 is powered on at ${CAMERA_BASE_URL}`);
    }
  };

  // Stop Camera
  const handleStopCamera = async () => {
    setConnectionStatus("connecting");
    try {
      await cameraApi.stop();
      setIsCameraRunning(false);
      setConnectionStatus("offline");
      setCameraError(null);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to stop camera.";
      setCameraError(msg);
      setConnectionStatus("offline");
    }
  };

  // Capture frame from USB Webcam and analyze with FastAPI
  const handleCaptureAndDetect = async () => {
    setIsAnalyzing(true);
    setPredictionError(null);
    try {
      // 1. Retrieve crisp frame directly from Raspberry Pi 5 /snapshot endpoint
      const blob = await cameraApi.fetchSnapshotBlob();

      // Set local snapshot preview
      const previewUrl = URL.createObjectURL(blob);
      setCapturedPreviewUrl(previewUrl);

      // 2. Transmit to FastAPI PyTorch EfficientNet-B0 inference engine
      const result = await predictApi.predictFile(blob, `rover_snap_${Date.now()}.jpg`);
      setPrediction(result);
      if (onPredictionComplete) {
        onPredictionComplete(result);
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Inference request failed.";
      setPredictionError(msg);
    } finally {
      setIsAnalyzing(false);
    }
  };

  // Handle uploaded field image
  const handleFileUpload = async (file: File) => {
    if (!file.type.startsWith("image/")) {
      setPredictionError("Please select a valid image file (JPEG, PNG, or WEBP).");
      return;
    }

    setIsAnalyzing(true);
    setPredictionError(null);

    const previewUrl = URL.createObjectURL(file);
    setCapturedPreviewUrl(previewUrl);

    try {
      const result = await predictApi.predictFile(file, file.name);
      setPrediction(result);
      if (onPredictionComplete) {
        onPredictionComplete(result);
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to analyze uploaded image.";
      setPredictionError(msg);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileUpload(e.dataTransfer.files[0]);
    }
  };

  return (
    <div className="card p-6 border border-green-200/80 shadow-card animate-fade-in space-y-6">
      {/* Header & Status Indicator */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-green-100">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-leaf-gradient flex items-center justify-center shadow-glow text-white">
            <Camera className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-leaf-dark">Live Rover Camera & AI Diagnosis</h3>
            <p className="text-xs text-gray-500">Raspberry Pi 5 USB Webcam + EfficientNet-B0 Classifier</p>
          </div>
        </div>

        {/* Live Status Pill */}
        <div className="flex items-center gap-2 self-start sm:self-auto">
          {connectionStatus === "streaming" && (
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-green-50 text-green-700 border border-green-200">
              <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
              LIVE STREAM
            </span>
          )}
          {connectionStatus === "connecting" && (
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-amber-50 text-amber-700 border border-amber-200">
              <RefreshCw className="w-3 h-3 animate-spin" />
              CONNECTING
            </span>
          )}
          {connectionStatus === "offline" && (
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-gray-100 text-gray-600 border border-gray-200">
              <span className="w-2 h-2 rounded-full bg-gray-400" />
              STANDBY / OFFLINE
            </span>
          )}
          {connectionStatus === "error" && (
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-red-50 text-red-600 border border-red-200">
              <AlertCircle className="w-3 h-3" />
              CAMERA ERROR
            </span>
          )}

          {/* Quick Refresh Check */}
          <button
            onClick={checkStatus}
            title="Refresh status"
            className="p-1.5 text-gray-400 hover:text-leaf hover:bg-green-50 rounded-lg transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Camera Error Alert */}
      {cameraError && (
        <div className="p-4 bg-red-50/90 border border-red-200 rounded-xl flex items-start gap-3 text-sm text-red-700 animate-fade-in">
          <AlertCircle className="w-5 h-5 flex-shrink-0 text-red-500 mt-0.5" />
          <div className="flex-1">
            <p className="font-semibold">Webcam Connection Notice</p>
            <p className="text-xs text-red-600 mt-0.5">{cameraError}</p>
          </div>
          <button
            onClick={handleStartCamera}
            className="px-3 py-1 bg-red-600 text-white rounded-lg text-xs font-medium hover:bg-red-700 transition-colors"
          >
            Retry
          </button>
        </div>
      )}

      {/* Main Grid: Live Video / Viewfinder + Controls & Image Upload */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column (7 cols): Camera Viewport */}
        <div className="lg:col-span-7 flex flex-col space-y-3">
          <div className="relative w-full aspect-video bg-gray-900 rounded-2xl overflow-hidden shadow-inner border border-green-200/50 flex items-center justify-center group">
            {isCameraRunning ? (
              // Live MJPEG Video Stream directly from Raspberry Pi 5
              // eslint-disable-next-line @next/next/no-img-element
              <img
                key={streamKey}
                src={`${cameraApi.getVideoStreamUrl()}?t=${streamKey}`}
                alt="AgriRover Live Video Feed"
                className="w-full h-full object-cover"
                onError={() => {
                  setConnectionStatus("error");
                  setCameraError("Lost video stream connection to Raspberry Pi webcam.");
                }}
              />
            ) : (
              // Standby / Viewfinder placeholder
              <div className="flex flex-col items-center justify-center p-6 text-center text-gray-400">
                <div className="w-16 h-16 rounded-2xl bg-gray-800/80 border border-gray-700 flex items-center justify-center mb-3">
                  <VideoOff className="w-8 h-8 text-gray-500" />
                </div>
                <h4 className="text-base font-semibold text-gray-200">Webcam Stream Disconnected</h4>
                <p className="text-xs text-gray-400 max-w-sm mt-1">
                  Start the camera to receive the real-time MJPEG video feed from the USB webcam mounted on the rover.
                </p>
                <button
                  onClick={handleStartCamera}
                  disabled={connectionStatus === "connecting"}
                  className="mt-4 px-5 py-2.5 bg-leaf-gradient text-white rounded-xl text-sm font-semibold hover:opacity-90 transition-opacity shadow-glow flex items-center gap-2"
                >
                  <Video className="w-4 h-4" />
                  {connectionStatus === "connecting" ? "Initializing..." : "Start Camera"}
                </button>
              </div>
            )}

            {/* Video overlay badge with camera stats */}
            {isCameraRunning && cameraInfo && (
              <div className="absolute bottom-3 left-3 px-3 py-1.5 bg-black/60 backdrop-blur-md rounded-lg text-white text-[11px] font-mono flex items-center gap-3">
                <span className="flex items-center gap-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
                  Pi 5 USB0
                </span>
                <span>{cameraInfo.actual_resolution || "640x480"}</span>
                <span>{cameraInfo.actual_fps ? `${cameraInfo.actual_fps.toFixed(0)} FPS` : "15 FPS"}</span>
              </div>
            )}
          </div>

          {/* Camera Action Buttons Strip */}
          <div className="flex flex-wrap items-center gap-3">
            {isCameraRunning ? (
              <>
                <button
                  onClick={handleCaptureAndDetect}
                  disabled={isAnalyzing}
                  className="flex-1 py-3 px-4 bg-leaf-gradient text-white rounded-xl font-semibold text-sm hover:opacity-95 transition-all shadow-glow flex items-center justify-center gap-2 disabled:opacity-50"
                >
                  {isAnalyzing ? (
                    <>
                      <RefreshCw className="w-4 h-4 animate-spin" />
                      Analyzing Leaf...
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-4 h-4" />
                      Capture & Detect Disease
                    </>
                  )}
                </button>
                <button
                  onClick={handleStopCamera}
                  className="py-3 px-4 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-xl font-semibold text-sm transition-colors flex items-center gap-1.5"
                >
                  <VideoOff className="w-4 h-4 text-gray-500" />
                  Stop
                </button>
              </>
            ) : (
              <button
                onClick={handleStartCamera}
                disabled={connectionStatus === "connecting"}
                className="flex-1 py-3 px-4 bg-leaf-gradient text-white rounded-xl font-semibold text-sm hover:opacity-95 transition-all shadow-glow flex items-center justify-center gap-2"
              >
                <Video className="w-4 h-4" />
                Start Camera
              </button>
            )}
          </div>
        </div>

        {/* Right Column (5 cols): File Upload or Snapshot Viewfinder */}
        <div className="lg:col-span-5 flex flex-col justify-between space-y-4">
          {/* Snapshot or Upload Area */}
          <div
            onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
            onDragLeave={() => setIsDragging(false)}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
            className={cn(
              "relative border-2 border-dashed rounded-2xl p-5 text-center cursor-pointer transition-all flex flex-col items-center justify-center min-h-[220px]",
              isDragging
                ? "border-primary bg-green-50/60 scale-[1.01]"
                : "border-green-200 bg-green-50/30 hover:bg-green-50/60 hover:border-green-300"
            )}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept="image/jpeg,image/png,image/webp"
              className="hidden"
              onChange={(e) => {
                if (e.target.files && e.target.files[0]) {
                  handleFileUpload(e.target.files[0]);
                }
              }}
            />

            {capturedPreviewUrl ? (
              <div className="space-y-2 w-full">
                <div className="relative w-full h-36 rounded-xl overflow-hidden bg-black/5 border border-green-200">
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img
                    src={capturedPreviewUrl}
                    alt="Analyzed leaf specimen"
                    className="w-full h-full object-cover"
                  />
                  <div className="absolute top-2 right-2 px-2 py-0.5 bg-black/60 backdrop-blur-sm rounded text-[10px] text-white font-medium">
                    Sample Analyzed
                  </div>
                </div>
                <p className="text-xs text-gray-500">Click or drop another image to re-analyze</p>
              </div>
            ) : (
              <div className="space-y-2">
                <div className="w-12 h-12 rounded-xl bg-white shadow-sm border border-green-200 flex items-center justify-center mx-auto text-leaf">
                  <Upload className="w-6 h-6" />
                </div>
                <p className="text-sm font-semibold text-agri-text">Upload Leaf Specimen</p>
                <p className="text-xs text-gray-500 max-w-[220px] mx-auto">
                  Drag & drop field photo or click to browse (JPEG, PNG, WEBP)
                </p>
              </div>
            )}
          </div>

          {/* Prediction Error Alert */}
          {predictionError && (
            <div className="p-3 bg-amber-50 border border-amber-200 rounded-xl text-xs text-amber-800 flex items-start gap-2">
              <AlertTriangle className="w-4 h-4 flex-shrink-0 text-amber-600 mt-0.5" />
              <span>{predictionError}</span>
            </div>
          )}

          {/* Quick Guidance Info */}
          <div className="p-3 bg-white rounded-xl border border-green-100 flex items-start gap-2 text-xs text-gray-600">
            <Info className="w-4 h-4 flex-shrink-0 text-primary mt-0.5" />
            <div className="space-y-1">
              <span className="font-semibold text-agri-text">Field & Web Photo Tip:</span>
              <p className="text-[11px] leading-relaxed text-gray-500">
                Crop closely around the affected yellow/brown spots so the leaf fills 80%+ of the frame.
                Wide shots showing soil, hands, or multiple vines reduce disease detection accuracy.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* AI Prediction Result Box (Displays once inference completes) */}
      {prediction && (
        <div className="pt-4 border-t border-green-100 space-y-4 animate-fade-in-up">
          <div className="flex items-center justify-between">
            <h4 className="text-base font-bold text-agri-text flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-leaf" />
              AI Diagnosis Result
            </h4>
            <span className="text-xs text-gray-400 font-mono">
              Inference: {prediction.processing_time_ms} ms • {prediction.model_version}
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Main Diagnosis Card */}
            <div
              className={cn(
                "p-4 rounded-xl border transition-all",
                prediction.status === "no_plant" && "bg-gradient-to-br from-slate-50 to-white border-slate-300 shadow-sm",
                prediction.status === "confirmed" && prediction.is_healthy && "bg-gradient-to-br from-green-50 to-white border-green-200",
                prediction.status === "confirmed" && !prediction.is_healthy && "bg-gradient-to-br from-rose-50 to-white border-rose-200",
                prediction.status === "low_confidence" && "bg-gradient-to-br from-amber-50 to-white border-amber-200",
                prediction.status === "uncertain" && "bg-gradient-to-br from-amber-50/70 to-white border-amber-300 shadow-sm"
              )}
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs uppercase tracking-wider font-semibold text-gray-500">Identified State</span>
                <span
                  className={cn(
                    "px-2.5 py-0.5 rounded-full text-xs font-bold",
                    prediction.status === "no_plant" && "bg-slate-200 text-slate-800 border border-slate-300",
                    prediction.status === "confirmed" && prediction.is_healthy && "bg-green-100 text-green-700",
                    prediction.status === "confirmed" && !prediction.is_healthy && "bg-rose-100 text-rose-700",
                    prediction.status === "low_confidence" && "bg-amber-100 text-amber-700",
                    prediction.status === "uncertain" && "bg-amber-100 text-amber-800 border border-amber-300"
                  )}
                >
                  {prediction.status === "no_plant"
                    ? "PLANT NOT FOUND"
                    : prediction.status === "uncertain"
                    ? "UNCERTAIN / UNCONFIRMED"
                    : prediction.status.toUpperCase().replace("_", " ")}
                </span>
              </div>
              <p
                className={cn(
                  "text-xl font-bold",
                  prediction.status === "no_plant" && "text-slate-900",
                  prediction.status === "confirmed" && prediction.is_healthy && "text-leaf-dark",
                  prediction.status === "confirmed" && !prediction.is_healthy && "text-rose-800",
                  prediction.status === "low_confidence" && "text-amber-900",
                  prediction.status === "uncertain" && "text-amber-900"
                )}
              >
                {prediction.disease_label}
              </p>
              <div className="mt-3">
                <div className="flex justify-between text-xs text-gray-600 mb-1">
                  <span>Confidence</span>
                  <span
                    className={cn(
                      "font-bold",
                      prediction.status === "no_plant" && "text-slate-600",
                      prediction.status === "confirmed" && prediction.is_healthy && "text-leaf",
                      prediction.status === "confirmed" && !prediction.is_healthy && "text-rose-600",
                      (prediction.status === "low_confidence" || prediction.status === "uncertain") && "text-amber-700"
                    )}
                  >
                    {prediction.confidence_percentage}%
                  </span>
                </div>
                <div className="w-full h-2 bg-gray-100 rounded-full overflow-hidden">
                  <div
                    className={cn(
                      "h-full transition-all duration-700",
                      prediction.status === "no_plant" && "bg-slate-400",
                      prediction.status === "confirmed" && prediction.is_healthy && "bg-leaf-gradient",
                      prediction.status === "confirmed" && !prediction.is_healthy && "bg-red-500",
                      (prediction.status === "low_confidence" || prediction.status === "uncertain") && "bg-amber-500"
                    )}
                    style={{ width: `${prediction.confidence_percentage}%` }}
                  />
                </div>
              </div>
            </div>

            {/* Candidate Probabilities */}
            <div className="p-4 bg-white border border-green-100 rounded-xl">
              <p className="text-xs uppercase tracking-wider font-semibold text-gray-500 mb-2">Class Candidates</p>
              {prediction.top_predictions && prediction.top_predictions.length > 0 ? (
                <div className="space-y-2">
                  {prediction.top_predictions.map((cand) => (
                    <div key={cand.disease_class} className="flex items-center justify-between text-xs">
                      <span className="text-gray-700 font-medium truncate max-w-[130px]">{cand.display_name}</span>
                      <span className="font-mono text-gray-500">{cand.confidence_percentage}%</span>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="py-2 text-center text-xs text-slate-500">
                  <p className="font-semibold text-slate-700">No Leaf Detected in Frame</p>
                  <p className="mt-1 text-[11px] text-slate-500 leading-relaxed">
                    Rover AI evaluates bitter gourd vines and leaves only.
                  </p>
                </div>
              )}
            </div>

            {/* Specimen Metadata */}
            <div className="p-4 bg-white border border-green-100 rounded-xl flex flex-col justify-between">
              <div>
                <p className="text-xs uppercase tracking-wider font-semibold text-gray-500 mb-2">Image Specimen</p>
                <div className="text-xs text-gray-600 space-y-1">
                  <div className="flex justify-between">
                    <span>Resolution:</span>
                    <span className="font-mono">{prediction.image_metadata.width} × {prediction.image_metadata.height} px</span>
                  </div>
                  <div className="flex justify-between">
                    <span>File Size:</span>
                    <span className="font-mono">{prediction.image_metadata.size_kb} KB</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Format:</span>
                    <span className="font-mono">{prediction.image_metadata.format}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Agronomy Action Notice */}
          <div
            className={cn(
              "p-4 rounded-xl space-y-3",
              prediction.status === "no_plant"
                ? "bg-slate-50 border border-slate-300"
                : "bg-green-50/70 border border-green-200"
            )}
          >
            <div className="flex items-start gap-2.5">
              {prediction.status === "no_plant" ? (
                <AlertCircle className="w-5 h-5 text-slate-600 flex-shrink-0 mt-0.5" />
              ) : (
                <ShieldCheck className="w-5 h-5 text-primary flex-shrink-0 mt-0.5" />
              )}
              <div>
                <p
                  className={cn(
                    "text-sm font-bold",
                    prediction.status === "no_plant" ? "text-slate-900" : "text-leaf-dark"
                  )}
                >
                  {prediction.status === "no_plant" ? "Botanical Verification Guidance" : "Recommended Next Action"}
                </p>
                <p className="text-xs text-gray-700 mt-0.5 leading-relaxed">{prediction.recommended_action}</p>
              </div>
            </div>

            {/* Immediate actions list if present */}
            {prediction.recommendations?.immediate && prediction.recommendations.immediate.length > 0 && (
              <div className="pt-2 border-t border-green-200/60">
                <p className="text-xs font-semibold text-leaf-dark mb-1.5">
                  {prediction.status === "no_plant" ? "Field Scanning Checklist:" : "Immediate Field Management:"}
                </p>
                <ul className="grid grid-cols-1 md:grid-cols-2 gap-1.5 text-xs text-gray-700">
                  {prediction.recommendations.immediate.map((item, idx) => (
                    <li key={idx} className="flex items-start gap-1.5">
                      <ChevronRight className="w-3.5 h-3.5 text-primary flex-shrink-0 mt-0.5" />
                      <span>{item}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Disclaimer */}
            {prediction.recommendations?.disclaimer && (
              <p className="text-[11px] text-gray-500 italic pt-1 border-t border-green-200/40">
                {prediction.recommendations.disclaimer}
              </p>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
