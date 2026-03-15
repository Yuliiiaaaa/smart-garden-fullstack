import { useDropzone } from 'react-dropzone';
import { useState } from 'react';
import { uploadFile } from '../services/fileService';

interface FileUploaderProps {
  onUploadSuccess: (key: string) => void;
}

export function FileUploader({ onUploadSuccess }: FileUploaderProps) {
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');

  const onDrop = async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (!file) return;
    setUploading(true);
    try {
      const { key } = await uploadFile(file);
      onUploadSuccess(key);
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('Произошла неизвестная ошибка');
      }
    } finally {
      setUploading(false);
    }
  };

  const { getRootProps, getInputProps } = useDropzone({
    onDrop,
    accept: { 'image/*': ['.jpeg', '.jpg', '.png'] },
    maxSize: 10 * 1024 * 1024,
    multiple: false,
  });

  return (
    <div {...getRootProps()} style={{ border: '2px dashed #ccc', padding: '20px', textAlign: 'center' }}>
      <input {...getInputProps()} />
      {uploading ? <p>Загрузка...</p> : <p>Перетащите файл или нажмите для выбора</p>}
      {error && <p style={{ color: 'red' }}>{error}</p>}
    </div>
  );
}