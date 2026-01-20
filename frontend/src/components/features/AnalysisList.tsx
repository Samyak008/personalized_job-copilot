'use client';

import { useQuery } from '@tanstack/react-query';
import { BarChart2, Calendar, Loader2 } from 'lucide-react';
import Link from 'next/link';
import api from '@/lib/api';
import { Card, CardContent } from '@/components/ui/card';
import { Analysis } from '@/types';

function getScoreColor(score: number) {
    if (score >= 80) return 'text-green-600 bg-green-100';
    if (score >= 60) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
}

export default function AnalysisList() {
    const { data: analyses, isLoading } = useQuery<Analysis[]>({
        queryKey: ['analyses'],
        queryFn: async () => {
            const res = await api.get('/analyses/'); // Note trailing slash from router? Check router.
            return res.data;
        },
    });

    if (isLoading) return <Loader2 className="h-6 w-6 animate-spin text-gray-400" />;

    if (!analyses || analyses.length === 0) {
        return <div className="text-gray-500 text-sm">No analyses run yet.</div>;
    }

    return (
        <div className="space-y-3">
            {analyses.map((analysis) => (
                <Link key={analysis.id} href={`/analysis/${analysis.id}`}>
                    <Card className="hover:bg-gray-50 transition-colors cursor-pointer">
                        <CardContent className="p-4 flex items-center justify-between">
                            <div>
                                <div className="flex items-center gap-2 mb-1">
                                    <span className={`px-2 py-0.5 rounded text-xs font-bold ${getScoreColor(analysis.match_score)}`}>
                                        {analysis.match_score}%
                                    </span>
                                    <span className="font-medium text-sm truncate max-w-[200px]">
                                        Job Analysis
                                    </span>
                                </div>

                                <div className="flex items-center gap-2 text-xs text-gray-400">
                                    <Calendar className="h-3 w-3" />
                                    {new Date(analysis.created_at).toLocaleDateString()}
                                </div>
                            </div>
                            <BarChart2 className="h-5 w-5 text-gray-300" />
                        </CardContent>
                    </Card>
                </Link>
            ))}
        </div>
    );
}
