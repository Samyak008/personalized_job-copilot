'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useMutation } from '@tanstack/react-query';
import { Loader2, ArrowLeft } from 'lucide-react';
import api from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from '@/components/ui/card';
import { Resume } from '@/types';
import { ProgressStepper, Step } from '@/components/ui/progress-stepper';

interface JobInputProps {
    resume: Resume;
    onCancel: () => void;
}

const ANALYSIS_STEPS: Step[] = [
    { id: 'parse', label: 'Parsing Job Description', status: 'pending' },
    { id: 'analyze', label: 'Analyzing Skill Fit', status: 'pending' },
    { id: 'strategy', label: 'Formulating Strategy', status: 'pending' },
    { id: 'generate', label: 'Drafting Outreach', status: 'pending' },
];

export default function JobInput({ resume, onCancel }: JobInputProps) {
    const router = useRouter();
    const [jobDescription, setJobDescription] = useState('');
    const [steps, setSteps] = useState<Step[]>(ANALYSIS_STEPS);
    const [isAnalyzing, setIsAnalyzing] = useState(false);

    // Simulate progress while API is running
    useEffect(() => {
        if (!isAnalyzing) return;

        let currentStepIndex = 0;

        const updateStep = (index: number, status: Step['status']) => {
            setSteps(prev => prev.map((s, i) => i === index ? { ...s, status } : s));
        };

        // Start first step
        updateStep(0, 'inprogress');

        const interval = setInterval(() => {
            if (currentStepIndex >= 3) {
                clearInterval(interval);
                return;
            }

            // Complete current step
            updateStep(currentStepIndex, 'completed');
            currentStepIndex++;
            // Start next step
            updateStep(currentStepIndex, 'inprogress');
        }, 3500); // Advance every 3.5s (simulated)

        return () => clearInterval(interval);
    }, [isAnalyzing]);

    const analysisMutation = useMutation({
        mutationFn: async () => {
            setIsAnalyzing(true);
            const res = await api.post('/analyses/', {
                resume_id: resume.id,
                job_description: jobDescription
            });
            return res.data;
        },
        onSuccess: (data) => {
            // Mark all complete
            setSteps(prev => prev.map(s => ({ ...s, status: 'completed' })));

            // Small delay to show completion before redirect
            setTimeout(() => {
                router.push(`/analysis/${data.id}`);
            }, 1000);
        },
        onError: (error) => {
            console.error(error);
            setIsAnalyzing(false);
            setSteps(ANALYSIS_STEPS.map(s => ({ ...s, status: 'pending' }))); // Reset
            alert('Analysis failed. check console.');
        }
    });

    return (
        <div className="space-y-4 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <Button variant="ghost" onClick={onCancel} className="mb-2" disabled={isAnalyzing}>
                <ArrowLeft className="mr-2 h-4 w-4" /> Back
            </Button>

            <Card>
                <CardHeader>
                    <CardTitle>Analyze Job for: {resume.filename}</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                    {isAnalyzing ? (
                        <div className="py-8 px-4 flex justify-center">
                            <ProgressStepper steps={steps} className="w-full max-w-md" />
                        </div>
                    ) : (
                        <div className="space-y-2">
                            <label className="text-sm font-medium">Job Description</label>
                            <textarea
                                className="flex min-h-[200px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                                placeholder="Paste the job description here..."
                                value={jobDescription}
                                onChange={(e) => setJobDescription(e.target.value)}
                            />
                        </div>
                    )}
                </CardContent>
                {!isAnalyzing && (
                    <CardFooter>
                        <Button
                            className="w-full"
                            onClick={() => analysisMutation.mutate()}
                            disabled={!jobDescription.trim()}
                        >
                            Run Analysis
                        </Button>
                    </CardFooter>
                )}
            </Card>
        </div>
    );
}
