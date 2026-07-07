const API_BASE = "http://localhost:8000";

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

export async function fetchProblems(): Promise<Problem[]> {
    const res = await fetch(`${API_BASE}/problems/`);
    if (!res.ok) throw new Error("Failed to fetch problems");
    const data = await res.json();
    return data.problems;
}

export async function fetchProblemById(id: string): Promise<Problem> {
    const res = await fetch(`${API_BASE}/problems/${id}`);
    if (!res.ok) throw new Error("Problem not found");
    return await res.json();
}