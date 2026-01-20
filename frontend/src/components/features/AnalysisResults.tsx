'use client';

import { useState } from 'react';
import { CheckCircle, XCircle, Copy, FileText, Linkedin, Mail, MessageSquare } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Analysis } from '@/types';

interface AnalysisResultsProps {
    analysis: Analysis;
}

export default function AnalysisResults({ analysis }: AnalysisResultsProps) {
    const [activeTab, setActiveTab] = useState<'email' | 'linkedin' | 'strategy'>('email');

    // Safe access to content
    const matchScore = analysis.match_score || 0;
    const skillGaps = analysis.skill_gaps || [];
    const suggestions = analysis.suggestions || [];
    const interviewQuestions = analysis.interview_questions || [];

    const copyToClipboard = (text: string) => {
        navigator.clipboard.writeText(text);
        alert('Copied to clipboard!');
    };

    return (
        <div className="space-y-8">
            {/* 1. Score & Overview */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <Card className="md:col-span-1 border-primary/20 bg-primary/5">
                    <CardContent className="flex flex-col items-center justify-center py-8">
                        <div className="relative h-32 w-32 flex items-center justify-center rounded-full border-8 border-primary/20 bg-background text-4xl font-bold text-primary">
                            {matchScore.toFixed(0)}%
                        </div>
                        <p className="mt-4 text-center font-medium text-muted-foreground">Match Score</p>
                    </CardContent>
                </Card>

                <Card className="md:col-span-2">
                    <CardHeader>
                        <CardTitle>Skill Gap Analysis</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-4">
                            {skillGaps.length === 0 ? (
                                <p className="text-green-600 flex items-center">
                                    <CheckCircle className="mr-2 h-5 w-5" /> Perfect match! No critical gaps found.
                                </p>
                            ) : (
                                skillGaps.map((gap, i) => (
                                    <div key={i} className="flex items-start p-3 bg-red-50 rounded border border-red-100">
                                        <XCircle className="h-5 w-5 text-red-500 mt-0.5 mr-3 flex-shrink-0" />
                                        <div>
                                            <p className="font-bold text-red-700">{gap.skill}</p>
                                            <p className="text-sm text-red-600 mt-1">{gap.recommendation}</p>
                                            <div className="mt-2 flex gap-2">
                                                <span className="text-xs font-semibold px-2 py-0.5 bg-red-100 text-red-700 rounded uppercase">
                                                    {gap.importance} Priority
                                                </span>
                                            </div>
                                        </div>
                                    </div>
                                ))
                            )}
                        </div>
                    </CardContent>
                </Card>
            </div>

            {/* 2. Generated Content Tabs */}
            <Card>
                <CardHeader>
                    <CardTitle>Generated Application Content</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="flex space-x-2 border-b mb-6 overflow-x-auto">
                        <button
                            onClick={() => setActiveTab('email')}
                            className={`px-4 py-2 border-b-2 font-medium text-sm transition-colors whitespace-nowrap ${activeTab === 'email' ? 'border-primary text-primary' : 'border-transparent text-gray-500 hover:text-gray-700'}`}
                        >
                            <Mail className="inline h-4 w-4 mr-2" /> Cold Email
                        </button>
                        <button
                            onClick={() => setActiveTab('linkedin')}
                            className={`px-4 py-2 border-b-2 font-medium text-sm transition-colors whitespace-nowrap ${activeTab === 'linkedin' ? 'border-primary text-primary' : 'border-transparent text-gray-500 hover:text-gray-700'}`}
                        >
                            <Linkedin className="inline h-4 w-4 mr-2" /> LinkedIn Message
                        </button>
                        <button
                            onClick={() => setActiveTab('strategy')}
                            className={`px-4 py-2 border-b-2 font-medium text-sm transition-colors whitespace-nowrap ${activeTab === 'strategy' ? 'border-primary text-primary' : 'border-transparent text-gray-500 hover:text-gray-700'}`}
                        >
                            <FileText className="inline h-4 w-4 mr-2" /> Improvement Strategy
                        </button>
                    </div>

                    <div className="min-h-[300px] relative">
                        <Button
                            variant="ghost"
                            size="sm"
                            className="absolute right-0 top-0"
                            onClick={() => {
                                const text = activeTab === 'email' ? analysis.cold_email
                                    : activeTab === 'linkedin' ? analysis.linkedin_dm
                                        : suggestions.join('\n');
                                copyToClipboard(text || '');
                            }}
                        >
                            <Copy className="h-4 w-4 mr-2" /> Copy
                        </Button>

                        <div className="pt-8">
                            {activeTab === 'email' && (
                                <div className="p-4 bg-gray-50 rounded whitespace-pre-wrap text-sm leading-relaxed font-mono">
                                    {analysis.cold_email || "No email generated (likely due to AI constraints). Try regenerating."}
                                </div>
                            )}

                            {activeTab === 'linkedin' && (
                                <div className="p-4 bg-gray-50 rounded whitespace-pre-wrap text-sm leading-relaxed font-mono">
                                    {analysis.linkedin_dm || "No message generated."}
                                </div>
                            )}

                            {activeTab === 'strategy' && (
                                <div className="space-y-6">
                                    <div>
                                        <h4 className="font-bold flex items-center mb-3">
                                            <FileText className="h-4 w-4 mr-2 text-primary" /> Resume Improvements
                                        </h4>
                                        <ul className="list-disc pl-5 space-y-2 text-sm">
                                            {suggestions.length > 0 ? suggestions.map((s, i) => (
                                                <li key={i}>{s}</li>
                                            )) : <li className="text-gray-500">No specific improvements found.</li>}
                                        </ul>
                                    </div>

                                    {interviewQuestions.length > 0 && (
                                        <div>
                                            <h4 className="font-bold flex items-center mb-3">
                                                <MessageSquare className="h-4 w-4 mr-2 text-primary" /> Interview Prep
                                            </h4>
                                            <ul className="list-disc pl-5 space-y-2 text-sm italic text-gray-700">
                                                {interviewQuestions.map((q, i) => (
                                                    <li key={i}>{q}</li>
                                                ))}
                                            </ul>
                                        </div>
                                    )}
                                </div>
                            )}
                        </div>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}
