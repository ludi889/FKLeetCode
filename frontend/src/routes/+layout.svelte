<script lang="ts">
	import './layout.css';

	// Svelte 5 syntax for accepting page content
	let { children } = $props();
</script>

<div
	style="font-family: system-ui, sans-serif; min-height: 100vh; display: flex; flex-direction: column;"
>
	<header
		style="background: #111; color: white; padding: 1rem 2rem; display: flex; justify-content: space-between; align-items: center;"
	>
		<div
			style="font-weight: bold; font-size: 1.5rem; letter-spacing: -1px;"
		>
			<a
				href="/"
				style="color: white; text-decoration: none;"
			>FKLeetCode</a>
		</div>

		<nav style="display: flex; gap: 1.5rem;">
			<a
				href="/problems"
				style="color: #ccc; text-decoration: none;"
			>Problems</a>

			<a
				href="/sessions/"
				style="color: #ccc; text-decoration: none;"
			>Create Session</a>

			<a
				href="/about"
				style="color: #ccc; text-decoration: none;"
			>About</a>
		</nav>
	</header>

	<main
		style="flex: 1; display: flex; flex-direction: column; align-items: center; padding: 2rem;"
	>{@render children()}</main>

	<footer
		style="text-align: center; padding: 2rem; color: #666; font-size: 0.9rem; border-top: 1px solid #eee;"
	>© {new Date().getFullYear()} FKLeetCode. The ultimate coding interview simulator.</footer>
</div>
