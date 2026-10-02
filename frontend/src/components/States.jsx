import { AlertTriangle, LoaderCircle, Newspaper } from 'lucide-react'

export function LoadingState() {
  return <div className="flex min-h-56 items-center justify-center gap-2 text-slate-400"><LoaderCircle className="animate-spin" size={20} /> Loading intelligence feed…</div>
}

export function EmptyState() {
  return <div className="flex min-h-56 flex-col items-center justify-center text-center text-slate-500"><Newspaper size={28} /><p className="mt-3 font-medium text-slate-300">No matching articles</p><p className="mt-1 text-sm">Try clearing a filter or using a broader search.</p></div>
}

export function ErrorState({ message, retry }) {
  return <div className="flex min-h-56 flex-col items-center justify-center text-center"><AlertTriangle className="text-amber-300" size={28} /><p className="mt-3 font-medium text-slate-200">Couldn’t load the feed</p><p className="mt-1 max-w-lg text-sm text-slate-500">{message}</p><button type="button" onClick={retry} className="mt-4 rounded-lg border border-slate-700 px-3 py-2 text-sm text-slate-300 hover:border-slate-500">Try again</button></div>
}
