import React from 'react';
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';

const RiskTrendChart = ({ data = [], loading = false, title = 'Risk Trend' }) => {
    if (loading) {
        return (
            <div style={{ 
                padding: '20px', 
                background: '#151929', 
                borderRadius: '12px', 
                border: '1px solid #2a2a4a',
                height: '300px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
            }}>
                <div style={{ color: '#666' }}>Loading chart data...</div>
            </div>
        );
    }

    if (!data || data.length === 0) {
        return (
            <div style={{ 
                padding: '20px', 
                background: '#151929', 
                borderRadius: '12px', 
                border: '1px solid #2a2a4a',
                height: '300px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                flexDirection: 'column'
            }}>
                <div style={{ fontSize: '24px', marginBottom: '8px' }}>📊</div>
                <div style={{ color: '#666' }}>No risk trend data available</div>
            </div>
        );
    }

    return (
        <div style={{ 
            padding: '20px', 
            background: '#151929', 
            borderRadius: '12px', 
            border: '1px solid #2a2a4a'
        }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                <h3 style={{ margin: 0, fontSize: '16px', color: '#fff' }}>{title}</h3>
                <span style={{ fontSize: '12px', color: '#666' }}>Last 30 days</span>
            </div>
            <ResponsiveContainer width="100%" height={250}>
                <LineChart data={data}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#2a2a4a" />
                    <XAxis dataKey="date" stroke="#666" tick={{ fontSize: 10 }} />
                    <YAxis stroke="#666" tick={{ fontSize: 10 }} />
                    <Tooltip 
                        contentStyle={{ 
                            background: '#1a1a2e', 
                            border: '1px solid #2a2a4a', 
                            borderRadius: '8px',
                            color: '#fff'
                        }}
                        labelStyle={{ color: '#fff' }}
                    />
                    <Legend />
                    <Line 
                        type="monotone" 
                        dataKey="total_cases" 
                        stroke="#1976d2" 
                        name="Total Cases" 
                        strokeWidth={2}
                    />
                    <Line 
                        type="monotone" 
                        dataKey="high_risk_cases" 
                        stroke="#d32f2f" 
                        name="High Risk" 
                        strokeWidth={2}
                    />
                </LineChart>
            </ResponsiveContainer>
        </div>
    );
};

export default RiskTrendChart;
