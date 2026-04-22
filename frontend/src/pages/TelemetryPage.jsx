import React, { useState, useEffect } from 'react';
import { fetchJSON } from '../api';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const TelemetryPage = () => {
    const [telemetry, setTelemetry] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchJSON('/telemetry/latest?limit=300')
            .then(data => { setTelemetry(data); setLoading(false); })
            .catch(() => setLoading(false));
    }, []);

    // Group by driver for two-line chart
    const drivers = [...new Set(telemetry.map(t => t.driver_id))];
    const d1 = telemetry.filter(t => t.driver_id === drivers[0]);
    const d2 = telemetry.filter(t => t.driver_id === drivers[1]);

    // Format data for Recharts (merge points by index)
    const chartData = [];
    const maxLen = Math.max(d1.length, d2.length);
    for (let i = 0; i < maxLen; i++) {
        chartData.push({
            sample: i,
            driver1: d1[i]?.speed || null,
            driver2: d2[i]?.speed || null,
        });
    }

    // Live gauges from latest sample
    const latest = telemetry[telemetry.length - 1] || {};
    const brakePercent = latest.brake != null ? Math.round(latest.brake) : 88;
    const throttlePercent = latest.throttle != null ? Math.round(latest.throttle) : 72;

    // Compute some aggregates
    const avgSpeed = telemetry.length > 0
        ? Math.round(telemetry.reduce((s, t) => s + (t.speed || 0), 0) / telemetry.length)
        : 0;
    const maxSpeed = telemetry.length > 0
        ? Math.round(Math.max(...telemetry.map(t => t.speed || 0)))
        : 0;

    const d1Name = d1[0]?.driver_name?.split(' ').pop() || 'Driver 1';
    const d2Name = d2[0]?.driver_name?.split(' ').pop() || 'Driver 2';

    return (
        <div className="p-6 space-y-6">
            {/* Stat bar */}
            <div className="grid grid-cols-4 gap-4">
                <div className="glass-panel p-3">
                    <p className="text-[9px] text-slate-500 font-bold uppercase">Samples</p>
                    <p className="text-xl font-bold text-white">{telemetry.length}</p>
                </div>
                <div className="glass-panel p-3">
                    <p className="text-[9px] text-slate-500 font-bold uppercase">Avg Speed</p>
                    <p className="text-xl font-bold text-tertiary">{avgSpeed} <span className="text-xs text-slate-500">km/h</span></p>
                </div>
                <div className="glass-panel p-3">
                    <p className="text-[9px] text-slate-500 font-bold uppercase">Max Speed</p>
                    <p className="text-xl font-bold text-primary-container">{maxSpeed} <span className="text-xs text-slate-500">km/h</span></p>
                </div>
                <div className="glass-panel p-3">
                    <p className="text-[9px] text-slate-500 font-bold uppercase">Drivers</p>
                    <p className="text-xl font-bold text-white">{drivers.length}</p>
                </div>
            </div>

            <div className="grid grid-cols-12 gap-6 h-[500px]">
                <div className="col-span-8 glass-panel relative flex flex-col p-4">
                    <div className="flex justify-between items-center mb-4">
                        <div className="flex items-center gap-2">
                            <div className="w-1 h-6 bg-[#E10600]"></div>
                            <h2 className="font-headline-md text-white text-lg tracking-tight uppercase">Real-Time Telemetry: V-Max</h2>
                        </div>
                    </div>
                    <div className="flex-1 w-full h-full min-h-0">
                        {loading ? (
                            <div className="flex items-center justify-center h-full">
                                <span className="text-slate-500 animate-pulse text-sm">Loading telemetry stream...</span>
                            </div>
                        ) : (
                            <ResponsiveContainer width="100%" height="100%">
                                <LineChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" vertical={false} />
                                    <XAxis dataKey="sample" stroke="#666" tick={{ fill: '#888', fontSize: 10 }} />
                                    <YAxis stroke="#666" tick={{ fill: '#888', fontSize: 10 }} domain={['dataMin - 10', 'dataMax + 10']} />
                                    <Tooltip 
                                        contentStyle={{ backgroundColor: '#1a1a1a', border: '1px solid rgba(255,255,255,0.1)', color: '#fff', fontSize: '10px', textTransform: 'uppercase' }} 
                                        itemStyle={{ fontSize: '12px', fontWeight: 'bold' }} 
                                    />
                                    <Legend wrapperStyle={{ fontSize: '10px' }} iconType="circle" />
                                    <Line type="monotone" dataKey="driver1" name={d1Name} stroke="#E10600" strokeWidth={2} dot={false} activeDot={{ r: 4 }} />
                                    {drivers.length > 1 && (
                                        <Line type="monotone" dataKey="driver2" name={d2Name} stroke="#00dbe9" strokeWidth={2} dot={false} activeDot={{ r: 4 }} />
                                    )}
                                </LineChart>
                            </ResponsiveContainer>
                        )}
                    </div>
                </div>
                <div className="col-span-4 glass-panel p-4 flex flex-col items-center justify-center">
                    <div className="w-48 h-48 rounded-full border-4 border-white/5 flex items-center justify-center relative">
                        <div className="absolute inset-0 border-t-4 border-[#E10600] rounded-full rotate-45"></div>
                        <div className="flex flex-col items-center">
                            <span className="text-4xl font-black text-white">{brakePercent}%</span>
                            <span className="text-[10px] text-[#E10600] font-bold uppercase">Brake Peak</span>
                        </div>
                    </div>
                    <div className="mt-8 grid grid-cols-2 gap-4 w-full">
                        <div className="bg-white/5 p-3"><p className="text-[9px] text-slate-500 font-bold uppercase">Throttle</p><p className="text-xl font-bold text-white">{throttlePercent}%</p></div>
                        <div className="bg-white/5 p-3"><p className="text-[9px] text-slate-500 font-bold uppercase">Gear</p><p className="text-xl font-bold text-tertiary">{latest.gear || '—'}</p></div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default TelemetryPage;
