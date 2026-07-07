<script lang="ts">
    import { page } from '$app/stores';
    import { fetchProblemById } from '$lib/api';
    
    // Extract the ID from the URL path (/problems/[id])
    $: problemId = $page.params.id;
    $: problemPromise = fetchProblemById(problemId);
</script>

<main style="max-width: 800px; margin: 0 auto; padding: 2rem; font-family: sans-serif;">
    <a href="/" style="text-decoration: none; color: #666;">← Back to Problems</a>

    {#await problemPromise}
        <p>Loading problem details...</p>
    {:then problem}
        <div style="margin-top: 2rem;">
            <h1>{problem.title}</h1>
            <span style="padding: 0.25rem 0.5rem; background: #eee; border-radius: 4px;">
                {problem.difficulty}
            </span>

            <div style="margin-top: 2rem; background: #f9f9f9; padding: 1.5rem; border-radius: 8px;">
                <h3>Description</h3>
                <p style="white-space: pre-wrap; line-height: 1.6;">{problem.statement}</p>
            </div>

            <div style="margin-top: 2rem;">
                <h3>Constraints</h3>
                <ul>
                    {#each Object.entries(problem.constraints) as [key, value]}
                        <li><strong>{key}:</strong> {JSON.stringify(value)}</li>
                    {/each}
                </ul>
            </div>

            <button style="margin-top: 2rem; padding: 1rem 2rem; background: #000; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 1.1rem;">
                Start Coding Session
            </button>
        </div>
    {:catch error}
        <p style="color: red;">Error: {error.message}</p>
    {/await}
</main>