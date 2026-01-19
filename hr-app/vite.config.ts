import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
	plugins: [sveltekit()],
	server: {
		allowedHosts: [
			'xn--299a1v27n0w5a.store',     
    		'www.xn--299a1v27n0w5a.store',
			'xn--zb0brsr4zmlx.store',
            '근태관리.store'
		]
	}
});