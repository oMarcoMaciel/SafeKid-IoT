export function getChartOptions(isHeatmap: boolean, isCurve: boolean, isBar: boolean, title?: string) {
  const isLine = isCurve;
  
  return {
    chart: {
      height: 350,
      type: (isLine ? 'line' : (isHeatmap ? 'heatmap' : (isBar ? 'bar' : 'area'))) as 'line',
      stacked: (isBar || (!isLine && !isHeatmap)) && !isLine,
      stackType: (isBar ? '100%' : undefined) as '100%' | 'normal' | undefined,
      toolbar: {
        show: false
      },
      animations: {
        enabled: true,
        easing: 'easeinout' as const,
        speed: 800,
        animateGradually: {
          enabled: true,
          delay: 150
        },
        dynamicAnimation: {
          enabled: true,
          speed: 350
        }
      }
    },
    dataLabels: {
      enabled: false
    },
    colors: isLine ? ["#6366f1"] : ["#22c55e", "#3b82f6", "#eab308"],
    title: {
      text: title,
      align: 'left' as const,
      style: {
        fontSize: '14px',
        fontWeight: 'bold',
        fontFamily: 'Inter, sans-serif',
        color: '#1e293b'
      }
    },
    annotations: isLine ? {
      yaxis: [
        {
          y: -55,
          y2: 0,
          fillColor: '#22c55e',
          opacity: 0.1,
          label: {
            text: 'VERY NEAR',
            style: { color: '#15803d', background: '#f0fdf4', fontSize: '9px', fontWeight: 'bold' }
          }
        },
        {
          y: -75,
          y2: -55,
          fillColor: '#3b82f6',
          opacity: 0.1,
          label: {
            text: 'NEAR',
            style: { color: '#1d4ed8', background: '#eff6ff', fontSize: '9px', fontWeight: 'bold' }
          }
        },
        {
          y: -100,
          y2: -75,
          fillColor: '#eab308',
          opacity: 0.1,
          label: {
            text: 'FAR',
            style: { color: '#a16207', background: '#fefce8', fontSize: '9px', fontWeight: 'bold' }
          }
        }
      ]
    } : undefined,
    xaxis: {
      type: 'datetime' as const,
      labels: {
        datetimeUTC: false,
        style: {
          fontSize: '10px'
        }
      }
    },
    yaxis: {
      min: isLine ? -100 : undefined,
      max: isLine ? -30 : undefined,
      title: {
        text: isLine ? 'Signal (RSSI dBm)' : (isBar ? 'Activity (%)' : undefined),
        style: {
          fontSize: '10px',
          fontWeight: 'bold',
          color: '#64748b'
        }
      },
      labels: {
        formatter: (val: number) => {
          if (isLine) return `${val.toFixed(0)}dBm`;
          if (isBar) return `${Math.round(val).toString()}%`;
          return val.toString();
        },
        style: {
          fontSize: '10px'
        }
      }
    },
    stroke: {
      curve: 'smooth' as const,
      width: isHeatmap ? 0 : 3
    },
    plotOptions: {
      heatmap: isHeatmap ? {
        shadeIntensity: 0.5,
        radius: 2,
        useFillColorAsStroke: true,
        colorScale: {
          ranges: [
            { from: 1, to: 10, name: 'Low Activity', color: '#e2e8f0' },
            { from: 11, to: 30, name: 'Moderate Activity', color: '#94a3b8' },
            { from: 31, to: 70, name: 'High Activity', color: '#6366f1' },
            { from: 71, to: 1000, name: 'Intense Activity', color: '#4338ca' }
          ]
        }
      } : undefined,
      bar: {
        horizontal: false,
        borderRadius: 4,
        columnWidth: '60%',
      }
    },
    tooltip: {
      shared: true,
      intersect: false,
      x: {
        format: 'dd MMM HH:mm'
      },
      y: {
        formatter: (val: number, opts?: { 
          seriesIndex: number, 
          dataPointIndex: number, 
          w: { globals: { seriesPercent: number[][] } } 
        }) => {
          if (isLine) {
            return `${val.toFixed(1)} dBm`;
          }
          
          if (isBar && opts) {
            const seriesIndex = opts.seriesIndex;
            const dataPointIndex = opts.dataPointIndex;
            try {
              const seriesPercent = opts.w.globals.seriesPercent[seriesIndex];
              const percent = seriesPercent ? seriesPercent[dataPointIndex] : undefined;
              return percent !== undefined 
                ? `${val.toString()} pings (${percent.toFixed(1)}%)`
                : `${val.toString()} pings`;
            } catch (e) {
              return `${val.toString()} pings`;
            }
          }
          return val.toString();
        }
      }
    },
    legend: {
      position: 'top' as const,
      horizontalAlign: 'right' as const,
      fontSize: '12px',
      fontFamily: 'Inter, sans-serif',
      show: true
    }
  };
}
