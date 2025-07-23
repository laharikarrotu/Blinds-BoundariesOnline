import { useState } from 'react';

interface ImageUploadProps {
  onUpload: (imageId: string) => void;
}

export default function ImageUpload({ onUpload }: ImageUploadProps) {
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadedImage, setUploadedImage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
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
      formData.append('image', file);

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

      // Upload to backend
      const response = await fetch('http://localhost:8000/upload', {
        method: 'POST',
        body: formData,
      });

      clearInterval(progressInterval);
      setUploadProgress(100);

      if (!response.ok) {
        throw new Error('Upload failed');
      }

      const result = await response.json();
      setUploadedImage(URL.createObjectURL(file));
      onUpload(result.image_id);
      
    } catch (err) {
      setError('Failed to upload image. Please try again.');
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="p-6 border border-gray-300 rounded-lg max-w-md mx-auto mt-8 bg-white shadow">
      <h2 className="text-xl font-semibold mb-4 text-center">Upload Window Image</h2>
      
      <div className="space-y-4">
        <input
          type="file"
          accept="image/*"
          onChange={handleFileChange}
          disabled={isUploading}
          className="block w-full mb-4 text-sm text-gray-700 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 disabled:opacity-50"
        />

        {isUploading && (
          <div className="w-full bg-gray-200 rounded h-2 mt-4">
            <div
              className="bg-blue-500 h-2 rounded transition-all"
              style={{ width: `${uploadProgress}%` }}
            ></div>
          </div>
        )}

        {uploadedImage && (
          <div className="mt-4 p-3 bg-green-100 text-green-800 rounded text-center">
            ✅ Uploaded! <a href={uploadedImage} target="_blank" rel="noopener noreferrer" className="underline text-blue-700">View Image</a>
          </div>
        )}

        {error && (
          <div className="mt-4 p-3 bg-red-100 text-red-800 rounded text-center">
            ❌ {error}
          </div>
        )}
      </div>
    </div>
  );
} 