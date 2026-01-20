'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Trash2, FileText, ArrowRight, Loader2 } from 'lucide-react';
import api from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Resume } from '@/types';

interface ResumeListProps {
    onSelectResume: (resume: Resume) => void;
}

export default function ResumeList({ onSelectResume }: ResumeListProps) {
    const queryClient = useQueryClient();

    const { data: resumes, isLoading, error } = useQuery<Resume[]>({
        queryKey: ['resumes'],
        queryFn: async () => {
            const res = await api.get('/resumes/');
            return res.data;
        },
    });

    const deleteMutation = useMutation({
        mutationFn: async (id: string) => {
            await api.delete(`/resumes/${id}`);
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['resumes'] });
        },
    });

    if (isLoading) {
        return (
            <div className="flex justify-center p-8">
                <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
            </div>
        );
    }

    if (error) {
        return <div className="text-red-500 p-4">Failed to load resumes.</div>;
    }

    if (!resumes || resumes.length === 0) {
        return (
            <div className="text-center p-8 text-gray-500">
                No resumes uploaded yet. Upload one to get started!
            </div>
        );
    }

    return (
        <div className="space-y-3">
            {resumes.map((resume) => (
                <Card key={resume.id} className="hover:bg-gray-50 transition-colors">
                    <CardContent className="p-4 flex items-center justify-between">
                        <div className="flex items-center gap-3 overflow-hidden">
                            <div className="bg-blue-100 p-2 rounded-lg">
                                <FileText className="h-5 w-5 text-blue-600" />
                            </div>
                            <div className="min-w-0">
                                <p className="font-medium truncate">{resume.filename}</p>
                                <p className="text-xs text-gray-400">
                                    {new Date(resume.created_at).toLocaleDateString()}
                                </p>
                            </div>
                        </div>

                        <div className="flex items-center gap-2">
                            <Button
                                variant="outline"
                                size="sm"
                                onClick={() => onSelectResume(resume)}
                            >
                                Analyze
                                <ArrowRight className="ml-2 h-3 w-3" />
                            </Button>
                            <Button
                                variant="ghost"
                                size="icon"
                                className="text-red-500 hover:text-red-600 hover:bg-red-50"
                                onClick={() => {
                                    if (confirm('Are you sure?')) deleteMutation.mutate(resume.id);
                                }}
                            >
                                <Trash2 className="h-4 w-4" />
                            </Button>
                        </div>
                    </CardContent>
                </Card>
            ))}
        </div>
    );
}
