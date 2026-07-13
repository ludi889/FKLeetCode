export interface Problem {
    id: string;
    title: string;
    statement: string;
    difficulty: string;
    tags: Record<string, string[]>;
    constraints: Record<string, any>;
    signature: Record<string, any>;
    test_cases: Record<string, any>;
}
export interface Session {
    id: string;
    problem_variant_id: string;
    status: string;
    started_at: string | null;
    ended_at: string | null;
}

export interface ProblemVariant {
    id: string;
    problem_id: string;
    scenario_context: string;
    stage_1_mvp: string;
    stage_2_curveball: string;
    stage_3_system: string;
}

export interface SubmitCodeResponse {
    job_id: string;
}