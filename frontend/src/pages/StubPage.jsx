function StubPage({ title, description }) {
  return (
    <div className="flex items-center justify-center min-h-[400px] px-5 py-10">
      <div className="text-center max-w-lg">
        <div className="text-6xl mb-5">🚧</div>
        <h1 className="text-3xl font-bold text-zinc-900 dark:text-zinc-50 mb-4">{title}</h1>
        <p className="text-base text-zinc-600 dark:text-zinc-400 leading-relaxed mb-6">
          {description || 'This page is under construction and will be implemented soon.'}
        </p>
        <div className="inline-block px-5 py-2 bg-gradient-to-br from-indigo-500 to-indigo-700 text-white rounded-full text-sm font-semibold">
          Coming Soon
        </div>
      </div>
    </div>
  );
}

export default StubPage;
