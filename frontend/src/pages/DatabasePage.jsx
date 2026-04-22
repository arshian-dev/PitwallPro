import React, { useState, useEffect } from 'react';
import { fetchJSON } from '../api';

const DatabasePage = () => {
    const [races, setRaces] = useState([]);
    const [selectedRace, setSelectedRace] = useState(null);
    const [results, setResults] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchJSON('/races?season=2023').then(data => {
            setRaces(data);
            setLoading(false);
            if (data.length > 0) setSelectedRace(data[0]);
        }).catch(() => setLoading(false));
    }, []);

    useEffect(() => {
        if (selectedRace) {
            fetchJSON(`/races/${selectedRace.race_id}/results`)
                .then(setResults)
                .catch(() => setResults([]));
        }
    }, [selectedRace]);

    return (
        <div className="p-margin space-y-stack-lg">
            <section className="flex justify-between items-end">
                <div>
                    <span className="text-tertiary font-label-caps text-[10px] tracking-[0.2em] mb-1 block">ADMINISTRATION PORTAL</span>
                    <h1 className="text-white font-headline-xl text-headline-xl">Race Database</h1>
                </div>
                <div className="flex items-center gap-3">
                    <span className="text-[10px] text-slate-400 font-bold uppercase">Select Race:</span>
                    <select className="bg-white/5 border border-white/10 text-white text-xs p-2 max-w-xs"
                        value={selectedRace?.race_id || ''}
                        onChange={e => setSelectedRace(races.find(r => r.race_id === +e.target.value))}>
                        {races.map(r => (
                            <option key={r.race_id} value={r.race_id} className="bg-[#1a1a1a]">{r.track_name} — {r.date}</option>
                        ))}
                    </select>
                </div>
            </section>

            {/* Race list */}
            <div className="grid grid-cols-12 gap-gutter">
                <div className="col-span-12 lg:col-span-4 glass-panel overflow-hidden max-h-[600px] overflow-y-auto">
                    <div className="p-3 border-b border-white/10 bg-white/5">
                        <span className="text-[10px] text-slate-400 font-bold uppercase">2023 Season — {races.length} Races</span>
                    </div>
                    <div className="divide-y divide-white/5">
                        {races.map(r => (
                            <div key={r.race_id}
                                onClick={() => setSelectedRace(r)}
                                className={`p-3 cursor-pointer transition-colors flex justify-between items-center ${selectedRace?.race_id === r.race_id ? 'bg-primary-container/10 border-l-2 border-primary-container' : 'hover:bg-white/5'}`}>
                                <div>
                                    <div className="text-white text-xs font-bold">{r.track_name}</div>
                                    <div className="text-slate-500 text-[10px]">{r.track_country}</div>
                                </div>
                                <span className="text-[10px] text-slate-400 font-data-mono">{r.date}</span>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Results table */}
                <div className="col-span-12 lg:col-span-8 glass-panel overflow-hidden">
                    <div className="p-3 border-b border-white/10 bg-white/5 flex justify-between items-center">
                        <span className="text-[10px] text-slate-400 font-bold uppercase">
                            {selectedRace ? `${selectedRace.track_name} — Race Results` : 'Select a race'}
                        </span>
                        <span className="text-[10px] text-tertiary font-bold">{results.length} ENTRIES</span>
                    </div>
                    <table className="w-full text-left">
                        <thead className="bg-white/5 border-b border-white/10">
                            <tr className="text-[10px] text-slate-400 font-bold uppercase">
                                <th className="p-3 w-16">POS</th>
                                <th className="p-3">DRIVER</th>
                                <th className="p-3">TEAM</th>
                                <th className="p-3 w-20">POINTS</th>
                                <th className="p-3 w-28">FASTEST LAP</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-white/5">
                            {results.map((rr, idx) => (
                                <tr key={rr.result_id || idx} className="hover:bg-white/5 transition-colors">
                                    <td className="p-3">
                                        <span className={`font-data-mono font-bold text-sm ${rr.position <= 3 ? 'text-primary-container' : 'text-white'}`}>
                                            P{rr.position}
                                        </span>
                                    </td>
                                    <td className="p-3">
                                        <div className="text-white font-bold text-sm">{rr.driver_name}</div>
                                        <div className="text-slate-500 text-[10px]">{rr.driver_nationality}</div>
                                    </td>
                                    <td className="p-3 text-slate-300 text-xs">{rr.team_name}</td>
                                    <td className="p-3 font-data-mono text-white text-sm">{rr.points}</td>
                                    <td className="p-3 font-data-mono text-tertiary text-sm">{rr.fastest_lap || '—'}</td>
                                </tr>
                            ))}
                            {results.length === 0 && (
                                <tr><td colSpan="5" className="p-6 text-center text-slate-500 text-sm">
                                    {loading ? 'Loading...' : 'No results available'}
                                </td></tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
};

export default DatabasePage;
