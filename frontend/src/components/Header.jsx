import { Radar } from 'lucide-react'

export function Header() {
  return (
    <header className="border-b border-slate-800/80 bg-slate-950/75 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center gap-3 px-4 py-5 sm:px-6 lg:px-8">
        <div className="rounded-xl border border-cyan-400/20 bg-cyan-400/10 p-2 text-cyan-300">
          <Radar size={24} aria-hidden="true" />
        </div>
        <div>
          <h1 className="text-xl font-semibold tracking-tight text-white">CyberNews Feed</h1>
          <p className="text-sm text-slate-400">Security intelligence, without the tab overload.</p>
        </div>
      </div>
    </header>
  )
}
