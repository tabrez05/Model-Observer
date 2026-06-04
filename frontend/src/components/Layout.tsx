import { Link, NavLink, Outlet, useNavigate } from 'react-router-dom';
import { useCompareStore } from '../store';

export default function Layout() {
  const { selectedIds, clear } = useCompareStore();
  const navigate = useNavigate();

  return (
    <div className="min-h-screen flex flex-col">
      {/* Top nav */}
      <header className="sticky top-0 z-40 bg-gray-950/90 backdrop-blur border-b border-gray-800">
        <div className="max-w-7xl mx-auto px-4 h-14 flex items-center gap-6">
          <Link to="/" className="flex items-center gap-2 font-semibold text-white">
            <span className="text-brand-500">◈</span>
            <span>ML Tracker</span>
          </Link>
          <nav className="flex items-center gap-1 text-sm">
            <NavLink
              to="/"
              end
              className={({ isActive }) =>
                `px-3 py-1.5 rounded-md transition-colors ${isActive ? 'bg-gray-800 text-white' : 'text-gray-400 hover:text-white hover:bg-gray-800'}`
              }
            >
              Runs
            </NavLink>
            <NavLink
              to="/compare"
              className={({ isActive }) =>
                `px-3 py-1.5 rounded-md transition-colors ${isActive ? 'bg-gray-800 text-white' : 'text-gray-400 hover:text-white hover:bg-gray-800'}`
              }
            >
              Compare
            </NavLink>
            <NavLink
              to="/new"
              className={({ isActive }) =>
                `px-3 py-1.5 rounded-md transition-colors ${isActive ? 'bg-gray-800 text-white' : 'text-gray-400 hover:text-white hover:bg-gray-800'}`
              }
            >
              + New Run
            </NavLink>
          </nav>

          {/* Compare tray */}
          {selectedIds.length > 0 && (
            <div className="ml-auto flex items-center gap-3">
              <span className="text-sm text-gray-400">
                {selectedIds.length} selected
              </span>
              <button
                className="btn-primary text-xs"
                onClick={() => navigate(`/compare?ids=${selectedIds.join(',')}`)}
              >
                Compare →
              </button>
              <button className="btn-ghost text-xs" onClick={clear}>
                Clear
              </button>
            </div>
          )}
        </div>
      </header>

      <main className="flex-1 max-w-7xl mx-auto w-full px-4 py-6">
        <Outlet />
      </main>
    </div>
  );
}
