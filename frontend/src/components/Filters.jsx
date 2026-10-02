import { Search, X } from 'lucide-react'

export function Filters({ search, setSearch, source, setSource, category, setCategory, sources, categories, reset }) {
  const active = search || source || category
  return (
    <section className="rounded-2xl border border-slate-800 bg-slate-900/70 p-4 shadow-2xl shadow-black/10">
      <div className="grid gap-3 md:grid-cols-[minmax(0,1fr)_14rem_14rem_auto]">
        <label className="relative block">
          <span className="sr-only">Search articles</span>
          <Search className="pointer-events-none absolute left-3 top-3 text-slate-500" size={18} />
          <input
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            placeholder="Search threats, CVEs, vendors..."
            className="w-full rounded-xl border border-slate-700 bg-slate-950 py-2.5 pl-10 pr-3 text-sm text-slate-100 outline-none transition focus:border-cyan-400"
          />
        </label>

        <select aria-label="Filter by source" value={source} onChange={(event) => setSource(event.target.value)} className="rounded-xl border border-slate-700 bg-slate-950 px-3 py-2.5 text-sm text-slate-200 outline-none focus:border-cyan-400">
          <option value="">All sources</option>
          {sources.map((item) => <option key={item.id} value={item.slug}>{item.name}</option>)}
        </select>

        <select aria-label="Filter by category" value={category} onChange={(event) => setCategory(event.target.value)} className="rounded-xl border border-slate-700 bg-slate-950 px-3 py-2.5 text-sm text-slate-200 outline-none focus:border-cyan-400">
          <option value="">All categories</option>
          {categories.map((item) => <option key={item.id} value={item.slug}>{item.name}</option>)}
        </select>

        <button type="button" disabled={!active} onClick={reset} className="inline-flex items-center justify-center gap-2 rounded-xl border border-slate-700 px-3 py-2.5 text-sm text-slate-300 transition hover:border-slate-500 hover:text-white disabled:cursor-not-allowed disabled:opacity-40">
          <X size={16} aria-hidden="true" /> Clear
        </button>
      </div>
    </section>
  )
}
