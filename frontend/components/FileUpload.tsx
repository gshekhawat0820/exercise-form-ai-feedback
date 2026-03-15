'use client';

import { useState, useCallback, DragEvent } from 'react';
import { Upload, FileVideo, AlertCircle, Loader2 } from 'lucide-react';
import { apiClient } from '@/lib/api';
import { isValidVideoType, isValidFileSize, formatFileSize } from '@/lib/utils';

interface FileUploadProps {
  onAnalysisComplete: (result: any) => void;
  isAnalyzing: boolean;
  setIsAnalyzing: (value: boolean) => void;
}

export default function FileUpload({ onAnalysisComplete, isAnalyzing, setIsAnalyzing }: FileUploadProps) {
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Handle drag events
  const handleDrag = useCallback((e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  }, []);

  // Handle drop
  const handleDrop = useCallback((e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    setError(null);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelect(e.dataTransfer.files[0]);
    }
  }, []);

  // Handle file selection
  const handleFileSelect = (file: File) => {
    // Validate file type
    if (!isValidVideoType(file)) {
      setError('Invalid file type. Please upload MP4, MOV, or AVI video files.');
      setSelectedFile(null);
      return;
    }

    // Validate file size (50MB max)
    if (!isValidFileSize(file, 50)) {
      setError('File too large. Maximum size is 50MB.');
      setSelectedFile(null);
      return;
    }

    setError(null);
    setSelectedFile(file);
  };

  // Handle file input change
  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFileSelect(e.target.files[0]);
    }
  };

  // Handle analysis
  const handleAnalyze = async () => {
    if (!selectedFile) return;

    setIsAnalyzing(true);
    setError(null);

    try {
      const result = await apiClient.analyzeVideo(selectedFile);
      onAnalysisComplete(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred during analysis');
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Upload Area */}
      <div
        className={`relative border-2 border-dashed rounded-xl transition-all ${
          dragActive
            ? 'border-primary-500 bg-primary-50'
            : 'border-slate-300 bg-white hover:border-primary-400'
        } ${isAnalyzing ? 'opacity-50 pointer-events-none' : ''}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <input
          type="file"
          id="file-upload"
          className="hidden"
          accept="video/mp4,video/quicktime,video/x-msvideo"
          onChange={handleFileInputChange}
          disabled={isAnalyzing}
        />

        <label
          htmlFor="file-upload"
          className="flex flex-col items-center justify-center py-12 px-6 cursor-pointer"
        >
          {!selectedFile ? (
            <>
              <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mb-4">
                <Upload className="w-8 h-8 text-primary-600" />
              </div>
              <h3 className="text-lg font-semibold text-slate-900 mb-2">
                Upload Exercise Video
              </h3>
              <p className="text-sm text-slate-600 text-center mb-2">
                Drag and drop your video here, or click to browse
              </p>
              <p className="text-xs text-slate-500">
                Supports MP4, MOV, AVI • Max 50MB • 5-30 seconds
              </p>
            </>
          ) : (
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                <FileVideo className="w-6 h-6 text-green-600" />
              </div>
              <div className="text-left">
                <p className="font-medium text-slate-900">{selectedFile.name}</p>
                <p className="text-sm text-slate-600">{formatFileSize(selectedFile.size)}</p>
              </div>
              {!isAnalyzing && (
                <button
                  type="button"
                  onClick={(e) => {
                    e.preventDefault();
                    setSelectedFile(null);
                    setError(null);
                  }}
                  className="ml-auto text-slate-400 hover:text-slate-600"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              )}
            </div>
          )}
        </label>
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
          <div>
            <h4 className="font-medium text-red-900 mb-1">Analysis Failed</h4>
            <p className="text-sm text-red-700">{error}</p>
          </div>
        </div>
      )}

      {/* Analyze Button */}
      {selectedFile && !isAnalyzing && (
        <button
          onClick={handleAnalyze}
          className="w-full bg-primary-600 hover:bg-primary-700 text-white font-semibold py-4 px-6 rounded-xl transition-colors shadow-lg shadow-primary-500/30"
        >
          Analyze Exercise Form
        </button>
      )}

      {/* Loading State */}
      {isAnalyzing && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
          <div className="flex items-center gap-4">
            <Loader2 className="w-6 h-6 text-blue-600 animate-spin" />
            <div>
              <h4 className="font-medium text-blue-900 mb-1">Analyzing Your Form...</h4>
              <p className="text-sm text-blue-700">
                Our AI is examining your video. This may take up to 30 seconds.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Tips */}
      {!selectedFile && !isAnalyzing && (
        <div className="bg-slate-50 rounded-lg p-4 border border-slate-200">
          <h4 className="font-medium text-slate-900 mb-3">Tips for best results:</h4>
          <ul className="space-y-2 text-sm text-slate-700">
            <li className="flex items-start gap-2">
              <svg className="w-5 h-5 text-green-600 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              <span>Position camera to show your full body during the exercise</span>
            </li>
            <li className="flex items-start gap-2">
              <svg className="w-5 h-5 text-green-600 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              <span>Ensure good lighting so your form is clearly visible</span>
            </li>
            <li className="flex items-start gap-2">
              <svg className="w-5 h-5 text-green-600 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              <span>Capture at least 2-3 full repetitions of your exercise</span>
            </li>
          </ul>
        </div>
      )}
    </div>
  );
}
