import React from 'react';

const MetricCard = ({ title, value, subtitle, icon, color = '#1976d2', loading = false }) => {
    if (loading) {
        return (
            <div style={{ 
                padding: '20px', 
                background: '#151929', 
                borderRadius: '12px', 
                border: '1px solid #2a2a4a',
                minHeight: '100px'
            }}>
                <div style={{ height: '20px', background: '#2a2a4a', borderRadius: '4px', marginBottom: '12px' }} />
                <div style={{ height: '32px', background: '#2a2a4a', borderRadius: '4px', width: '60%' }} />
            </div>
        );
    }

    return (
        <div style={{ 
            padding: '20px', 
            background: '#151929', 
            borderRadius: '12px', 
            border: '1px solid #2a2a4a',
            transition: 'all 0.3s ease'
        }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                    <div style={{ fontSize: '12px', color: '#666', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                        {title}
                    </div>
                    <div style={{ fontSize: '28px', fontWeight: 'bold', color: '#fff', marginTop: '4px' }}>
                        {value !== undefined && value !== null ? value : '--'}
                    </div>
                    {subtitle && (
                        <div style={{ fontSize: '12px', color: '#666', marginTop: '4px' }}>
                            {subtitle}
                        </div>
                    )}
                </div>
                {icon && (
                    <div style={{ 
                        fontSize: '32px', 
                        opacity: 0.3,
                        color: color
                    }}>
                        {icon}
                    </div>
                )}
            </div>
        </div>
    );
};

export default MetricCard;
