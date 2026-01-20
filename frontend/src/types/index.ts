export interface Resume {
    id: string;
    filename: string;
    created_at: string;
    parsed_data: Record<string, any>; // Simplified
}

export interface SkillGap {
    skill: string;
    importance: 'high' | 'medium' | 'low';
    current_level: string;
    recommendation: string;
}

export interface Analysis {
    id: string;
    resume_id: string;
    job_description: string;
    job_url?: string;

    match_score: number;
    skill_gaps: SkillGap[];
    suggestions: string[]; // Resume improvements

    cold_email?: string;
    linkedin_dm?: string;
    interview_questions: string[];

    created_at: string;
}

export interface AnalysisRequest {
    resume_id: string;
    job_description: string;
}
