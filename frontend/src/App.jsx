import { useCallback, useEffect, useMemo, useState } from 'react'
import { ArticleCard } from './components/ArticleCard.jsx'
import { Filters } from './components/Filters.jsx'
import { Header } from './components/Header.jsx'
import { Pagination } from './components/Pagination.jsx'
import { EmptyState, ErrorState, LoadingState } from './components/States.jsx'
import { useDebounce } from './hooks/useDebounce.js'
import { getArticles, getCategories, getSources } from './lib/api.js'

export default function App() {
  const [search, setSearch] = useState('')
  const [source, setSource] = useState('')
  const [category, setCategory] = useState('')
  const [page, setPage] = useState(1)
  const [articles, setArticles] = useState([])
  const [meta, setMeta] = useState(null)
  const [sources, setSources] = useState([])
  const [categories, setCategories] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [revision, setRevision] = useState(0)
  const debouncedSearch = useDebounce(search.trim(), 350)

  const params = useMemo(() => ({
    page,
    page_size: 18,
    source,
    category,
    search: debouncedSearch.length >= 2 ? debouncedSearch : '',
  }), [page, source, category, debouncedSearch])

  useEffect(() => {
    const controller = new AbortController()
    Promise.all([getSources({ signal: controller.signal }), getCategories({ signal: controller.signal })])
      .then(([sourceRows, categoryRows]) => {
        setSources(sourceRows.filter((item) => item.is_active))
        setCategories(categoryRows)
      })
      .catch((err) => {
        if (err.name !== 'AbortError') setError(err.message)
      })
    return () => controller.abort()
  }, [])

  useEffect(() => {
    const controller = new AbortController()
    setLoading(true)
    setError('')
    getArticles(params, { signal: controller.signal })
      .then((data) => {
        setArticles(data.items)
        setMeta(data.meta)
      })
      .catch((err) => {
        if (err.name !== 'AbortError') setError(err.message)
      })
      .finally(() => {
        if (!controller.signal.aborted) setLoading(false)
      })
    return () => controller.abort()
  }, [params, revision])

  const changeSearch = useCallback((value) => { setSearch(value); setPage(1) }, [])
  const changeSource = useCallback((value) => { setSource(value); setPage(1) }, [])
  const changeCategory = useCallback((value) => { setCategory(value); setPage(1) }, [])

  const reset = useCallback(() => {
    setSearch('')
    setSource('')
    setCategory('')
    setPage(1)
  }, [])

  return (
    <div className="min-h-screen">
      <Header />
      <main className="mx-auto max-w-6xl px-4 py-8 sm:px-6 lg:px-8">
        <div className="mb-6">
          <p className="text-sm font-medium uppercase tracking-[0.2em] text-cyan-400">Live feed</p>
          <div className="mt-2 flex flex-wrap items-end justify-between gap-3">
            <div>
              <h2 className="text-3xl font-semibold tracking-tight text-white">Cybersecurity headlines, normalized.</h2>
              <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-400">Search and filter coverage from independent security publications and research blogs.</p>
            </div>
            {meta && <span className="text-sm text-slate-500">{meta.total} indexed articles</span>}
          </div>
        </div>

        <Filters search={search} setSearch={changeSearch} source={source} setSource={changeSource} category={category} setCategory={changeCategory} sources={sources} categories={categories} reset={reset} />

        <section className="mt-6">
          {loading ? <LoadingState /> : error ? <ErrorState message={error} retry={() => setRevision((value) => value + 1)} /> : articles.length === 0 ? <EmptyState /> : (
            <div className="space-y-4">
              <div className="grid gap-4 lg:grid-cols-2">
                {articles.map((article) => <ArticleCard key={article.id} article={article} />)}
              </div>
              <Pagination meta={meta} setPage={setPage} />
            </div>
          )}
        </section>
      </main>
      <footer className="border-t border-slate-900 py-8 text-center text-xs text-slate-600">CyberNews Feed indexes metadata and links back to original publishers.</footer>
    </div>
  )
}
