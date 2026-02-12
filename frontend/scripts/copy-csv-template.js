/**
 * ビルド後に public/faq-csv-template を dist/faq-csv-template へコピーする。
 * Render 等で Vite の public コピーが効かない場合でも、CSV テンプレートを配信可能にする。
 * 実行コンテキスト: frontend/ (package.json の build から node scripts/copy-csv-template.js)
 */
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const rootDir = path.resolve(__dirname, '..')
const srcDir = path.join(rootDir, 'public', 'faq-csv-template')
const destDir = path.join(rootDir, 'dist', 'faq-csv-template')

if (!fs.existsSync(srcDir)) {
  console.warn('[copy-csv-template] public/faq-csv-template が存在しません。スキップします。')
  process.exit(0)
}

const distDir = path.join(rootDir, 'dist')
if (!fs.existsSync(distDir)) {
  console.error('[copy-csv-template] dist が存在しません。先に vite build を実行してください。')
  process.exit(1)
}

fs.cpSync(srcDir, destDir, { recursive: true })
console.log('[copy-csv-template] dist/faq-csv-template へコピーしました。')
