import { defineConfig } from 'vite'
import preact from '@preact/preset-vite'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  base: '/admin/',
  plugins: [
    tailwindcss(),
    preact(),
  ],
  build: {
    // Output directly into dist
    outDir: 'dist',
    // Target modern browsers — smaller output
    target: 'es2020',
    // Inline assets under 4 kB to reduce HTTP requests
    assetsInlineLimit: 4096,
    // Minify with esbuild (default, very fast, produces tiny output)
    minify: 'esbuild',
    rollupOptions: {
      output: {
        // Split vendor code (preact) from app code
        manualChunks: {
          vendor: ['preact', 'preact/hooks'],
        },
        // Hash-based filenames for cache busting
        entryFileNames: 'assets/[name]-[hash].js',
        chunkFileNames: 'assets/[name]-[hash].js',
        assetFileNames: 'assets/[name]-[hash][extname]',
      },
    },
    // Warn (not fail) if a chunk exceeds 500 kB — our budget is well under that
    chunkSizeWarningLimit: 500,
  },
})
