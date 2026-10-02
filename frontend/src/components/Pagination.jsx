import { ChevronLeft, ChevronRight } from 'lucide-react'

export function Pagination({ meta, setPage }) {
  if (!meta || meta.pages <= 1) return null
  return (
    <nav className="flex items-center justify-between border-t border-slate-800 pt-5" aria-label="Pagination">
      <p className="text-sm text-slate-500">Page {meta.page} of {meta.pages} · {meta.total} articles</p>
      <div className="flex gap-2">
        <button type="button" onClick={() => setPage(meta.page - 1)} disabled={meta.page <= 1} className="rounded-lg border border-slate-700 p-2 text-slate-300 hover:border-slate-500 disabled:opacity-30" aria-label="Previous page"><ChevronLeft size={18} /></button>
        <button type="button" onClick={() => setPage(meta.page + 1)} disabled={meta.page >= meta.pages} className="rounded-lg border border-slate-700 p-2 text-slate-300 hover:border-slate-500 disabled:opacity-30" aria-label="Next page"><ChevronRight size={18} /></button>
      </div>
    </nav>
  )
}
