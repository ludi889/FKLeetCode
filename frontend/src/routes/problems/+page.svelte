<script lang="ts">
    import { fetchProblems } from '$lib/api';
    
    // Trigger the fetch immediately when the component loads
    const problemsPromise = fetchProblems();
</script>

<main style="max-width: 800px; margin: 0 auto; padding: 2rem; font-family: sans-serif;">
    <h1>FKLeetCode Problems</h1>
    
    {#await problemsPromise}
        <p>Loading problems from database...</p>
    {:then problems}
        <table style="width: 100%; border-collapse: collapse; text-align: left;">
            <thead>
                <tr style="border-bottom: 2px solid #ccc;">
                    <th style="padding: 1rem;">Title</th>
                    <th style="padding: 1rem;">Difficulty</th>
                    <th style="padding: 1rem;">Tags</th>
                </tr>
            </thead>
            <tbody>
                {#each problems as problem}
                    <tr style="border-bottom: 1px solid #eee;">
                        <td style="padding: 1rem;">
                            <a href={`/problems/${problem.id}`} style="color: blue; text-decoration: none;">
                                <strong>{problem.title}</strong>
                            </a>
                        </td>
                        <td style="padding: 1rem;">
                            <span style="padding: 0.25rem 0.5rem; background: #eee; border-radius: 4px;">
                                {problem.difficulty}
                            </span>
                        </td>
                        <td style="padding: 1rem;">
                            {problem.tags.topics?.join(', ') || 'No tags'}
                        </td>
                    </tr>
                {/each}
            </tbody>
        </table>
    {:catch error}
        <p style="color: red;">Error: {error.message}</p>
    {/await}
</main>