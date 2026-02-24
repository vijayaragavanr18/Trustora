"use client";

import { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, File, X } from 'lucide-react';
import { Button } from './ui/Button';
import { useRouter } from 'next/navigation';
import { api } from '@/lib/api';
import axios from 'axios';

interface UploadZoneProps {
  onUpload?: (file: File) => void;
  acceptedTypes?: string[];
  maxSize?: number; // in MB
}

export function UploadZone({ 
  onUpload, 
  acceptedTypes = ['image/*', 'video/*'],
  maxSize = 100 
}: UploadZoneProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [error, setError] = useState<string>('');
  const [uploading, setUploading] = useState(false);
  const router = useRouter();

  const onDrop = useCallback((acceptedFiles: File[], fileRejections: any[]) => {
    setError('');
    
    if (fileRejections.length > 0) {
      const rejection = fileRejections[0];
      const error = rejection.errors[0];
      
      if (error.code === 'file-too-large') {
        setError(`File is too large. Max size is ${maxSize}MB`);
      } else if (error.code === 'file-invalid-type') {
         setError('Invalid file type. Please upload a supported image or video.');
      } else {
         setError(error.message);
      }
      return;
    }

    if (acceptedFiles.length > 0) {
      const file = acceptedFiles[0];
      setSelectedFile(file);
    }
  }, [maxSize]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: acceptedTypes.reduce((acc, type) => {
      acc[type] = [];
      return acc;
    }, {} as Record<string, string[]>),
    maxSize: maxSize * 1024 * 1024,
    multiple: false
  });

  const handleUpload = async () => {
    if (!selectedFile) return;

    setUploading(true);
    setError('');

    try {
      console.log('Checking backend health...');
      try {
        const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        await axios.get(`${API_URL}/health`);
        console.log('Backend is reachable');
      } catch (healthErr) {
        console.error('Backend health check failed:', healthErr);
        throw new Error('Cannot connect to backend server. Please check if it is running.');
      }

      console.log('Starting upload...');
      
      let uploadResult;
      
      if (selectedFile.type.startsWith('image/')) {
        uploadResult = await api.uploadImage(selectedFile);
      } else if (selectedFile.type.startsWith('video/')) {
        uploadResult = await api.uploadVideo(selectedFile);
      } else if (selectedFile.type.startsWith('audio/')) {
        uploadResult = await api.uploadAudio(selectedFile);
      } else {
        throw new Error('Unsupported file type');
      }
      console.log('Upload successful!', uploadResult);

      // Start analysis
      const analysisResult = await api.startAnalysis(uploadResult.id);
      console.log('Analysis started!', analysisResult);

      // Redirect to results page
      router.push(`/analysis/${uploadResult.id}`);
      
    } catch (error: any) {
      console.error('=== UPLOAD ERROR ===');
      console.error('Full error:', error);
      console.error('Response:', error.response);
      
      const errorMessage = error.response?.data?.detail || error.message || 'Upload failed';
      setError(errorMessage);
      alert(errorMessage);
    } finally {
      setUploading(false);
    }
  };

  const removeFile = () => {
    setSelectedFile(null);
    setError('');
  };

  return (
    <div className="w-full">
      {!selectedFile ? (
        <div
          {...getRootProps()}
          className={`
            border-2 border-dashed rounded-xl p-12 text-center cursor-pointer
            transition-all duration-200
            ${isDragActive 
              ? 'border-primary bg-primary/5' 
              : 'border-border hover:border-primary/50 hover:bg-secondary/50'
            }
          `}
        >
          <input {...getInputProps()} />
          <Upload className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
          
          {isDragActive ? (
            <p className="text-lg font-medium text-primary">
              Drop file here...
            </p>
          ) : (
            <>
              <p className="text-lg font-medium mb-2">
                Drag & drop file here
              </p>
              <p className="text-sm text-muted-foreground mb-4">
                or click to browse
              </p>
              <p className="text-xs text-muted-foreground">
                Supported: Images (JPG, PNG) & Videos (MP4, MOV)
              </p>
              <p className="text-xs text-muted-foreground">
                Max size: {maxSize}MB
              </p>
            </>
          )}
        </div>
      ) : (
        <div className="border-2 border-border rounded-xl p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <File className="w-10 h-10 text-primary" />
              <div>
                <p className="font-medium">{selectedFile.name}</p>
                <p className="text-sm text-muted-foreground">
                  {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB
                </p>
              </div>
            </div>
            <button
              onClick={removeFile}
              className="p-2 hover:bg-secondary rounded-lg transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          <Button
            onClick={handleUpload}
            isLoading={uploading}
            className="w-full"
          >
            {uploading ? 'Uploading...' : 'Start Analysis'}
          </Button>
        </div>
      )}

      {error && (
        <p className="text-sm text-red-500 mt-2">{error}</p>
      )}
    </div>
  );
}
