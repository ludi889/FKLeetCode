<script lang="ts">
    import { page } from '$app/stores';
    import { fetchProblemById } from '$lib/api/client';
    import { Button } from '$lib/components/ui/button';
    import { Badge } from '$lib/components/ui/badge';
    import * as Card from '$lib/components/ui/card';

    const problemId = $page.params.id;
    const problemPromise = fetchProblemById(problemId);

    // Form state for code submission
    let userCode = $state('');
    let isSubmitting = $state(false);

    // Initialize user code with the default method signature when data loads
    function handleDataLoaded(signature: any) {
        if (!userCode && signature) {
            const args = signature.args.map((a: any) => `${a.name}: ${a.type}`).join(', ');
            userCode = `def ${signature.name}(${args}) -> ${signature.returns}:\n    # Write your code here\n    pass`;
        }
    }

    // Allow tabbing inside the textarea instead of losing focus
    function handleKeyDown(e: KeyboardEvent) {
        if (e.key === 'Tab') {
            e.preventDefault();
            const target = e.target as HTMLTextAreaElement;
            const start = target.selectionStart;
            const end = target.selectionEnd;
            userCode = userCode.substring(0, start) + "    " + userCode.substring(end);
            // Reset cursor position on next tick
            setTimeout(() => {
                target.selectionStart = target.selectionEnd = start + 4;
            }, 0);
        }
    }

    async function submitSolution() {
        isSubmitting = true;
        // TODO: Wire this up to the execution engine endpoint later
        setTimeout(() => {
            isSubmitting = false;
            alert("Code captured! Ready for Execution Engine integration.");
        }, 1000);
    }
</script>

{#await problemPromise}
    <div class="h-screen w-full flex items-center justify-center text-muted-foreground animate-pulse">
        Loading workspace environment...
    </div>
{:then problem}
    <span class="hidden" use:handleDataLoaded={problem.signature}></span>

    <div class="w-full h-[calc(100vh-4rem)] flex flex-col md:flex-row bg-background">
        <div class="w-full md:w-1/2 h-full border-r flex flex-col overflow-y-auto p-6 space-y-6">
            <div class="flex items-center justify-between">
                <h1 class="text-2xl font-bold tracking-tight">{problem.title}</h1>
                <Badge variant="secondary" class="bg-green-100 text-green-800">{problem.difficulty.toUpperCase()}</Badge>
            </div>

            <div class="prose prose-slate dark:prose-invert">
                <p class="whitespace-pre-wrap leading-relaxed text-sm text-foreground/90">
                    {problem.statement}
                </p>
            </div>

            <Card.Root>
                <Card.Header class="py-3">
                    <Card.Title class="text-sm font-semibold">Constraints</Card.Title>
                </Card.Header>
                <Card.Content class="text-xs space-y-1 text-muted-foreground">
                    {#each Object.entries(problem.constraints) as [key, value]}
                        <div class="flex justify-between border-b py-1 last:border-0">
                            <span class="font-mono text-primary">{key}</span>
                            <span class="font-medium text-foreground">{JSON.stringify(value)}</span>
                        </div>
                    {/each}
                </Card.Content>
            </Card.Root>
        </div>

        <div class="w-full md:w-1/2 h-full flex flex-col bg-slate-950 text-slate-50">
            <div class="h-12 border-b border-slate-800 px-4 flex items-center justify-between bg-slate-900/50">
                <span class="text-xs font-mono text-slate-400">Language: Python3</span>
                <div class="flex items-center gap-2">
                    <Button 
                        size="sm" 
                        variant="ghost" 
                        class="text-slate-300 hover:text-white hover:bg-slate-800 text-xs h-8"
                    >
                        Run Code
                    </Button>
                    <Button 
                        size="sm" 
                        onclick={submitSolution} 
                        disabled={isSubmitting}
                        class="bg-blue-600 hover:bg-blue-500 text-white text-xs h-8 font-semibold"
                    >
                        {isSubmitting ? 'Submitting...' : 'Submit'}
                    </Button>
                </div>
            </div>

            <div class="flex-1 relative p-4">
                <textarea
                    bind:value={userCode}
                    onkeydown={handleKeyDown}
                    spellcheck="false"
                    class="w-full h-full bg-transparent font-mono text-sm leading-relaxed resize-none focus:outline-none border-0 p-0 text-emerald-400 selection:bg-slate-800"
                ></textarea>
            </div>
        </div>
    </div>
{:catch error}
    <div class="h-screen w-full flex flex-col items-center justify-center gap-4">
        <p class="text-destructive font-medium">Failed to initialize workspace: {error.message}</p>
        <Button href="/problems" variant="outline">Return to Library</Button>
    </div>
{/await}