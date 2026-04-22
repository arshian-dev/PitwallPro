import React, { useState, useEffect } from 'react';
import { fetchJSON } from '../api';
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer, Tooltip, Legend } from 'recharts';

const CarLabPage = () => {
    const [cars, setCars] = useState([]);
    const [car1, setCar1] = useState(null);
    const [car2, setCar2] = useState(null);
    const [comparison, setComparison] = useState(null);

    useEffect(() => {
        fetchJSON('/cars').then(data => {
            setCars(data);
            if (data.length >= 2) { setCar1(data[0]); setCar2(data[1]); }
        }).catch(e => console.warn("Cars offline", e));
    }, []);

    useEffect(() => {
        if (car1 && car2) {
            fetchJSON(`/cars/compare/${car1.car_id}/${car2.car_id}`)
                .then(setComparison)
                .catch(e => console.warn("Compare offline", e));
        }
    }, [car1, car2]);

    const dims = ['horsepower', 'torque', 'weight', 'top_speed', 'acceleration'];
    const dimLabels = { horsepower: 'Power', torque: 'Torque', weight: 'Weight', top_speed: 'Top Speed', acceleration: 'Accel' };

    const radarData = dims.map(d => ({
        subject: dimLabels[d],
        car1: comparison?.car1?.[d] || 50,
        car2: comparison?.car2?.[d] || 50,
        fullMark: 100,
    }));

    return (
        <div className="p-margin space-y-stack-lg">
            <header className="flex flex-col md:flex-row md:items-end justify-between gap-4">
                <div>
                    <div className="flex items-center gap-2 mb-2">
                        <span className="w-2 h-2 rounded-full bg-tertiary glow-cyan animate-pulse"></span>
                        <span className="font-label-caps text-label-caps text-tertiary">LABORATORY SESSION ACTIVE</span>
                    </div>
                    <h1 className="font-headline-xl text-headline-xl text-on-background uppercase">CAR COMPARISON <span className="text-primary-container italic">LAB</span></h1>
                </div>
                <div className="flex gap-3">
                    <select className="bg-white/5 border border-white/10 text-white text-xs p-2 uppercase font-bold" value={car1?.car_id || ''} onChange={e => setCar1(cars.find(c => c.car_id === +e.target.value))}>
                        {cars.map(c => <option key={c.car_id} value={c.car_id} className="bg-[#1a1a1a]">{c.team_name} — {c.model}</option>)}
                    </select>
                    <span className="text-slate-500 self-center font-bold text-xs">VS</span>
                    <select className="bg-white/5 border border-white/10 text-white text-xs p-2 uppercase font-bold" value={car2?.car_id || ''} onChange={e => setCar2(cars.find(c => c.car_id === +e.target.value))}>
                        {cars.map(c => <option key={c.car_id} value={c.car_id} className="bg-[#1a1a1a]">{c.team_name} — {c.model}</option>)}
                    </select>
                </div>
            </header>
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-gutter">
                {/* Car 1 */}
                <div className="lg:col-span-4 glass-card p-stack-md relative overflow-hidden group">
                    <div className="absolute top-0 left-0 w-full h-1 bg-primary-container"></div>
                    <h3 className="font-headline-md text-headline-md uppercase text-white mb-4">{car1?.team_name || 'TEAM'} <span className="text-primary-container">{car1?.model || ''}</span></h3>
                    <div className="space-y-2">
                        <div className="flex justify-between text-xs py-2 border-b border-white/5"><span>Horsepower</span><span className="text-primary-container font-bold">{car1?.horsepower || '—'} HP</span></div>
                        <div className="flex justify-between text-xs py-2 border-b border-white/5"><span>Torque</span><span className="text-white font-bold">{car1?.torque || '—'} NM</span></div>
                        <div className="flex justify-between text-xs py-2 border-b border-white/5"><span>Weight</span><span className="text-white font-bold">{car1?.weight || '—'} KG</span></div>
                        <div className="flex justify-between text-xs py-2 border-b border-white/5"><span>Top Speed</span><span className="text-primary-container font-bold">{car1?.top_speed || '—'} KM/H</span></div>
                        <div className="flex justify-between text-xs py-2 border-b border-white/5"><span>0-100 km/h</span><span className="text-white font-bold">{car1?.acceleration || '—'}s</span></div>
                        <div className="flex justify-between text-xs py-2"><span>Power/Weight</span><span className="text-tertiary font-bold">{car1?.power_to_weight || '—'}</span></div>
                    </div>
                </div>
                {/* Radar */}
                <div className="lg:col-span-4 glass-card p-stack-md radar-grid flex items-center justify-center min-h-[400px]">
                    {comparison ? (
                        <ResponsiveContainer width="100%" height="100%">
                            <RadarChart cx="50%" cy="50%" outerRadius="70%" data={radarData}>
                                <PolarGrid stroke="rgba(255,255,255,0.1)" />
                                <PolarAngleAxis dataKey="subject" tick={{ fill: '#888', fontSize: 10, fontWeight: 'bold' }} />
                                <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
                                <Radar name={car1?.model} dataKey="car1" stroke="#E10600" fill="#E10600" fillOpacity={0.2} strokeWidth={2} />
                                <Radar name={car2?.model} dataKey="car2" stroke="#00DBE9" fill="#00DBE9" fillOpacity={0.1} strokeWidth={2} strokeDasharray="3 3" />
                                <Tooltip 
                                    contentStyle={{ backgroundColor: '#1a1a1a', border: '1px solid rgba(255,255,255,0.1)', color: '#fff', fontSize: '10px', textTransform: 'uppercase' }} 
                                    itemStyle={{ fontSize: '12px', fontWeight: 'bold' }}
                                />
                                <Legend wrapperStyle={{ fontSize: '10px' }} iconType="circle" />
                            </RadarChart>
                        </ResponsiveContainer>
                    ) : (
                        <span className="text-slate-500 text-sm">Select two cars to compare</span>
                    )}
                </div>
                {/* Car 2 */}
                <div className="lg:col-span-4 glass-card p-stack-md relative overflow-hidden group">
                    <div className="absolute top-0 left-0 w-full h-1 bg-tertiary"></div>
                    <h3 className="font-headline-md text-headline-md uppercase text-white mb-4">{car2?.team_name || 'TEAM'} <span className="text-tertiary">{car2?.model || ''}</span></h3>
                    <div className="space-y-2">
                        <div className="flex justify-between text-xs py-2 border-b border-white/5"><span>Horsepower</span><span className="text-tertiary font-bold">{car2?.horsepower || '—'} HP</span></div>
                        <div className="flex justify-between text-xs py-2 border-b border-white/5"><span>Torque</span><span className="text-white font-bold">{car2?.torque || '—'} NM</span></div>
                        <div className="flex justify-between text-xs py-2 border-b border-white/5"><span>Weight</span><span className="text-white font-bold">{car2?.weight || '—'} KG</span></div>
                        <div className="flex justify-between text-xs py-2 border-b border-white/5"><span>Top Speed</span><span className="text-tertiary font-bold">{car2?.top_speed || '—'} KM/H</span></div>
                        <div className="flex justify-between text-xs py-2 border-b border-white/5"><span>0-100 km/h</span><span className="text-white font-bold">{car2?.acceleration || '—'}s</span></div>
                        <div className="flex justify-between text-xs py-2"><span>Power/Weight</span><span className="text-primary-container font-bold">{car2?.power_to_weight || '—'}</span></div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default CarLabPage;
