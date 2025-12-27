import { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { API_ENDPOINTS } from '../config';
import { handleApiError, retryRequest } from '../utils/errorHandler';

interface ImageUploadProps {
  onUpload: (imageId: string, imageUrl?: string) => void;
}

export default function ImageUpload({ onUpload }: ImageUploadProps) {
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadedImage, setUploadedImage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (!file) return;

    // Validate file type
    if (!file.type.startsWith('image/')) {
      setError('Please select an image file');
      return;
    }

    // Validate file size (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
      setError('File size must be less than 10MB');
      return;
    }

    setIsUploading(true);
    setError(null);
    setUploadProgress(0);

    try {
      // Create FormData
      const formData = new FormData();
      formData.append('file', file);

      // Simulate upload progress
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 10;
        });
      }, 200);

      // Upload to backend with retry logic
      const result = await retryRequest(async () => {
        const response = await fetch(API_ENDPOINTS.UPLOAD_IMAGE, {
          method: 'POST',
          body: formData,
        });

        if (!response.ok) {
          const errorText = await response.text();
          throw new Error(`Upload failed: ${response.status} - ${errorText}`);
        }

        return response.json();
      });

      clearInterval(progressInterval);
      setUploadProgress(100);

      const imageUrl = URL.createObjectURL(file);
      setUploadedImage(imageUrl);
      onUpload(result.image_id, imageUrl);
      
    } catch (err) {
      setError(handleApiError(err));
    } finally {
      setIsUploading(false);
    }
  }, [onUpload]);

  const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png', '.gif', '.bmp', '.webp']
    },
    maxFiles: 1,
    disabled: isUploading
  });

  return (
    <div className="p-6 border border-gray-300 rounded-lg max-w-md mx-auto mt-8 bg-white shadow">
      <h2 className="text-xl font-semibold mb-4 text-center">Upload Window Image</h2>
      
      <div className="space-y-4">
        <div
          {...getRootProps()}
          className={`
            border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-all duration-200
            ${isDragActive && !isDragReject 
              ? 'border-blue-500 bg-blue-50' 
              : isDragReject 
                ? 'border-red-500 bg-red-50' 
                : 'border-gray-300 hover:border-gray-400 hover:bg-gray-50'
            }
            ${isUploading ? 'opacity-50 cursor-not-allowed' : ''}
          `}
        >
          <input {...getInputProps()} />
          
          <div className="space-y-2">
            <div className="text-4xl mb-2">
              {isDragActive && !isDragReject ? '📁' : '📸'}
            </div>
            
            {isDragActive && !isDragReject ? (
              <p className="text-blue-600 font-medium">Drop the image here...</p>
            ) : isDragReject ? (
              <p className="text-red-600 font-medium">Invalid file type!</p>
            ) : (
              <>
                <p className="text-gray-600 font-medium">
                  Drag & drop an image here, or click to select
                </p>
                <p className="text-sm text-gray-500">
                  Supports: JPG, PNG, GIF, BMP, WebP (max 10MB)
                </p>
              </>
            )}
          </div>
        </div>

        {isUploading && (
          <div className="space-y-2">
            <div className="w-full bg-gray-200 rounded h-2">
              <div
                className="bg-blue-500 h-2 rounded transition-all duration-300"
                style={{ width: `${uploadProgress}%` }}
              ></div>
            </div>
            <p className="text-sm text-gray-600 text-center">
              Uploading... {uploadProgress}%
            </p>
          </div>
        )}

        {uploadedImage && (
          <div className="mt-4 p-4 bg-green-100 text-green-800 rounded-lg text-center">
            <div className="flex items-center justify-center space-x-2">
              <span className="text-xl">✅</span>
              <span className="font-medium">Uploaded successfully!</span>
            </div>
            <a 
              href={uploadedImage} 
              target="_blank" 
              rel="noopener noreferrer" 
              className="inline-block mt-2 text-blue-700 underline hover:text-blue-900"
            >
              View Image
            </a>
          </div>
        )}

        {error && (
          <div className="mt-4 p-4 bg-red-100 text-red-800 rounded-lg text-center">
            <div className="flex items-center justify-center space-x-2">
              <span className="text-xl">❌</span>
              <span>{error}</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
} 