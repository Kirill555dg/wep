export function Footer() {
  const year = new Date().getFullYear()

  return (
    <footer className="border-t border-gray-100 py-3">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex items-center justify-between text-xs text-gray-400">
        <span>&copy; {year} Ибрахим Миркин</span>
        <a
          href="https://github.com/ibrahim-mirkin"
          target="_blank"
          rel="noopener noreferrer"
          className="hover:text-gray-600 transition-colors"
        >
          GitHub
        </a>
      </div>
    </footer>
  )
}
