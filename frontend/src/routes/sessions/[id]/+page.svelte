<script lang="ts">
    import { page } from '$app/stores';
    import { fetchSessionById, fetchProblemById, fetchVariantById, startSession, submitCode, stopSession } from '$lib/api/client';
    import { Button } from '$lib/components/ui/button';
    import { Badge } from '$lib/components/ui/badge';
    import * as Card from '$lib/components/ui/card';
    import { onDestroy } from 'svelte';

    const sessionId = $page.params.id;

    let sessionData = $state<any>(null);
    let problemData = $state<any>(null);
    let variantData = $state<any>(null);

    // Workspace State Management
    let activeStage = $state(1);
    let stage1Code = $state('');
    let stage2Code = $state('');
    let stage3Text = $state('');
    let hasVisitedStage2 = $state(false);

    let isSubmitting = $state(false);
    let isStarting = $state(false);
    let isStopping = $state(false);
    let currentJobId = $state<string | null>(null);
    
    // Timer state
    let timeElapsed = $state(0);
    let timerInterval: ReturnType<typeof setInterval>;
    let formattedTime = $derived(
        `${Math.floor(timeElapsed / 60).toString().padStart(2, '0')}:${(timeElapsed % 60).toString().padStart(2, '0')}`
    );

    async function loadEnvironment() {
        // 1. Fetch data
        const session = await fetchSessionById(sessionId);
        sessionData = session;
        const variant = await fetchVariantById(session.problem_variant_id);
        variantData = variant;
        const problem = await fetchProblemById(variant.problem_id);
        problemData = problem;

        // 2. Initialize Stage 1 Editor
        if (problem.signature) {
            const args = problem.signature.args.map((a: any) => `${a.name}: ${a.type}`).join(', ');
            const boilerplate = `def ${problem.signature.name}(${args}) -> ${problem.signature.returns}:\n    # Your generated scenario starts here\n    pass`;
            stage1Code = boilerplate; 
        }

        // 3. Handle Timer
        if (session.status === 'active' && session.started_at) {
            startClientTimer(session.started_at);
        }
    }

    const loadPromise = loadEnvironment();

    function startClientTimer(startedAtString: string) {
        const startTime = new Date(startedAtString).getTime();
        if (timerInterval) clearInterval(timerInterval);
        timerInterval = setInterval(() => {
            timeElapsed = Math.floor((Date.now() - startTime) / 1000);
        }, 1000);
    }

    function handleStageChange(newStage: number) {
        // Inheritance Logic: The first time they open Stage 2, copy Stage 1's code over.
        if (newStage === 2 && !hasVisitedStage2) {
            stage2Code = stage1Code;
            hasVisitedStage2 = true;
        }
        activeStage = newStage;
    }

    async function handleBeginAssessment() {
        isStarting = true;
        try {
            const updatedSession = await startSession(sessionId);
            sessionData = updatedSession;
            startClientTimer(updatedSession.started_at!);
        } catch (e: any) {
            alert(`Failed to start: ${e.message}`);
        } finally {
            isStarting = false;
        }
    }

    async function handleRunCode() {
        isSubmitting = true;
        try {
            // Dynamically submit the code for the active stage
            const codeToSubmit = activeStage === 1 ? stage1Code : stage2Code;
            const response = await submitCode(sessionId, codeToSubmit);
            currentJobId = response.job_id;
            // TODO: Next step is polling this job_id
        } catch (e: any) {
            alert(`Submission Error: ${e.message}`);
        } finally {
            isSubmitting = false;
        }
    }

    async function handleEndSession() {
        if (!confirm("Are you sure you want to end this session? You will not be able to submit further code.")) return;
        
        isStopping = true;
        try {
            const updatedSession = await stopSession(sessionId);
            sessionData = updatedSession;
            if (timerInterval) clearInterval(timerInterval);
        } catch (e: any) {
            alert(`Failed to end session: ${e.message}`);
        } finally {
            isStopping = false;
        }
    }

    onDestroy(() => {
        if (timerInterval) clearInterval(timerInterval);
    });
</script>

