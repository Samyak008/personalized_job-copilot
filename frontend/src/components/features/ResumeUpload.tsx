'use client';

import { useState } from 'react';
import { Upload, Loader2, FileText, CheckCircle } from 'lucide-react';
import api from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { cn } from '@/lib/utils';

interface ResumeUploadProps {
    onUploadSuccess?: () => void;
}

export default function ResumeUpload({ onUploadSuccess }: ResumeUploadProps) {
    const [isDragging, setIsDragging] = useState(false);
    const [uploading, setUploading] = useState(false);
    const [file, setFile] = useState<File | null>(null);

    const handleDrag = (e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === 'dragenter' || e.type === 'dragover') {
            setIsDragging(true);
        } else if (e.type === 'dragleave') {
            setIsDragging(false);
        }
    };

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        setIsDragging(false);
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            validateAndSetFile(e.dataTransfer.files[0]);
        }
    };

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            validateAndSetFile(e.target.files[0]);
        }
    };

    const validateAndSetFile = (file: File) => {
        if (file.type === 'application/pdf' || file.name.endsWith('.docx') || file.name.endsWith('.pdf')) {
            setFile(file);
        } else {
            alert('Only PDF and DOCX files are allowed.');
        }
    };

    const handleUpload = async () => {
        if (!file) return;

        setUploading(true);
        const formData = new FormData();
        formData.append('file', file);

        try {
            await api.post('/resumes/upload', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });
            setFile(null);
            if (onUploadSuccess) onUploadSuccess();
        } catch (error) {
            console.error('Upload failed:', error);
            alert('Failed to upload resume.');
        } finally {
            setUploading(false);
        }
    };

    return (
        <Card className="w-full">
            <CardContent className="p-6">
                <div
                    className={cn(
                        "border-2 border-dashed rounded-lg p-8 text-center transition-colors cursor-pointer",
                        isDragging ? "border-primary bg-primary/5" : "border-gray-300 hover:border-primary",
                        file ? "bg-green-50 border-green-200" : ""
                    )}
                    onDragEnter={handleDrag}
                    onDragLeave={handleDrag}
                    onDragOver={handleDrag}
                    onDrop={handleDrop}
                    onClick={() => !file && document.getElementById('resume-upload')?.click()}
                >
                    <input
                        id="resume-upload"
                        type="file"
                        className="hidden"
                        accept=".pdf,.docx"
                        onChange={handleFileChange}
                        disabled={uploading || !!file}
                    />

                    {!file ? (
                        <div className="flex flex-col items-center gap-2">
                            <Upload className="h-10 w-10 text-gray-400" />
                            <p className="text-sm font-medium text-gray-700">
                                Drag & drop your resume (PDF/DOCX)
                            </p>
                            <p className="text-xs text-gray-500">or click to browse</p>
                        </div>
                    ) : (
                        <div className="flex flex-col items-center gap-2">
                            <FileText className="h-10 w-10 text-green-600" />
                            <p className="text-sm font-medium text-gray-900">{file.name}</p>
                            <div className="flex gap-2 mt-2">
                                <Button
                                    size="sm"
                                    onClick={(e) => { e.stopPropagation(); handleUpload(); }}
                                    disabled={uploading}
                                >
                                    {uploading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                                    {uploading ? 'Processing...' : 'Start Analysis'}
                                </Button>
                                <Button
                                    variant="ghost"
                                    size="sm"
                                    disabled={uploading}
                                    onClick={(e) => { e.stopPropagation(); setFile(null); }}
                                >
                                    Change
                                </Button>
                            </div>
                        </div>
                    )}
                </div>
            </CardContent>
        </Card>
    );
}
