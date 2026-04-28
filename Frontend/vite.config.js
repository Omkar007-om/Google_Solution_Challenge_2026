import { defineConfig } from 'vite'
import react, { reactCompilerPreset } from '@vitejs/plugin-react'
import babel from '@rolldown/plugin-babel'

const repoName = process.env.GITHUB_REPOSITORY?.split('/')[1]
const isGithubPages = process.env.GITHUB_ACTIONS === 'true' && repoName

// https://vite.dev/config/
export default defineConfig({
  base: isGithubPages ? `/${repoName}/` : '/',
  plugins: [
    react(),
    babel({ presets: [reactCompilerPreset()] })
  ],
  server: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
})
