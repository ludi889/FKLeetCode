<script lang="ts">
    import { goto } from '$app/navigation';
    import { createSession } from '$lib/api/client';
    import { Button } from '$lib/components/ui/button';
    import { Terminal, Code2, Cpu } from 'lucide-svelte';

    let isStarting = $state(false);

    async function handleStartSession() {
        isStarting = true;
        try {
            const session = await createSession();
            if (!session || !session.id) throw new Error("No session ID returned.");
            await goto(`/sessions/${session.id}`);
        } catch (error: any) {
            console.error("Routing Error:", error);
            alert(`Error starting session: ${error.message}`);
        } finally {
            isStarting = false;
        }
    }
</script>

<div class="relative min-h-[calc(100vh-4rem)] flex flex-col items-center justify-center overflow-hidden bg-background">
    
    <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[400px] bg-blue-500/10 blur-[120px] rounded-full pointer-events-none"></div>

    <div class="relative z-10 text-center max-w-4xl mx-auto px-6">
        
        <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-secondary text-secondary-foreground text-sm font-medium mb-8 border shadow-sm">
            <span class="flex h-2 w-2 rounded-full bg-blue-600 animate-pulse"></span>
            Dynamic Execution Engine v1.0
        </div>

        <h1 class="text-5xl md:text-7xl font-extrabold tracking-tight mb-6 text-transparent bg-clip-text bg-gradient-to-b from-foreground to-foreground/70">
            Master the Interview. <br />
            <span class="text-blue-600">No Surprises.</span>
        </h1>
        
        <p class="text-lg md:text-xl text-muted-foreground mb-10 max-w-2xl mx-auto leading-relaxed">
            Practice dynamically generated coding scenarios, handle architectural curveballs, 
            and simulate real-world backend engineering environments.
        </p>

        <div class="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <Button 
                size="lg" 
                onclick={handleStartSession} 
                disabled={isStarting}
                class="font-semibold text-base px-8 h-14 w-full sm:w-auto shadow-lg hover:shadow-blue-500/20 transition-all"
            >
                {#if isStarting}
                    <div class="flex items-center gap-2">
                        <div class="h-4 w-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                        Initializing Environment...
                    </div>
                {:else}
                    Start a Session
                {/if}
            </Button>
            
            <Button 
                size="lg" 
                variant="outline" 
                href="/problems"
                class="font-semibold text-base px-8 h-14 w-full sm:w-auto bg-background/50 backdrop-blur-sm"
            >
                Browse Problems
            </Button>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-8 mt-24 text-left border-t pt-12">
            <div class="space-y-3">
                <div class="h-10 w-10 rounded-lg bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center text-blue-600">
                    <Terminal size={20} />
                </div>
                <h3 class="font-semibold text-foreground">Dynamic Variants</h3>
                <p class="text-sm text-muted-foreground leading-relaxed">Every session generates a unique scenario. You can't memorize the answers here.</p>
            </div>
            <div class="space-y-3">
                <div class="h-10 w-10 rounded-lg bg-emerald-100 dark:bg-emerald-900/30 flex items-center justify-center text-emerald-600">
                    <Cpu size={20} />
                </div>
                <h3 class="font-semibold text-foreground">Isolated Execution</h3>
                <p class="text-sm text-muted-foreground leading-relaxed">Your code is evaluated in a secure backend worker against hidden test cases.</p>
            </div>
            <div class="space-y-3">
                <div class="h-10 w-10 rounded-lg bg-purple-100 dark:bg-purple-900/30 flex items-center justify-center text-purple-600">
                    <Code2 size={20} />
                </div>
                <h3 class="font-semibold text-foreground">Architecture Focus</h3>
                <p class="text-sm text-muted-foreground leading-relaxed">Beyond just passing tests, handle stage-2 curveballs designed to break bad design.</p>
            </div>
        </div>
    </div>
</div>