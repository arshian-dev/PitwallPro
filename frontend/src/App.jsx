import React from 'react';
import { BrowserRouter, Routes, Route, Link, useLocation } from 'react-router-dom';

import DashboardPage from './pages/DashboardPage';
import CarLabPage from './pages/CarLabPage';
import DriversPage from './pages/DriversPage';
import StrategyPage from './pages/StrategyPage';
import TelemetryPage from './pages/TelemetryPage';
import DatabasePage from './pages/DatabasePage';

const Layout = ({ children }) => {
    const location = useLocation();
    const isActive = (path) => location.pathname === path;

    return (
        <div className="flex h-screen overflow-hidden">
            {/* SideNavBar */}
            <aside className="flex flex-col h-full py-4 bg-[#0D0D0D] border-r border-white/10 w-64 shrink-0 z-50">
                <div className="px-6 mb-8">
                    <h1 className="text-lg font-black text-white font-headline-md tracking-tighter">MISSION CONTROL</h1>
                    <p className="font-['Space_Grotesk'] text-[11px] font-bold uppercase tracking-wider text-[#E10600]">LIVE TELEMETRY ACTIVE</p>
                </div>
                <nav className="flex-1 space-y-1">
                    <Link to="/" className={`flex items-center px-4 py-3 gap-3 transition-colors group ${isActive('/') ? 'bg-white/5 text-[#E10600] border-l-4 border-[#E10600]' : 'text-slate-500 hover:bg-white/5'}`}>
                        <span className={`material-symbols-outlined ${isActive('/') ? '' : 'group-hover:text-cyan-400'}`} data-icon="dashboard">dashboard</span>
                        <span className="font-['Space_Grotesk'] text-[11px] font-bold uppercase tracking-wider">Dashboard</span>
                    </Link>
                    <Link to="/car-lab" className={`flex items-center px-4 py-3 gap-3 transition-colors group ${isActive('/car-lab') ? 'bg-white/5 text-[#E10600] border-l-4 border-[#E10600]' : 'text-slate-500 hover:bg-white/5'}`}>
                        <span className={`material-symbols-outlined ${isActive('/car-lab') ? '' : 'group-hover:text-cyan-400'}`} data-icon="precision_manufacturing">precision_manufacturing</span>
                        <span className="font-['Space_Grotesk'] text-[11px] font-bold uppercase tracking-wider">Car Lab</span>
                    </Link>
                    <Link to="/drivers" className={`flex items-center px-4 py-3 gap-3 transition-colors group ${isActive('/drivers') ? 'bg-white/5 text-[#E10600] border-l-4 border-[#E10600]' : 'text-slate-500 hover:bg-white/5'}`}>
                        <span className={`material-symbols-outlined ${isActive('/drivers') ? '' : 'group-hover:text-cyan-400'}`} data-icon="person_filled">person_filled</span>
                        <span className="font-['Space_Grotesk'] text-[11px] font-bold uppercase tracking-wider">Drivers</span>
                    </Link>
                    <Link to="/strategy" className={`flex items-center px-4 py-3 gap-3 transition-colors group ${isActive('/strategy') ? 'bg-white/5 text-[#E10600] border-l-4 border-[#E10600]' : 'text-slate-500 hover:bg-white/5'}`}>
                        <span className={`material-symbols-outlined ${isActive('/strategy') ? '' : 'group-hover:text-cyan-400'}`} data-icon="calculate">calculate</span>
                        <span className="font-['Space_Grotesk'] text-[11px] font-bold uppercase tracking-wider">Strategy</span>
                    </Link>
                    <Link to="/telemetry" className={`flex items-center px-4 py-3 gap-3 transition-colors group ${isActive('/telemetry') ? 'bg-white/5 text-[#E10600] border-l-4 border-[#E10600]' : 'text-slate-500 hover:bg-white/5'}`}>
                        <span className={`material-symbols-outlined ${isActive('/telemetry') ? '' : 'group-hover:text-cyan-400'}`} data-icon="query_stats">query_stats</span>
                        <span className="font-['Space_Grotesk'] text-[11px] font-bold uppercase tracking-wider">Telemetry</span>
                    </Link>
                    <Link to="/database" className={`flex items-center px-4 py-3 gap-3 transition-colors group ${isActive('/database') ? 'bg-white/5 text-[#E10600] border-l-4 border-[#E10600]' : 'text-slate-500 hover:bg-white/5'}`}>
                        <span className={`material-symbols-outlined ${isActive('/database') ? '' : 'group-hover:text-cyan-400'}`} data-icon="database">database</span>
                        <span className="font-['Space_Grotesk'] text-[11px] font-bold uppercase tracking-wider">Database</span>
                    </Link>
                </nav>

            </aside>
            
            <div className="flex-1 flex flex-col min-w-0 bg-background relative h-screen">
                {/* TopAppBar */}
                <header className="flex justify-between items-center w-full px-6 h-16 z-50 bg-[#0D0D0D]/90 backdrop-blur-2xl border-b border-white/10 shadow-[0_8px_32px_0_rgba(0,0,0,0.8)]">
                    <div className="flex items-center gap-8">
                        <span className="text-xl font-black italic text-[#E10600] tracking-tighter">PITWALL PRO</span>

                    </div>
                    <div className="flex items-center gap-4">

                        <div className="flex items-center gap-2 pl-4 border-l border-white/10">
                            <span className="material-symbols-outlined text-[#E10600]">account_circle</span>
                            <span className="font-['Space_Grotesk'] text-[10px] font-bold text-white tracking-wider">CHIEF ENG.</span>
                        </div>
                    </div>
                </header>
                
                <main className="flex-1 overflow-y-auto">
                    {children}
                </main>

                <footer className="h-8 bg-[#0D0D0D] border-t border-white/10 px-6 flex items-center justify-between text-[9px] font-bold uppercase tracking-widest shrink-0">
                    <div className="flex gap-4 items-center">
                        <span className="text-[#E10600] flex items-center gap-1"><span className="w-2 h-2 bg-[#E10600] rounded-full animate-pulse"></span> Uplink Active</span>
                        <span className="text-slate-500">Latency: 12ms</span>
                        <span className="text-slate-500">Packet Loss: 0.00%</span>
                    </div>
                    <div className="flex gap-4 text-slate-500">
                        <span>GPS: 51.3498° N, 0.2187° W</span>
                        <span className="text-white">Time: {new Date().toLocaleTimeString('en-GB', { hour12: false })} UTC</span>
                    </div>
                </footer>
            </div>
        </div>
    );
};

function App() {
  return (
    <BrowserRouter>
        <Layout>
            <Routes>
                <Route path="/" element={<DashboardPage />} />
                <Route path="/car-lab" element={<CarLabPage />} />
                <Route path="/drivers" element={<DriversPage />} />
                <Route path="/strategy" element={<StrategyPage />} />
                <Route path="/telemetry" element={<TelemetryPage />} />
                <Route path="/database" element={<DatabasePage />} />
            </Routes>
        </Layout>
    </BrowserRouter>
  );
}

export default App;
