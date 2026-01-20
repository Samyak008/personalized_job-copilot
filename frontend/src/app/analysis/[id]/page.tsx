'use client';

import { useParams, useRouter } from 'next/navigation';
import { useQuery } from '@tanstack/react-query';
import { ArrowLeft, Loader2 } from 'lucide-react';
import api from '@/lib/api';
import { Button } from '@/components/ui/button';
import AnalysisResults from '@/components/features/AnalysisResults';
import { Analysis } from '@/types';

export default function AnalysisPage() {
    const params = useParams();
    const router = useRouter();
    const id = params?.id as string;

    const { data: analysis, isLoading, error } = useQuery<Analysis>({
        queryKey: ['analysis', id],
        queryFn: async () => {
            const res = await api.get(`/analyses/${id}`);
            return res.data;
        },
        enabled: !!id,
    });

    if (isLoading) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-gray-50">
                <div className="text-center">
                    <Loader2 className="h-10 w-10 animate-spin text-primary mx-auto mb-4" />
                    <p className="text-gray-500">Loading analysis results...</p>
                </div>
            </div>
        );
    }

    if (error || !analysis) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-gray-50">
                <div className="text-center">
                    <h2 className="text-xl font-bold text-red-600 mb-2">Error Loading Analysis</h2>
                    <p className="text-gray-600 mb-4">Could not fetch the analysis details.</p>
                    <Button onClick={() => router.back()}>Go Back</Button>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-50 p-6">
            <div className="max-w-5xl mx-auto">
                <div className="mb-6">
                    <Button variant="ghost" onClick={() => router.push('/dashboard')}>
                        <ArrowLeft className="mr-2 h-4 w-4" /> Back to Dashboard
                    </Button>
                </div>

                <header className="mb-8">
                    <h1 className="text-3xl font-bold text-gray-900">Analysis Results</h1>
                    <p className="text-gray-500">
                        Res: {analysis.resume_id} • Date: {new Date(analysis.created_at).toLocaleDateString()}
                    </p>
                </header>

                <AnalysisResults analysis={analysis} />
            </div>
        </div>
    );
}
