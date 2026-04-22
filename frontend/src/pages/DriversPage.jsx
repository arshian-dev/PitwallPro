import React, { useState, useEffect } from 'react';
import { fetchJSON } from '../api';

const DriversPage = () => {
    const [driverStats, setDriverStats] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchJSON('/drivers').then(async (drivers) => {
            // Fetch stats for each driver
            const statsPromises = drivers.map(d =>
                fetchJSON(`/drivers/${d.driver_id}/stats`).catch(() => ({
                    driver_id: d.driver_id, name: d.name, nationality: d.nationality,
                    team_name: d.team_name, consistency: 0, wins: 0, podiums: 0,
                    total_points: 0, position_history: [],
                }))
            );
            const allStats = await Promise.all(statsPromises);
            // Sort by total points descending, take top 10
            allStats.sort((a, b) => b.total_points - a.total_points);
            setDriverStats(allStats.slice(0, 10));
            setLoading(false);
        }).catch(e => { console.warn("Drivers offline", e); setLoading(false); });
    }, []);

    if (loading) {
        return (
            <div className="flex items-center justify-center h-full">
                <span className="text-slate-500 animate-pulse font-label-caps uppercase tracking-widest">Loading Driver Telemetry...</span>
            </div>
        );
    }

    return (
        <div className="p-6 space-y-8">
            <header>
                <h1 className="text-headline-xl font-headline-xl text-white uppercase italic">Driver Performance</h1>
                <p className="text-slate-500 font-label-caps uppercase tracking-widest flex items-center gap-2">
                    <span className="w-3 h-[1px] bg-[#E10600]"></span> Season 2023 Analytics Dashboard
                </p>
            </header>
            <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
                {driverStats.map((driver, idx) => {
                    const maxPos = 20;
                    const history = driver.position_history || [];
                    return (
                        <div key={driver.driver_id} className="bg-[#1A1A1A]/60 backdrop-blur-2xl border border-white/10 flex flex-col md:flex-row relative overflow-hidden group">
                            <div className="absolute top-0 left-0 w-1 h-full bg-[#E10600]"></div>
                            <div className="w-full md:w-56 p-6 border-b md:border-b-0 md:border-r border-white/5 flex flex-col items-center text-center">
                                <div className="relative w-24 h-24 mb-4">
                                    <div className="absolute inset-0 rounded-full border-2 border-[#E10600] border-t-transparent animate-spin" style={{animationDuration: '3s'}}></div>
                                    <div className="w-full h-full rounded-full bg-white/5 flex items-center justify-center p-1 overflow-hidden relative">
                                        <img 
                                            src={`/pictures/${driver.name?.toLowerCase().replace(/\s+/g, '_')}.png`} 
                                            alt={driver.name}
                                            className="w-full h-full object-cover rounded-full z-10"
                                            onError={(e) => { e.target.style.display = 'none'; }}
                                        />
                                        <span className="text-2xl font-black text-white absolute z-0">P{idx + 1}</span>
                                    </div>
                                </div>
                                <h3 className="font-headline-md text-white text-sm">{driver.name?.toUpperCase()}</h3>
                                <p className="text-[#E10600] text-[10px] uppercase font-bold">{driver.nationality}</p>
                                <p className="text-slate-500 text-[9px] uppercase mt-1">{driver.team_name}</p>
                            </div>
                            <div className="flex-1 p-6 space-y-6">
                                <div className="grid grid-cols-4 gap-4">
                                    <div><span className="text-[9px] text-slate-500">CONSISTENCY</span><div className="text-lg font-black text-cyan-400">{driver.consistency}%</div></div>
                                    <div><span className="text-[9px] text-slate-500">WINS</span><div className="text-lg font-black text-white">{driver.wins}</div></div>
                                    <div><span className="text-[9px] text-slate-500">PODIUMS</span><div className="text-lg font-black text-white">{driver.podiums}</div></div>
                                    <div><span className="text-[9px] text-slate-500">POINTS</span><div className="text-lg font-black text-white">{driver.total_points}</div></div>
                                </div>
                                <div className="h-16 w-full flex items-end gap-[2px]">
                                    {history.slice(-15).map((pos, i) => {
                                        const h = Math.max(10, ((maxPos - pos) / maxPos) * 100);
                                        return (
                                            <div key={i} className="flex-1 bg-cyan-400/20 hover:bg-cyan-400/40 transition-colors relative group/bar" style={{ height: h + '%' }}>
                                                <span className="absolute -top-4 left-1/2 -translate-x-1/2 text-[8px] text-cyan-400 opacity-0 group-hover/bar:opacity-100 transition-opacity">P{pos}</span>
                                            </div>
                                        );
                                    })}
                                    {history.length === 0 && <span className="text-slate-600 text-[9px]">No race data</span>}
                                </div>
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
};

export default DriversPage;
