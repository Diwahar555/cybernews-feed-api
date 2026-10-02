import { ArrowUpRight, CalendarDays } from 'lucide-react'

function dateLabel(value) {
  if (!value) return 'Date unavailable'
  return new Intl.DateTimeFormat(undefined, { dateStyle: 'medium', timeStyle: 'short' }).format(new Date(value))
}

export function ArticleCard({ article }) {
  return (
    <article className="group rounded-2xl border border-slate-800 bg-slate-900/55 p-5 transition hover:-translate-y-0.5 hover:border-slate-700 hover:bg-slate-900/80">
      <div className="mb-3 flex flex-wrap items-center gap-2 text-xs">
        <span className="rounded-full bg-cyan-400/10 px-2.5 py-1 font-medium text-cyan-300">{article.source.name}</span>
        <span className="inline-flex items-center gap-1 text-slate-500"><CalendarDays size={13} /> {dateLabel(article.published_at)}</span>
      </div>

      <h2 className="text-lg font-semibold leading-7 text-slate-100 group-hover:text-white">{article.title}</h2>
      {article.summary && <p className="mt-2 line-clamp-3 text-sm leading-6 text-slate-400">{article.summary}</p>}

      <div className="mt-4 flex flex-wrap items-center justify-between gap-3">
        <div className="flex flex-wrap gap-2">
          {article.categories.map((item) => (
            <span key={item.id} className="rounded-md border border-slate-700 px-2 py-1 text-[11px] font-medium uppercase tracking-wide text-slate-400">{item.name}</span>
          ))}
        </div>
        <a href={article.url} target="_blank" rel="noreferrer noopener" className="inline-flex items-center gap-1 text-sm font-medium text-cyan-300 hover:text-cyan-200">
          Read original <ArrowUpRight size={15} />
        </a>
      </div>
    </article>
  )
}