{#await loadPromise}
    <div class="h-screen w-full flex items-center justify-center text-muted-foreground animate-pulse">
        Initializing Dynamic Interview Environment...
    </div>
{:then}
    {#if sessionData.status === 'pending'}
        <div class="max-w-2xl mx-auto mt-24 text-center space-y-6 p-6">
            <Badge variant="outline" class="text-blue-600 border-blue-600 bg-blue-50">Environment Prepared</Badge>
            <h1 class="text-4xl font-bold tracking-tight">{problemData.title}</h1>
            <Button size="lg" class="w-full h-14 text-lg font-bold" onclick={handleBeginAssessment} disabled={isStarting}>
                {isStarting ? 'Unlocking Workspace...' : 'Begin Assessment'}
            </Button>
        </div>

    {:else if sessionData.status === 'active'}
        <div class="flex h-screen w-full overflow-hidden">
            
            <div class="w-full md:w-1/2 h-full border-r flex flex-col overflow-y-auto p-6 space-y-8 bg-slate-50 dark:bg-slate-950/50">
                <div class="flex items-center justify-between pb-4 border-b">
                    <div>
                        <Badge variant="secondary" class="mb-2">System Design & Implementation</Badge>
                        <h1 class="text-2xl font-bold tracking-tight">{problemData.title}</h1>
                    </div>
                    <Badge variant="outline" class="font-mono text-xl px-4 py-1.5 border-primary text-primary shadow-sm">
                        {formattedTime}
                    </Badge>
                </div>

                <div class="space-y-8 pb-12">
                    <section>
                        <h3 class="text-sm font-bold text-muted-foreground uppercase tracking-wider mb-3">Scenario Context</h3>
                        <p class="text-base text-foreground leading-relaxed">{variantData.scenario_context}</p>
                    </section>

                    <section class="bg-blue-50/50 dark:bg-blue-950/20 p-5 rounded-xl border border-blue-100 dark:border-blue-900/50">
                        <div class="flex items-center gap-2 mb-3">
                            <span class="flex h-6 w-6 items-center justify-center rounded-full bg-blue-600 text-white text-xs font-bold">1</span>
                            <h3 class="text-lg font-semibold text-foreground">The MVP</h3>
                        </div>
                        <p class="text-sm text-foreground/90 leading-relaxed whitespace-pre-wrap">{variantData.stage_1_mvp}</p>
                    </section>

                    <section class="bg-amber-50/50 dark:bg-amber-950/20 p-5 rounded-xl border border-amber-100 dark:border-amber-900/50">
                        <div class="flex items-center gap-2 mb-3">
                            <span class="flex h-6 w-6 items-center justify-center rounded-full bg-amber-500 text-white text-xs font-bold">2</span>
                            <h3 class="text-lg font-semibold text-foreground">The Architectural Curveball</h3>
                        </div>
                        <p class="text-sm text-foreground/90 leading-relaxed whitespace-pre-wrap">{variantData.stage_2_curveball}</p>
                    </section>

                    <section class="bg-purple-50/50 dark:bg-purple-950/20 p-5 rounded-xl border border-purple-100 dark:border-purple-900/50">
                        <div class="flex items-center gap-2 mb-3">
                            <span class="flex h-6 w-6 items-center justify-center rounded-full bg-purple-600 text-white text-xs font-bold">3</span>
                            <h3 class="text-lg font-semibold text-foreground">Scale & System Design</h3>
                        </div>
                        <p class="text-sm text-foreground/90 leading-relaxed whitespace-pre-wrap">{variantData.stage_3_system}</p>
                    </section>
                </div>
            </div>

            <div class="w-full md:w-1/2 h-full flex flex-col bg-slate-950 text-slate-50">
                <div class="h-12 border-b border-slate-800 flex items-center justify-between bg-slate-900/80 px-2">
                    <div class="flex h-full">
                        <button 
                            onclick={() => handleStageChange(1)} 
                            class="px-6 h-full text-xs font-semibold tracking-wider uppercase transition-colors {activeStage === 1 ? 'text-blue-400 border-b-2 border-blue-500 bg-slate-800/50' : 'text-slate-500 hover:text-slate-300'}"
                        >
                            1. MVP
                        </button>
                        <button 
                            onclick={() => handleStageChange(2)} 
                            class="px-6 h-full text-xs font-semibold tracking-wider uppercase transition-colors {activeStage === 2 ? 'text-amber-400 border-b-2 border-amber-500 bg-slate-800/50' : 'text-slate-500 hover:text-slate-300'}"
                        >
                            2. Curveball
                        </button>
                        <button 
                            onclick={() => handleStageChange(3)} 
                            class="px-6 h-full text-xs font-semibold tracking-wider uppercase transition-colors {activeStage === 3 ? 'text-purple-400 border-b-2 border-purple-500 bg-slate-800/50' : 'text-slate-500 hover:text-slate-300'}"
                        >
                            3. System
                        </button>
                    </div>

                    <div class="flex items-center gap-2 pr-2">
                        {#if activeStage === 1 || activeStage === 2}
                            <Button size="sm" variant="outline" onclick={handleRunCode} disabled={isSubmitting} class="text-slate-900 text-xs h-8">
                                {isSubmitting ? 'Queueing...' : 'Run Tests'}
                            </Button>
                        {/if}
                        <Button size="sm" onclick={handleEndSession} disabled={isStopping} class="bg-red-600 hover:bg-red-500 text-white text-xs h-8 font-semibold">
                            {isStopping ? 'Ending...' : 'End Session'}
                        </Button>
                    </div>
                </div>

                {#if currentJobId}
                    <div class="bg-slate-900 border-b border-slate-800 p-2 px-4 flex justify-between items-center text-xs font-mono">
                        <span class="text-yellow-500 animate-pulse">Execution Job Queued: {currentJobId.substring(0,8)}...</span>
                        <span class="text-slate-400">Awaiting worker...</span>
                    </div>
                {/if}

                <div class="flex-1 relative p-4">
                    {#if activeStage === 1}
                        <textarea bind:value={stage1Code} spellcheck="false" class="w-full h-full bg-transparent font-mono text-sm leading-relaxed resize-none focus:outline-none border-0 p-0 text-sky-400 selection:bg-slate-800"></textarea>
                    {:else if activeStage === 2}
                        <textarea bind:value={stage2Code} spellcheck="false" class="w-full h-full bg-transparent font-mono text-sm leading-relaxed resize-none focus:outline-none border-0 p-0 text-amber-400 selection:bg-slate-800"></textarea>
                    {:else if activeStage === 3}
                        <textarea bind:value={stage3Text} placeholder="Describe your system architecture, databases, caching strategy, and how you will scale to handle the constraints mentioned in Stage 3..." class="w-full h-full bg-transparent font-sans text-sm leading-relaxed resize-none focus:outline-none border-0 p-0 text-slate-300 selection:bg-slate-800"></textarea>
                    {/if}
                </div>
            </div>
        </div>

    {:else if sessionData.status === 'completed'}
        <div class="max-w-4xl mx-auto mt-12 space-y-8 p-6 pb-24">
            <div class="text-center space-y-4 mb-12">
                <Badge variant="outline" class="text-emerald-600 border-emerald-600 bg-emerald-50">Assessment Finished</Badge>
                <h1 class="text-4xl font-bold tracking-tight">Session Debrief</h1>
                <p class="text-lg text-muted-foreground">
                    Your code is being evaluated. Here is the secret rubric the interviewer was grading you against.
                </p>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <Card.Root>
                    <Card.Header class="bg-slate-50 dark:bg-slate-900/50 border-b">
                        <Card.Title>Technical Expectations</Card.Title>
                    </Card.Header>
                    <Card.Content class="p-6 space-y-4">
                        {#each Object.entries(variantData.technical_rubric) as [key, value]}
                            <div>
                                <h4 class="text-sm font-bold capitalize text-slate-500 mb-1">{key.replace('_', ' ')}</h4>
                                <p class="text-sm font-medium">{value}</p>
                            </div>
                        {/each}
                    </Card.Content>
                </Card.Root>

                <div class="space-y-6">
                    <Card.Root>
                        <Card.Header class="bg-slate-50 dark:bg-slate-900/50 border-b">
                            <Card.Title>System Design Rubric</Card.Title>
                        </Card.Header>
                        <Card.Content class="p-6 space-y-4">
                            {#each Object.entries(variantData.system_rubric) as [key, value]}
                                <div>
                                    <h4 class="text-sm font-bold capitalize text-slate-500 mb-1">{key.replace('_', ' ')}</h4>
                                    <p class="text-sm font-medium">{value}</p>
                                </div>
                            {/each}
                        </Card.Content>
                    </Card.Root>
                    
                    <Card.Root>
                        <Card.Header class="bg-slate-50 dark:bg-slate-900/50 border-b">
                            <Card.Title>Communication Rubric</Card.Title>
                        </Card.Header>
                        <Card.Content class="p-6 space-y-4">
                            {#each Object.entries(variantData.communication_rubric) as [key, value]}
                                <div>
                                    <h4 class="text-sm font-bold capitalize text-slate-500 mb-1">{key.replace('_', ' ')}</h4>
                                    <p class="text-sm font-medium">{value}</p>
                                </div>
                            {/each}
                        </Card.Content>
                    </Card.Root>
                </div>
            </div>

            <div class="pt-8 flex justify-center gap-4">
                <Button href="/problems" variant="outline" size="lg">Return to Library</Button>
            </div>
        </div>
    {/if}
{:catch error}
    <div class="h-screen w-full flex flex-col items-center justify-center gap-4">
        <p class="text-destructive font-semibold">Failed to load session: {error.message}</p>
        <Button href="/problems" variant="outline">Return Home</Button>
    </div>
{/await}