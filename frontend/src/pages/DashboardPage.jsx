import React, { useState, useEffect } from 'react';
import { fetchJSON } from '../api';

const DashboardPage = () => {
    const [stats, setStats] = useState({
        fastest_car: { value: 324.8, driver: 'CAR 16', sector: 'S3' },
        efficiency: 98.2,
        constructor_lead: 'STRATOS',
        avg_lap_time: '1:31.402'
    });
    const [alerts, setAlerts] = useState([]);

    useEffect(() => {
        fetchJSON('/dashboard/stats').then(setStats).catch(e => console.warn("Dashboard stats offline", e));
        fetchJSON('/alerts').then(setAlerts).catch(e => console.warn("Alerts offline", e));
    }, []);

    const severityIcon = (sev) => {
        if (!sev) return { icon: 'info', color: 'text-blue-400', bg: '' };
        const s = sev.toUpperCase();
        if (s === 'CRITICAL') return { icon: 'error_outline', color: 'text-primary-container', bg: 'bg-primary-container/5' };
        if (s === 'WARNING') return { icon: 'warning', color: 'text-yellow-500', bg: '' };
        return { icon: 'info', color: 'text-cyan-400', bg: '' };
    };

    return (
        <div className="p-margin space-y-gutter">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-gutter">
                <div className="glass-card p-stack-md relative overflow-hidden group">
                    <div className="flex justify-between items-start mb-2">
                        <span className="font-label-caps text-slate-500 uppercase">Fastest Car</span>
                        <span className="material-symbols-outlined text-primary-container text-lg">speed</span>
                    </div>
                    <div className="flex flex-col">
                        <span className="font-headline-md text-white text-3xl">{stats.fastest_car.value} <span className="text-xs text-slate-500">KM/H</span></span>
                        <span className="font-label-caps text-tertiary mt-1">{stats.fastest_car.sector} - {stats.fastest_car.driver}</span>
                    </div>
                    <div className="mt-4 h-1 bg-white/5 rounded-full overflow-hidden">
                        <div className="h-full bg-primary-container w-[88%]"></div>
                    </div>
                </div>
                <div className="glass-card p-stack-md relative overflow-hidden">
                    <div className="flex justify-between items-start mb-2">
                        <span className="font-label-caps text-slate-500 uppercase">Best Efficiency</span>
                        <span className="material-symbols-outlined text-tertiary text-lg">bolt</span>
                    </div>
                    <div className="flex flex-col">
                        <span className="font-headline-md text-white text-3xl">{stats.efficiency}<span className="text-xs text-slate-500">%</span></span>
                        <span className="font-label-caps text-slate-400 mt-1">HYBRID DEPLOYMENT</span>
                    </div>
                    <div className="mt-4 h-1 bg-white/5 rounded-full overflow-hidden">
                        <div className="h-full bg-tertiary w-[98%] shadow-[0_0_8px_rgba(0,219,233,0.5)]"></div>
                    </div>
                </div>
                <div className="glass-card p-stack-md relative overflow-hidden">
                    <div className="flex justify-between items-start mb-2">
                        <span className="font-label-caps text-slate-500 uppercase">Top Constructor</span>
                        <span className="material-symbols-outlined text-slate-400 text-lg">engineering</span>
                    </div>
                    <div className="flex flex-col">
                        <span className="font-headline-md text-white text-3xl uppercase tracking-tighter">{stats.constructor_lead}</span>
                        <span className="font-label-caps text-primary-container mt-1">+1.2S GAP LEAD</span>
                    </div>
                    <div className="mt-4 h-1 bg-white/5 rounded-full overflow-hidden">
                        <div className="h-full bg-primary-container w-[75%]"></div>
                    </div>
                </div>
                <div className="glass-card p-stack-md relative overflow-hidden">
                    <div className="flex justify-between items-start mb-2">
                        <span className="font-label-caps text-slate-500 uppercase">Avg Lap Time</span>
                        <span className="material-symbols-outlined text-slate-400 text-lg">timer</span>
                    </div>
                    <div className="flex flex-col">
                        <span className="font-headline-md text-white text-3xl tabular-nums">{stats.avg_lap_time}</span>
                        <span className="font-label-caps text-slate-400 mt-1">LAST 10 LAPS</span>
                    </div>
                    <div className="mt-4 h-1 bg-white/5 rounded-full overflow-hidden">
                        <div className="h-full bg-white/40 w-[60%]"></div>
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-12 gap-gutter">
                <div className="col-span-12 lg:col-span-8 glass-card flex flex-col min-h-[400px]">
                    <div className="flex justify-between items-center p-stack-md border-b border-white/10">
                        <div>
                            <h3 className="font-headline-md text-lg text-white uppercase tracking-tight">Lap Time Trends</h3>
                            <p className="font-label-caps text-slate-500">REAL-TIME TELEMETRY STREAM (COMP 1 vs COMP 2)</p>
                        </div>
                        <div className="flex gap-2">
                            <span className="flex items-center gap-1 font-label-caps text-[9px] text-primary-container"><span className="w-2 h-2 bg-primary-container rounded-full"></span> CAR 44</span>
                            <span className="flex items-center gap-1 font-label-caps text-[9px] text-tertiary ml-2"><span className="w-2 h-2 bg-tertiary rounded-full"></span> CAR 16</span>
                        </div>
                    </div>
                    <div className="flex-1 p-stack-md relative overflow-hidden telemetry-grid">
                        <svg className="absolute inset-0 w-full h-full px-4 py-8" preserveAspectRatio="none" viewBox="0 0 600 200">
                            <polyline fill="none" points="0,150 50,130 100,160 150,140 200,120 250,100 300,150 350,110 400,170 450,90 500,130 550,120 600,150" stroke="#e10600" strokeWidth="2"></polyline>
                            <polyline fill="none" points="0,170 50,180 100,160 150,190 200,140 250,160 300,150 350,180 400,130 450,170 500,160 550,180 600,150" stroke="#00dbe9" strokeDasharray="4" strokeWidth="1.5"></polyline>
                        </svg>
                    </div>
                </div>
                <div className="col-span-12 lg:col-span-4 glass-card flex flex-col">
                    <div className="p-stack-md border-b border-white/10 flex justify-between items-center">
                        <h3 className="font-headline-md text-lg text-white uppercase tracking-tight">System Alerts</h3>
                        <span className="flex items-center gap-1 font-label-caps text-[9px] text-primary-container px-2 py-1 bg-primary-container/10 border border-primary-container/20">{alerts.length} ACTIVE</span>
                    </div>
                    <div className="flex-1 overflow-y-auto divide-y divide-white/5">
                        {alerts.map((alert, idx) => {
                            const s = severityIcon(alert.severity);
                            return (
                                <div key={alert.alert_id || idx} className={`p-stack-md ${s.bg} flex gap-4`}>
                                    <span className={`material-symbols-outlined ${s.color}`}>{s.icon}</span>
                                    <div>
                                        <h4 className={`font-label-caps ${s.color}`}>{alert.severity || 'INFO'}</h4>
                                        <p className="text-[11px] text-slate-400 leading-tight mt-1">{alert.message}</p>
                                        <p className="text-[9px] text-slate-600 mt-2">LIVE</p>
                                    </div>
                                </div>
                            );
                        })}
                        {alerts.length === 0 && (
                            <div className="p-stack-md text-slate-500 text-sm text-center">No active alerts</div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default DashboardPage;
