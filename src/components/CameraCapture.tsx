"use client";

import { useRef, useState, useEffect } from 'react';
import { X, Power, Mic, Video as VideoIcon, Camera as CameraIcon, AlertCircle } from 'lucide-react';

interface CameraCaptureProps {
  onCapture: (blob: Blob) => void;
  mode?: 'photo' | 'video' | 'audio';
}

export function CameraCapture({ onCapture, mode = 'video' }: CameraCaptureProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [isRecording, setIsRecording] = useState(false);
  const [isCameraActive, setIsCameraActive] = useState(false);
  const [error, setError] = useState<string>('');
  const [stream, setStream] = useState<MediaStream | null>(null);
  const [isVideoReady, setIsVideoReady] = useState(false);
  const [captureStatus, setCaptureStatus] = useState<string>('');

  const startMedia = async () => {
    try {
      setError('');
      setCaptureStatus('Requesting permissions...');

      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        setError('Camera/Microphone access is not supported in this browser. Try Chrome or Edge.');
        setCaptureStatus('');
        return;
      }

      const constraints: MediaStreamConstraints = {
        video: mode !== 'audio'
          ? { width: { ideal: 1280 }, height: { ideal: 720 }, facingMode: 'user' }
          : false,
        audio: true
      };

      const newStream = await navigator.mediaDevices.getUserMedia(constraints);
      setStream(newStream);        // triggers the useEffect below to set srcObject
      setIsVideoReady(false);
      setIsCameraActive(true);
      setCaptureStatus('Starting camera...');

      if (mode === 'audio') {
        setIsVideoReady(true);
        setCaptureStatus('Microphone ready!');
        setTimeout(() => setCaptureStatus(''), 2000);
      }
    } catch (err: any) {
      setCaptureStatus('');
      if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
        setError('Camera/Microphone permission denied. Click the lock icon in your browser address bar to allow access.');
      } else if (err.name === 'NotFoundError') {
        setError('No camera or microphone found. Please connect a device and try again.');
      } else if (err.name === 'NotReadableError') {
        setError('Camera is in use by another app. Close other apps using the camera and try again.');
      } else {
        setError(`Failed to access ${mode === 'audio' ? 'microphone' : 'camera'}: ${err.message}`);
      }
    }
  };

  // Set srcObject whenever stream changes — this runs AFTER the video element renders
  useEffect(() => {
    if (!videoRef.current || !stream || mode === 'audio') return;
    const video = videoRef.current;
    video.srcObject = stream;
    video.play().catch(() => {
      // Autoplay blocked — onCanPlay will still fire on interaction
    });
  }, [stream, mode]);

  const stopMedia = () => {
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
      setStream(null);
    }
    if (videoRef.current) videoRef.current.srcObject = null;
    setIsCameraActive(false);
    setIsRecording(false);
    setIsVideoReady(false);
    setCaptureStatus('');
  };

  const takePhoto = () => {
    setError('');

    if (!videoRef.current || !canvasRef.current || !isCameraActive) {
      setError('Camera not ready. Please start the camera first.');
      return;
    }

    const video = videoRef.current;
    const canvas = canvasRef.current;

    const doCapture = () => {
      // Only require videoWidth > 0; don't block on readyState
      if (video.videoWidth === 0) return false;
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight || video.videoWidth * 0.75;
      const ctx = canvas.getContext('2d');
      if (!ctx) return false;
      ctx.save();
      ctx.translate(canvas.width, 0);
      ctx.scale(-1, 1);
      ctx.drawImage(video, 0, 0);
      ctx.restore();
      canvas.toBlob((blob) => {
        if (blob) {
          setCaptureStatus('Photo captured!');
          onCapture(blob);
        } else {
          setError('Failed to capture photo. Please try again.');
        }
      }, 'image/jpeg', 0.95);
      return true;
    };

    if (doCapture()) return;

    // Poll every 200ms up to 3 seconds
    setCaptureStatus('Waiting for camera...');
    let attempts = 0;
    const poll = setInterval(() => {
      attempts++;
      if (doCapture()) {
        clearInterval(poll);
        setCaptureStatus('');
      } else if (attempts >= 15) {
        clearInterval(poll);
        setCaptureStatus('');
        setError('Camera not producing frames. Try restarting the camera or use a different browser.');
      }
    }, 200);
  };

  const startRecording = () => {
    if (!stream || !isCameraActive) return;

    // Determine best supported MIME type
    const mimeTypes = mode === 'audio'
      ? ['audio/webm;codecs=opus', 'audio/webm', 'audio/ogg;codecs=opus', 'audio/ogg', '']
      : ['video/webm;codecs=vp9,opus', 'video/webm;codecs=vp8,opus', 'video/webm', 'video/mp4', ''];

    const supportedMime = mimeTypes.find(mt => {
      try { return mt === '' || MediaRecorder.isTypeSupported(mt); } catch { return false; }
    }) ?? '';

    try {
      const options = supportedMime ? { mimeType: supportedMime } : {};
      const mediaRecorder = new MediaRecorder(stream, options);
      const chunks: Blob[] = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) chunks.push(event.data);
      };

      mediaRecorder.onstop = () => {
        const mimeType = supportedMime || (mode === 'audio' ? 'audio/webm' : 'video/webm');
        const blob = new Blob(chunks, { type: mimeType });
        if (blob.size === 0) {
          setError('Recording was empty. Please try again.');
          return;
        }
        setCaptureStatus('Recording complete! Uploading...');
        onCapture(blob);
      };

      mediaRecorder.onerror = (e: any) => {
        setError(`Recording error: ${e.error?.message || 'Unknown error'}`);
        setIsRecording(false);
      };

      mediaRecorder.start(100); // Collect data every 100ms
      mediaRecorderRef.current = mediaRecorder;
      setIsRecording(true);
      setCaptureStatus('Recording...');
    } catch (e: any) {
      console.error("MediaRecorder start error:", e);
      setError(`Recording failed: ${e.message}. Try using Chrome browser.`);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  useEffect(() => {
    return () => {
      if (stream) stream.getTracks().forEach(t => t.stop());
    };
  }, [stream]);

  return (
    <div className="w-full max-w-3xl mx-auto">
      <div className="relative aspect-video bg-black rounded-3xl overflow-hidden shadow-2xl border-4 border-gray-900 ring-4 ring-gray-800/50">

        {/* MEDIA FEED */}
        {isCameraActive ? (
          mode === 'audio' ? (
            <div className="absolute inset-0 flex flex-col items-center justify-center bg-gray-900">
               <div className={`w-32 h-32 rounded-full flex items-center justify-center transition-all duration-500 ${isRecording ? 'bg-red-500/20 scale-110' : 'bg-cyan-500/20'}`}>
                 <Mic className={`w-12 h-12 ${isRecording ? 'text-red-500 animate-pulse' : 'text-cyan-500'}`} />
               </div>
               <p className="mt-4 font-mono text-cyan-400 text-xs animate-pulse">Voice Authentication Active</p>
               {captureStatus && <p className="mt-2 text-xs text-gray-400 font-mono">{captureStatus}</p>}
            </div>
          ) : (
            <>
              <video
                ref={videoRef}
                autoPlay
                playsInline
                muted
                onCanPlay={() => {
                  setIsVideoReady(true);
                  setCaptureStatus('Camera ready!');
                  setTimeout(() => setCaptureStatus(''), 1500);
                }}
                onLoadedMetadata={() => {
                  if (videoRef.current && videoRef.current.videoWidth > 0) {
                    setIsVideoReady(true);
                  }
                }}
                className="w-full h-full object-cover transform scale-x-[-1]"
              />
              <canvas ref={canvasRef} className="hidden" />
              {captureStatus && (
                <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-black/70 text-white text-sm font-mono px-4 py-2 rounded-full">
                  {captureStatus}
                </div>
              )}
            </>
          )
        ) : (
          <div className="absolute inset-0 flex flex-col items-center justify-center bg-gray-950 text-gray-500">
            {mode === 'audio' ? <Mic className="w-20 h-20 mb-4 opacity-20" /> : <CameraIcon className="w-20 h-20 mb-4 opacity-20" />}
            <p className="font-mono text-xs uppercase tracking-[0.2em] opacity-50">System Offline</p>
            <p className="font-mono text-[10px] mt-2 opacity-30 text-center px-4">
              Click the button below to initialize {mode === 'audio' ? 'microphone' : 'camera'}
            </p>
          </div>
        )}

        {/* OVERLAYS */}
        <div className="absolute top-6 left-6 z-20 flex flex-col gap-2">
           {isRecording && (
             <div className="flex items-center gap-2 bg-red-500/90 text-white px-3 py-1.5 rounded-full backdrop-blur-md shadow-lg animate-pulse">
               <div className="w-2 h-2 bg-white rounded-full" />
               <span className="text-xs font-bold font-mono tracking-widest uppercase">{mode === 'audio' ? 'Recording Voice' : 'Recording Video'}</span>
             </div>
           )}
           {isCameraActive && !isRecording && (
              <div className="px-3 py-1 bg-black/40 backdrop-blur-md rounded-full border border-white/10">
                 <span className="text-[10px] font-mono text-green-400 tracking-wider flex items-center gap-1 uppercase">
                   <span className="w-1.5 h-1.5 rounded-full bg-green-500" /> Secure {mode} Node
                 </span>
              </div>
           )}
        </div>

        {/* CONTROLS */}
        <div className="absolute bottom-0 left-0 right-0 p-8 pt-24 bg-gradient-to-t from-black/80 via-black/40 to-transparent flex justify-center items-end z-20">

          {isCameraActive && (
            <div className="relative group">
               <div className={`
                 rounded-full p-1 border-4 transition-all duration-300
                 ${isRecording ? 'border-red-500/50 scale-110' : 'border-white/80 hover:border-white hover:scale-105'}
               `}>
                 <button
                   suppressHydrationWarning
                   onClick={() => {
                     if (mode === 'photo') takePhoto();
                     else if (isRecording) stopRecording();
                     else startRecording();
                   }}
                   disabled={mode === 'photo' && !isVideoReady}
                   className={`
                     w-16 h-16 rounded-full flex items-center justify-center transition-all duration-300 shadow-xl
                     ${isRecording ? 'bg-red-500 rounded-lg scale-50' : (mode === 'photo' && !isVideoReady) ? 'bg-gray-600 cursor-not-allowed' : 'bg-white hover:bg-gray-100 active:scale-95'}
                   `}
                 >
                   {!isRecording && (
                     mode === 'photo' ? <CameraIcon className={isVideoReady ? 'text-black' : 'text-gray-400'} /> :
                     mode === 'audio' ? <Mic className="text-black" /> :
                     <VideoIcon className="text-black" />
                   )}
                 </button>
               </div>
               <p className="absolute -bottom-8 left-1/2 -translate-x-1/2 text-[10px] text-white/50 uppercase tracking-widest font-bold whitespace-nowrap">
                 {mode === 'photo' ? (isVideoReady ? 'Shoot' : 'Loading...') : isRecording ? 'Stop' : 'Capture'}
               </p>
            </div>
          )}

          <div className={`${isCameraActive ? 'absolute right-8 bottom-8' : 'relative'}`}>
             <button
               suppressHydrationWarning
               onClick={isCameraActive ? stopMedia : startMedia}
               className={`group flex items-center gap-2 px-6 py-3 rounded-full backdrop-blur-md border transition-all duration-300 shadow-lg
                ${isCameraActive ? 'bg-red-500/10 border-red-500/50 text-red-400 hover:bg-red-500 hover:text-white' : 'bg-cyan-500/10 border-cyan-500/50 text-cyan-400 hover:bg-cyan-500 hover:text-white scale-110'}`}
             >
               <Power className="w-5 h-5" />
               <span className="text-sm font-bold uppercase tracking-wider">{isCameraActive ? 'Offline' : `Init ${mode}`}</span>
             </button>
          </div>
        </div>
      </div>

      {error && (
        <div className="mt-4 p-4 rounded-xl bg-red-500/10 border border-red-500/20 flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-red-500 mt-0.5 flex-shrink-0" />
            <div>
              <p className="text-sm text-red-400 font-medium">{error}</p>
              {error.includes('permission') && (
                <p className="text-xs text-red-400/70 mt-1">
                  In Chrome: Click the 🔒 lock icon in the address bar → Permissions → Allow Camera & Microphone
                </p>
              )}
            </div>
        </div>
      )}
    </div>
  );
}
