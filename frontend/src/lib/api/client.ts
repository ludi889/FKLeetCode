import type { Problem, Session, ProblemVariant, SubmitCodeResponse } from '$lib/types';
const API_BASE = "http://localhost:8000";



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



export async function createSession(problemId?: string): Promise<Session> {
    // If you need to pass a specific problem ID to generate a variant, 
    // you can attach it to the body. Otherwise, send an empty POST.
    const res = await fetch(`${API_BASE}/sessions/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: problemId ? JSON.stringify({ problem_id: problemId }) : undefined
    });
    
    if (!res.ok) {
        throw new Error(`Failed to create session: ${res.statusText}`);
    }
    
    return await res.json();
}

export async function fetchSessionById(id: string): Promise<Session> {
    const res = await fetch(`${API_BASE}/sessions/${id}`);
    if (!res.ok) throw new Error("Session not found");
    return await res.json();
}

export async function fetchVariantById(id: string): Promise<ProblemVariant> {
    const res = await fetch(`${API_BASE}/variants/${id}`);
    if (!res.ok) throw new Error("Variant not found");
    return await res.json();
}

export async function startSession(id: string): Promise<Session> {
    const res = await fetch(`${API_BASE}/sessions/${id}/start`, { method: 'POST' });
    if (!res.ok) throw new Error("Failed to start session");
    return await res.json();
}

export async function submitCode(id: string, code: string): Promise<SubmitCodeResponse> {
    const res = await fetch(`${API_BASE}/sessions/${id}/submit`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code })
    });
    
    if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Failed to submit code");
    }
    
    return await res.json();
}

export async function stopSession(id: string): Promise<Session> {
    const res = await fetch(`${API_BASE}/sessions/${id}/stop`, { method: 'POST' });
    if (!res.ok) throw new Error("Failed to stop session");
    return await res.json();
}