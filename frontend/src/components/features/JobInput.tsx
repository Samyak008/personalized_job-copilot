'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useMutation } from '@tanstack/react-query';
import { Loader2, ArrowLeft } from 'lucide-react';
import api from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from '@/components/ui/card';
import { Resume } from '@/types';

interface JobInputProps {
    resume: Resume;
    onCancel: () => void;
}

export default function JobInput({ resume, onCancel }: JobInputProps) {
    const router = useRouter();
    const [jobDescription, setJobDescription] = useState('');

    const analysisMutation = useMutation({
        mutationFn: async () => {
            const res = await api.post('/analyses/', {
                resume_id: resume.id,
                job_description: jobDescription
            });
            return res.data;
        },
        onSuccess: (data) => {
            // Redirect to analysis results
            router.push(`/analysis/${data.id}`);
        },
        onError: (error) => {
            console.error(error);
            alert('Analysis failed. check console.');
        }
    });

    return (
        <div className="space-y-4 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <Button variant="ghost" onClick={onCancel} className="mb-2">
                <ArrowLeft className="mr-2 h-4 w-4" /> Back
            </Button>

            <Card>
                <CardHeader>
                    <CardTitle>Analyze Job for: {resume.filename}</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                    <div className="space-y-2">
                        <label className="text-sm font-medium">Job Description</label>
                        <textarea
                            className="flex min-h-[200px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                            placeholder="Paste the job description here..."
                            value={jobDescription}
                            onChange={(e) => setJobDescription(e.target.value)}
                        />
                    </div>
                </CardContent>
                <CardFooter>
                    <Button
                        className="w-full"
                        onClick={() => analysisMutation.mutate()}
                        disabled={!jobDescription.trim() || analysisMutation.isPending}
                    >
                        {analysisMutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                        {analysisMutation.isPending ? 'Analyzing (this may take 10-20s)...' : 'Run Analysis'}
                    </Button>
                </CardFooter>
            </Card>
        </div>
    );
}
