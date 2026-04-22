import React, { useState, useEffect, useCallback } from 'react';
import { fetchJSON } from '../api';
import { ComposedChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ReferenceLine, ReferenceArea } from 'recharts';

const COMPOUNDS = ['SOFT', 'MEDIUM', 'HARD'];
const COMPOUND_COLORS = { SOFT: '#E10600', MEDIUM: '#FFC107', HARD: '#ccc' };

const StrategyPage = () => {
    const [compound, setCompound] = useState('SOFT');
    const [fuel, setFuel] = useState(84);
    const [trackTemp, setTrackTemp] = useState(28);
    const [totalLaps, setTotalLaps] = useState(52);
    const [stops, setStops] = useState(1);
    const [tracks, setTracks] = useState([]);
    const [selectedTrack, setSelectedTrack] = useState(null);
    const [cars, setCars] = useState([]);
    const [selectedCar, setSelectedCar] = useState(null);
    const [simResult, setSimResult] = useState(null);

    // User-chosen compounds for each stint (stint1 = starting compound)
    const [stint2Compound, setStint2Compound] = useState('HARD');
    const [stint3Compound, setStint3Compound] = useState('MEDIUM');

    useEffect(() => {
        Promise.all([
            fetchJSON('/strategy/tracks'),
            fetchJSON('/strategy/cars')
        ]).then(([trackData, carData]) => {
            setTracks(trackData);
            setCars(carData);
            if (trackData.length > 0) {
                const silverstone = trackData.find(t => t.id === 'silverstone') || trackData[0];
                handleTrackChange(silverstone);
            }
            if (carData.length > 0) {
                const rb19 = carData.find(c => c.id === 'rb19') || carData[0];
                setSelectedCar(rb19.id);
            }
        });
    }, []);

    const handleTrackChange = (track) => {
        setSelectedTrack(track);
        setTotalLaps(track.laps);
        setTrackTemp(track.temp);
    };

    // When stops changes, reset stint compounds to sensible defaults
    useEffect(() => {
        if (stops === 1) {
            setStint2Compound(compound === 'HARD' ? 'MEDIUM' : 'HARD');
        } else {
            setStint2Compound('MEDIUM');
            setStint3Compound('HARD');
        }
    }, [stops]);

    // Build the stints param string
    const buildStintsParam = useCallback(() => {
        if (stops === 1) return `${compound},${stint2Compound}`;
        return `${compound},${stint2Compound},${stint3Compound}`;
    }, [compound, stint2Compound, stint3Compound, stops]);

    const runSim = useCallback(() => {
        const stintsParam = buildStintsParam();
        fetchJSON(`/strategy/simulate?compound=${compound}&fuel_kg=${fuel}&track_temp=${trackTemp}&total_laps=${totalLaps}&stops=${stops}&stints=${stintsParam}&car_id=${selectedCar}`)
            .then(setSimResult)
            .catch(e => console.warn("Strategy sim offline", e));
    }, [compound, fuel, trackTemp, totalLaps, stops, buildStintsParam, selectedCar]);

    useEffect(() => { 
        if (selectedTrack && selectedCar) runSim(); 
    }, [runSim, selectedTrack, selectedCar]);

    const curve = simResult?.degradation_curve || [];
    const pit = simResult?.pit_recommendation || {};
    const ruleViolation = pit.rule_violation || null;

    // Check violation client-side for instant feedback
    const getClientViolation = () => {
        const stints = stops === 1 ? [compound, stint2Compound] : [compound, stint2Compound, stint3Compound];
        const unique = new Set(stints);
        if (unique.size < 2) return 'F1 rules require at least 2 different slick compounds in a dry race.';
        return null;
    };
    const violation = ruleViolation || getClientViolation();

    // Custom Tooltip
    const CustomTooltip = ({ active, payload, label }) => {
        if (active && payload && payload.length) {
            const dataPoint = curve.find(p => p.lap === label);
            const comp = dataPoint?.compound || '';
            return (
                <div className="bg-[#1a1a1a] border border-white/10 p-3 shadow-xl" style={{ borderLeftColor: COMPOUND_COLORS[comp] || '#fff', borderLeftWidth: 3 }}>
                    <div className="flex items-center gap-2 mb-2">
                        <p className="text-white text-xs font-bold">LAP {label}</p>
                        <span className="text-[9px] font-bold px-1.5 py-0.5 rounded" style={{ background: COMPOUND_COLORS[comp] + '22', color: COMPOUND_COLORS[comp] }}>{comp}</span>
                    </div>
                    {payload.map((entry, index) => (
                        <p key={index} className="text-[10px] uppercase" style={{ color: entry.color }}>
                            {entry.name}: {entry.value.toFixed(2)} {entry.name === 'Grip %' ? '%' : 's'}
                        </p>
                    ))}
                </div>
            );
        }
        return null;
    };

    // Compound selector button row for a stint
    const CompoundSelector = ({ label, value, onChange }) => (
        <div className="glass-panel p-stack-md">
            <label className="text-[10px] text-slate-400 font-bold uppercase mb-3 block">{label}</label>
            <div className="grid grid-cols-3 gap-2">
                {COMPOUNDS.map(c => (
                    <button key={c} onClick={() => onChange(c)}
                        className={`border p-2 text-[10px] font-bold transition-all flex items-center justify-center gap-1.5 ${value === c ? 'border-[#E10600] bg-[#E10600]/10 text-white' : 'border-white/10 bg-white/5 text-slate-400 hover:bg-white/10'}`}>
                        <span className="w-2 h-2 rounded-full inline-block" style={{ background: COMPOUND_COLORS[c] }}></span>
                        {c}
                    </button>
                ))}
            </div>
        </div>
    );

    return (
        <div className="p-margin space-y-stack-lg">
            <header className="flex justify-between items-end">
                <div>
                    <h1 className="font-headline-xl text-headline-xl uppercase text-white mb-2">Race Strategy <span className="text-[#E10600]">Simulator</span></h1>
                    <p className="font-body-md text-on-surface opacity-60">
                        {selectedTrack?.name || 'Loading...'} | Total Laps: {totalLaps} | Temp: {trackTemp}°C
                    </p>
                </div>
                {pit.recommended_pit_laps && (
                    <div className={`glass-panel px-4 py-2 border-l-2 ${violation ? 'border-amber-500' : 'border-[#E10600]'}`}>
                        <span className="text-[9px] text-slate-400 font-bold uppercase block">
                            {violation ? '⚠ Rule Violation' : 'Optimal Pit Window'}
                        </span>
                        <span className="text-white font-headline-md text-xl">
                            {pit.recommended_pit_laps.map(l => `LAP ${l}`).join(' & ')}
                        </span>
                        <span className="text-[9px] text-tertiary font-bold block">
                            {pit.stints?.join(' → ')}
                        </span>
                    </div>
                )}
            </header>

            {/* Rule violation banner */}
            {violation && (
                <div className="flex items-center gap-3 bg-amber-500/10 border border-amber-500/30 px-4 py-3 rounded">
                    <span className="text-amber-400 text-lg">⚠</span>
                    <div>
                        <span className="text-amber-400 text-[10px] font-bold uppercase block">Regulation Violation</span>
                        <span className="text-amber-200 text-xs">{violation}</span>
                    </div>
                </div>
            )}

            <div className="grid grid-cols-12 gap-gutter">
                <div className="col-span-12 lg:col-span-4 space-y-gutter">
                    <div className="grid grid-cols-2 gap-2">
                        <div className="glass-panel p-stack-md">
                            <label className="text-[10px] text-slate-400 font-bold uppercase mb-2 block">Track</label>
                            <select 
                                className="w-full bg-white/5 border border-white/10 text-white text-xs p-2 uppercase font-bold"
                                value={selectedTrack?.id || ''}
                                onChange={(e) => handleTrackChange(tracks.find(t => t.id === e.target.value))}
                            >
                                {tracks.map(t => <option key={t.id} value={t.id} className="bg-[#1a1a1a]">{t.name}</option>)}
                            </select>
                        </div>
                        <div className="glass-panel p-stack-md">
                            <label className="text-[10px] text-slate-400 font-bold uppercase mb-2 block">Car</label>
                            <select 
                                className="w-full bg-white/5 border border-white/10 text-white text-xs p-2 uppercase font-bold"
                                value={selectedCar || ''}
                                onChange={(e) => setSelectedCar(e.target.value)}
                            >
                                {cars.map(c => <option key={c.id} value={c.id} className="bg-[#1a1a1a]">{c.model}</option>)}
                            </select>
                        </div>
                    </div>

                    <div className="glass-panel p-stack-md">
                        <label className="text-[10px] text-slate-400 font-bold uppercase mb-2 block">Pit Stop Strategy</label>
                        <div className="grid grid-cols-2 gap-2">
                            {[1, 2].map(s => (
                                <button key={s} onClick={() => setStops(s)}
                                    className={`border p-2 text-[10px] font-bold transition-all ${stops === s ? 'border-[#E10600] bg-[#E10600]/10 text-white' : 'border-white/10 bg-white/5 text-slate-400 hover:bg-white/10'}`}>
                                    {s} STOP{s > 1 ? 'S' : ''}
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* Stint compound selectors */}
                    <CompoundSelector label="Stint 1 — Starting Compound" value={compound} onChange={setCompound} />
                    <CompoundSelector label="Stint 2 — After Pit 1" value={stint2Compound} onChange={setStint2Compound} />
                    {stops >= 2 && (
                        <CompoundSelector label="Stint 3 — After Pit 2" value={stint3Compound} onChange={setStint3Compound} />
                    )}

                    <div className="glass-panel p-stack-md">
                        <div className="flex justify-between items-center mb-4">
                            <label className="text-[10px] font-bold text-slate-400 uppercase">Fuel Load (kg)</label>
                            <span className="font-data-mono text-cyan-400">{fuel} KG</span>
                        </div>
                        <input className="w-full h-1 bg-white/10 appearance-none cursor-pointer custom-slider" max="110" min="0" type="range" value={fuel} onChange={e => setFuel(+e.target.value)}/>
                    </div>
                    <div className="glass-panel p-stack-md space-y-2">
                        <span className="text-[10px] text-slate-400 font-bold uppercase">Simulation Output</span>
                        {simResult?.car && (
                            <div className="flex justify-between text-xs py-1 border-b border-white/5">
                                <span className="text-slate-400">Car Profile</span>
                                <span className="text-white font-bold">
                                    Deg: {simResult.car.tire_wear_mult}x | Aero: {simResult.car.downforce}x
                                </span>
                            </div>
                        )}
                        <div className="flex justify-between text-xs py-1 border-b border-white/5"><span className="text-slate-400">Fuel Penalty</span><span className="text-tertiary font-bold">{simResult?.fuel_penalty_per_lap_s?.toFixed(3) || '—'}s/lap</span></div>
                        <div className="flex justify-between text-xs py-1 border-b border-white/5"><span className="text-slate-400">Estimated Stint Loss</span><span className="text-primary-container font-bold">{pit.estimated_total_loss_s || '—'}s</span></div>
                        <div className="flex justify-between text-xs py-1"><span className="text-slate-400">Strategy Path</span><span className="text-white font-bold">{pit.stints?.join(' → ') || '—'}</span></div>
                    </div>
                </div>
                <div className="col-span-12 lg:col-span-8 glass-panel h-[550px] flex flex-col p-6">
                    <div className="flex justify-between items-center mb-2">
                        <span className="text-[10px] font-bold text-slate-300 uppercase">Grip Degradation & Pit Window</span>
                    </div>
                    {/* Stint bar showing compound segments */}
                    {pit.stints && pit.stints.length > 0 && (
                        <div className="flex gap-0.5 mb-4 h-5 rounded overflow-hidden">
                            {pit.stints.map((comp, i) => {
                                const pitLaps = pit.recommended_pit_laps || [];
                                const start = i === 0 ? 1 : pitLaps[i - 1] + 1;
                                const end = i < pitLaps.length ? pitLaps[i] : totalLaps;
                                const widthPct = ((end - start + 1) / totalLaps) * 100;
                                return (
                                    <div
                                        key={i}
                                        className="flex items-center justify-center text-[8px] font-bold uppercase tracking-wider"
                                        style={{
                                            width: `${widthPct}%`,
                                            background: COMPOUND_COLORS[comp] + '33',
                                            borderBottom: `2px solid ${COMPOUND_COLORS[comp]}`,
                                            color: COMPOUND_COLORS[comp],
                                        }}
                                    >
                                        {comp} (L{start}–{end})
                                    </div>
                                );
                            })}
                        </div>
                    )}
                    <div className="flex-1 w-full h-full min-h-0">
                        {curve.length > 0 && (
                            <ResponsiveContainer width="100%" height="100%">
                                <ComposedChart data={curve} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
                                    <XAxis dataKey="lap" stroke="#666" tick={{ fill: '#888', fontSize: 10 }} />
                                    <YAxis yAxisId="left" stroke="#666" tick={{ fill: '#888', fontSize: 10 }} domain={[0, 100]} />
                                    <YAxis yAxisId="right" orientation="right" stroke="#666" tick={{ fill: '#888', fontSize: 10 }} />
                                    <Tooltip content={<CustomTooltip />} />
                                    <Legend wrapperStyle={{ fontSize: '10px' }} iconType="circle" />
                                    <Line yAxisId="left" type="monotone" dataKey="grip" name="Grip %" stroke="#E10600" strokeWidth={2} dot={false} activeDot={{ r: 4 }} />
                                    <Line yAxisId="right" type="monotone" dataKey="lap_time_delta" name="Lap Delta (s)" stroke="#00dbe9" strokeWidth={2} dot={false} activeDot={{ r: 4 }} />
                                    {pit.recommended_pit_laps?.map((l, i) => (
                                        <React.Fragment key={i}>
                                            {/* Highlight Band */}
                                            <ReferenceLine 
                                                yAxisId="left" 
                                                x={l} 
                                                stroke="#E10600" 
                                                strokeWidth={40}
                                                strokeOpacity={0.2}
                                            />
                                            {/* Exact Lap Line */}
                                            <ReferenceLine 
                                                yAxisId="left" 
                                                x={l} 
                                                stroke="#E10600" 
                                                strokeWidth={2}
                                                label={{ position: 'insideTopLeft', value: `PIT ${i+1} (L${l})`, fill: '#E10600', fontSize: 11, fontWeight: 'bold' }} 
                                            />
                                        </React.Fragment>
                                    ))}
                                </ComposedChart>
                            </ResponsiveContainer>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default StrategyPage;
