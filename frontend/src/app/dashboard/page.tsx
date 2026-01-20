'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { supabase } from '@/lib/supabase';
import { useQueryClient } from '@tanstack/react-query';
import ResumeUpload from '@/components/features/ResumeUpload';
import ResumeList from '@/components/features/ResumeList';
import JobInput from '@/components/features/JobInput';
import AnalysisList from '@/components/features/AnalysisList';
import { Resume } from '@/types';
import { Button } from '@/components/ui/button';
import { LogOut } from 'lucide-react';

export default function DashboardPage() {
    const router = useRouter();
    const queryClient = useQueryClient();
    const [selectedResume, setSelectedResume] = useState<Resume | null>(null);
    const [userEmail, setUserEmail] = useState<string>('');

    useEffect(() => {
        // Check auth
        supabase.auth.getUser().then(({ data: { user } }) => {
            if (!user) {
                router.push('/auth');
            } else {
                setUserEmail(user.email || '');
            }
        });
    }, [router]);

    const handleLogout = async () => {
        await supabase.auth.signOut();
        router.push('/auth');
    };

    const handleResumeUploaded = () => {
        queryClient.invalidateQueries({ queryKey: ['resumes'] });
    };

    return (
        <div className="min-h-screen bg-gray-50 p-6">
            <header className="flex justify-between items-center mb-8 max-w-6xl mx-auto">
                <div>
                    <h1 className="text-3xl font-bold text-gray-900">ApplyWise</h1>
                    <p className="text-gray-500">Welcome, {userEmail}</p>
                </div>
                <Button variant="outline" onClick={handleLogout}>
                    <LogOut className="mr-2 h-4 w-4" /> Sign Out
                </Button>
            </header>

            <main className="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-8">
                {/* Left Column: Resumes & Analysis Flow */}
                <div className="md:col-span-2 space-y-6">
                    {selectedResume ? (
                        <JobInput
                            resume={selectedResume}
                            onCancel={() => setSelectedResume(null)}
                        />
                    ) : (
                        <>
                            <section className="space-y-4">
                                <h2 className="text-xl font-semibold">Upload Resume</h2>
                                <ResumeUpload onUploadSuccess={handleResumeUploaded} />
                            </section>

                            <section className="space-y-4">
                                <h2 className="text-xl font-semibold">My Resumes</h2>
                                <ResumeList onSelectResume={setSelectedResume} />
                            </section>
                        </>
                    )}
                </div>

                {/* Right Column: History */}
                <div className="space-y-6">
                    <section>
                        <h2 className="text-xl font-semibold mb-4">Recent Analyses</h2>
                        <AnalysisList />
                    </section>
                </div>
            </main>
        </div>
    );
}
