import { useState, useEffect, useRef } from "react";
import { useTranslation } from "react-i18next";
import { API_URL } from "../config";
import { useTheme } from "../context/ThemeContext";
import Sidebar from "../components/layout/Sidebar";
import Topbar from "../components/layout/Topbar";
import "../styles/dashboard.css";
import "../styles/neural-graph.css";

export default function ModelVisualizationPage() {
  const { t } = useTranslation();
  const { darkMode } = useTheme();
  const [structure, setStructure] = useState(null);
  const [error, setError] = useState(null);
  const [showSettings, setShowSettings] = useState(true);
  const [zoom, setZoom] = useState(100);
  const [selectedNode, setSelectedNode] = useState(null);

  const canvasRef = useRef(null);
  const wrapperRef = useRef(null);
  const nodesRef = useRef([]);
  const linksRef = useRef([]);
  const animationRef = useRef(null);
  const panRef = useRef({ x: 0, y: 0 });
  const dragRef = useRef(null);
  const isPanningRef = useRef(false);
  const lastMouseRef = useRef({ x: 0, y: 0 });
  const darkModeRef = useRef(darkMode);
  useEffect(() => { darkModeRef.current = darkMode; }, [darkMode]);

  // Load structure on mount
  useEffect(() => {
    fetch(`${API_URL}/models/structure`)
      .then(res => res.json())
      .then(data => {
        console.log("Structure loaded:", data);
        setStructure(data);
      })
      .catch(err => {
        console.error("Failed to load structure:", err);
        setError(err.message);
      });
  }, []);

  // Build graph when structure loads
  useEffect(() => {
    if (!structure) return;

    const width = 1200;
    const height = 700;
    const centerX = width / 2;
    const centerY = height / 2;

    const nodes = [];
    const links = [];

    const colors = {
      categorical: "#60a5fa",
      numerical: "#a78bfa",
      temporal: "#fb923c",
      lag: "#4ade80",
      cyclic: "#f472b6",
      transform: "#fbbf24",
      model: "#34d399",
      output: "#f87171",
    };

    const inputFeatures = structure.layers?.[0]?.features || {};

    // Categorical features (left)
    (inputFeatures.categorical || []).forEach((f, i) => {
      nodes.push({
        id: `cat_${i}`, label: f, color: colors.categorical, size: 24,
        x: centerX - 450, y: centerY - 150 + i * 70,
      });
    });

    // Numerical features (left-center)
    (inputFeatures.numerical || []).forEach((f, i) => {
      nodes.push({
        id: `num_${i}`, label: f.substring(0, 12), color: colors.numerical, size: 20,
        x: centerX - 280, y: centerY - 130 + i * 50,
      });
    });

    // Temporal features (top)
    (inputFeatures.temporal || []).forEach((f, i) => {
      nodes.push({
        id: `temp_${i}`, label: f, color: colors.temporal, size: 18,
        x: centerX - 100 + i * 90, y: centerY - 280,
      });
    });

    // Lag features (bottom)
    (inputFeatures.lag_features || []).forEach((f, i) => {
      const col = i % 4;
      const row = Math.floor(i / 4);
      nodes.push({
        id: `lag_${i}`, label: f.replace("demand_", "").substring(0, 10), color: colors.lag, size: 16,
        x: centerX - 300 + col * 90, y: centerY + 180 + row * 60,
      });
    });

    // Cyclic features
    (inputFeatures.cyclic || []).forEach((f, i) => {
      nodes.push({
        id: `cyc_${i}`, label: f, color: colors.cyclic, size: 16,
        x: centerX + 150 + (i % 2) * 80, y: centerY + 200 + Math.floor(i / 2) * 50,
      });
    });

    // Transform nodes
    nodes.push({
      id: "onehot", label: "OneHotEncoder", color: colors.transform, size: 38,
      x: centerX - 50, y: centerY - 80,
    });
    nodes.push({
      id: "passthrough", label: "Passthrough", color: colors.transform, size: 34,
      x: centerX - 50, y: centerY + 80,
    });

    // Random Forest
    nodes.push({
      id: "forest", label: "Random Forest", color: colors.model, size: 60,
      x: centerX + 200, y: centerY,
    });

    // Trees around forest
    for (let i = 0; i < 8; i++) {
      const angle = (i / 8) * Math.PI * 2 - Math.PI / 2;
      nodes.push({
        id: `tree_${i}`, label: `T${i + 1}`, color: "#4ade80", size: 14,
        x: centerX + 200 + Math.cos(angle) * 100,
        y: centerY + Math.sin(angle) * 100,
      });
    }

    // Output
    nodes.push({
      id: "output", label: "Demand Forecast", color: colors.output, size: 45,
      x: centerX + 450, y: centerY,
    });

    // Create links
    (inputFeatures.categorical || []).forEach((_, i) => {
      links.push({ source: `cat_${i}`, target: "onehot", color: colors.categorical });
    });
    (inputFeatures.numerical || []).forEach((_, i) => {
      links.push({ source: `num_${i}`, target: "passthrough", color: colors.numerical });
    });
    (inputFeatures.temporal || []).forEach((_, i) => {
      links.push({ source: `temp_${i}`, target: "passthrough", color: colors.temporal });
    });
    (inputFeatures.lag_features || []).forEach((_, i) => {
      links.push({ source: `lag_${i}`, target: "passthrough", color: colors.lag });
    });
    (inputFeatures.cyclic || []).forEach((_, i) => {
      links.push({ source: `cyc_${i}`, target: "passthrough", color: colors.cyclic });
    });

    links.push({ source: "onehot", target: "forest", color: colors.transform, width: 4 });
    links.push({ source: "passthrough", target: "forest", color: colors.transform, width: 4 });

    for (let i = 0; i < 8; i++) {
      links.push({ source: `tree_${i}`, target: "forest", color: "#4ade80" });
    }

    links.push({ source: "forest", target: "output", color: colors.model, width: 3 });

    // Stagger pulse animation offsets per link
    links.forEach((link, i) => { link._offset = i * 280; });

    nodesRef.current = nodes;
    linksRef.current = links;
  }, [structure]);

  // Setup canvas and animation
  useEffect(() => {
    const canvas = canvasRef.current;
    const wrapper = wrapperRef.current;
    if (!canvas || !wrapper) return;

    const resize = () => {
      const dpr = window.devicePixelRatio || 1;
      const rect = wrapper.getBoundingClientRect();
      canvas.width = rect.width * dpr;
      canvas.height = rect.height * dpr;
      canvas.style.width = rect.width + "px";
      canvas.style.height = rect.height + "px";
    };

    resize();
    window.addEventListener("resize", resize);

    let running = true;

    const draw = () => {
      if (!running) return;

      const dpr = window.devicePixelRatio || 1;
      const ctx = canvas.getContext("2d");
      const width = canvas.width / dpr;
      const height = canvas.height / dpr;

      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

      const dark = darkModeRef.current;

      // Background
      ctx.fillStyle = "#08080f";
      ctx.fillRect(0, 0, width, height);

      // Dot grid
      const dotColor = "rgba(255,255,255,0.03)";
      for (let gx = 0; gx <= width; gx += 36) {
        for (let gy = 0; gy <= height; gy += 36) {
          ctx.beginPath();
          ctx.fillStyle = dotColor;
          ctx.arc(gx, gy, 1, 0, Math.PI * 2);
          ctx.fill();
        }
      }

      // Apply zoom and pan
      const scale = zoom / 100;
      ctx.save();
      ctx.translate(width / 2 + panRef.current.x, height / 2 + panRef.current.y);
      ctx.scale(scale, scale);
      ctx.translate(-600, -350);

      const nodes = nodesRef.current;
      const links = linksRef.current;

      // Draw links
      links.forEach(link => {
        const source = nodes.find(n => n.id === link.source);
        const target = nodes.find(n => n.id === link.target);
        if (!source || !target) return;

        // Clean single line
        ctx.beginPath();
        ctx.strokeStyle = link.color + "28";
        ctx.lineWidth = link.width || 1.5;
        ctx.lineCap = "round";
        ctx.moveTo(source.x, source.y);
        ctx.lineTo(target.x, target.y);
        ctx.stroke();

        // Staggered pulse dot
        const progress = ((Date.now() + (link._offset || 0)) % 2200) / 2200;
        const px = source.x + (target.x - source.x) * progress;
        const py = source.y + (target.y - source.y) * progress;

        ctx.beginPath();
        ctx.fillStyle = "rgba(255,255,255,0.7)";
        ctx.arc(px, py, 2.5, 0, Math.PI * 2);
        ctx.fill();
      });

      // Draw nodes
      nodes.forEach(node => {
        const { x, y, label, color } = node;
        const isSelected = selectedNode === node.id;

        // Breathing animation on forest node
        const breathe = node.id === "forest"
          ? 1 + Math.sin(Date.now() / 900) * 0.05
          : 1;
        const r = node.size * breathe;

        // Selection dashed ring
        if (isSelected) {
          ctx.beginPath();
          ctx.strokeStyle = color + "55";
          ctx.lineWidth = 1;
          ctx.setLineDash([4, 4]);
          ctx.arc(x, y, r + 10, 0, Math.PI * 2);
          ctx.stroke();
          ctx.setLineDash([]);
        }

        // Fill
        ctx.beginPath();
        ctx.fillStyle = color + "1a";
        ctx.arc(x, y, r, 0, Math.PI * 2);
        ctx.fill();

        // Border
        ctx.beginPath();
        ctx.strokeStyle = color + "bb";
        ctx.lineWidth = isSelected ? 2 : 1.5;
        ctx.arc(x, y, r, 0, Math.PI * 2);
        ctx.stroke();

        // Label
        const labelColor = "rgba(255,255,255,0.82)";
        ctx.font = node.size > 30
          ? "600 12px -apple-system, BlinkMacSystemFont, sans-serif"
          : "500 10px -apple-system, BlinkMacSystemFont, sans-serif";
        ctx.textAlign = "center";
        ctx.fillStyle = labelColor;

        if (node.size > 30) {
          ctx.fillText(label, x, y + 4);
        } else {
          ctx.fillText(label, x, y + r + 14);
        }
      });

      ctx.restore();

      // Legend
      const legendItems = [
        { color: "#60a5fa", label: t('model.categorical') },
        { color: "#a78bfa", label: t('model.numerical') },
        { color: "#fb923c", label: t('model.temporal') },
        { color: "#4ade80", label: t('model.lagFeatures') },
        { color: "#f472b6", label: t('model.cyclic') },
        { color: "#fbbf24", label: t('model.transform') },
        { color: "#34d399", label: "Trees" },
      ];

      const lx = 16, ly = 16, lw = 126, lh = legendItems.length * 22 + 30;
      ctx.fillStyle = "rgba(8,8,15,0.88)";
      if (ctx.roundRect) {
        ctx.beginPath();
        ctx.roundRect(lx, ly, lw, lh, 8);
        ctx.fill();
        ctx.strokeStyle = "rgba(255,255,255,0.07)";
        ctx.lineWidth = 1;
        ctx.stroke();
      } else {
        ctx.fillRect(lx, ly, lw, lh);
      }

      ctx.font = "600 10px -apple-system, BlinkMacSystemFont, sans-serif";
      ctx.fillStyle = "#4b5563";
      ctx.textAlign = "left";
      ctx.fillText(t('model.legend').toUpperCase(), lx + 12, ly + 18);

      legendItems.forEach((item, i) => {
        const iy = ly + 30 + i * 22;
        ctx.beginPath();
        ctx.fillStyle = item.color;
        ctx.arc(lx + 18, iy, 4, 0, Math.PI * 2);
        ctx.fill();
        ctx.fillStyle = "#d1d5db";
        ctx.font = "11px -apple-system, BlinkMacSystemFont, sans-serif";
        ctx.fillText(item.label, lx + 30, iy + 4);
      });

      // Hint
      ctx.font = "11px -apple-system, BlinkMacSystemFont, sans-serif";
      ctx.fillStyle = "rgba(255,255,255,0.18)";
      ctx.textAlign = "right";
      ctx.fillText(t('model.dragInstructions'), width - 15, height - 15);

      animationRef.current = requestAnimationFrame(draw);
    };

    draw();

    return () => {
      running = false;
      window.removeEventListener("resize", resize);
      if (animationRef.current) cancelAnimationFrame(animationRef.current);
    };
  }, [structure, zoom, selectedNode]);

  // Mouse handlers
  const getMousePos = (e) => {
    const canvas = canvasRef.current;
    const rect = canvas.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;
    const scale = zoom / 100;
    const width = canvas.width / dpr;
    const height = canvas.height / dpr;

    const mx = (e.clientX - rect.left - width / 2 - panRef.current.x) / scale + 600;
    const my = (e.clientY - rect.top - height / 2 - panRef.current.y) / scale + 350;
    return { mx, my };
  };

  const handleMouseDown = (e) => {
    if (e.button === 2) {
      // Right click - pan
      isPanningRef.current = true;
      lastMouseRef.current = { x: e.clientX, y: e.clientY };
      return;
    }

    const { mx, my } = getMousePos(e);
    const clickedNode = nodesRef.current.find(n => {
      const dx = n.x - mx;
      const dy = n.y - my;
      return Math.sqrt(dx * dx + dy * dy) < n.size;
    });

    if (clickedNode) {
      dragRef.current = clickedNode;
      setSelectedNode(clickedNode.id);
    } else {
      setSelectedNode(null);
      isPanningRef.current = true;
      lastMouseRef.current = { x: e.clientX, y: e.clientY };
    }
  };

  const handleMouseMove = (e) => {
    if (dragRef.current) {
      const { mx, my } = getMousePos(e);
      dragRef.current.x = mx;
      dragRef.current.y = my;
    } else if (isPanningRef.current) {
      const dx = e.clientX - lastMouseRef.current.x;
      const dy = e.clientY - lastMouseRef.current.y;
      panRef.current.x += dx;
      panRef.current.y += dy;
      lastMouseRef.current = { x: e.clientX, y: e.clientY };
    }
  };

  const handleMouseUp = () => {
    dragRef.current = null;
    isPanningRef.current = false;
  };

  const handleWheel = (e) => {
    e.preventDefault();
    const delta = e.deltaY > 0 ? -5 : 5;
    setZoom(prev => Math.min(200, Math.max(30, prev + delta)));
  };

  const handleContextMenu = (e) => {
    e.preventDefault();
  };

  return (
    <div className="appShell">
      <Sidebar />
      <div className="main">
        <Topbar />

        <div className="neural-graph-page">
          <div className="graph-header">
            <div className="graph-title">
              <h1>{t('model.title')}</h1>
              <span className="graph-subtitle">{t('model.subtitle')}</span>
            </div>
            <div className="graph-controls">
              <span className="zoom-indicator">
                {t('model.zoom')}: {zoom}%
              </span>
              <button className="settings-btn" onClick={() => { panRef.current = { x: 0, y: 0 }; setZoom(100); }}>
                {t('model.resetView')}
              </button>
              <button className="settings-btn" onClick={() => setShowSettings(!showSettings)}>
                {showSettings ? t('model.hidePanel') : t('model.showPanel')}
              </button>
            </div>
          </div>

          {error && <div className="graph-error">{t('common.error')}: {error}</div>}

          <div className="graph-container">
            <div className="canvas-wrapper" ref={wrapperRef}>
              <canvas
                ref={canvasRef}
                onMouseDown={handleMouseDown}
                onMouseMove={handleMouseMove}
                onMouseUp={handleMouseUp}
                onMouseLeave={handleMouseUp}
                onWheel={handleWheel}
                onContextMenu={handleContextMenu}
                style={{ cursor: dragRef.current ? "grabbing" : "grab" }}
              />
            </div>

            {showSettings && (
              <div className="settings-panel">
                <h3>{t('model.modelInfo')}</h3>

                <div className="metrics-panel">
                  <div className="metric-row">
                    <span>{t('model.type')}</span>
                    <span className="metric-value">
                      {structure?.model_type || '—'}
                    </span>
                  </div>
                  <div className="metric-row">
                    <span>{t('model.trees')}</span>
                    <span className="metric-value">
                      {structure?.layers?.[2]?.config?.n_estimators ?? '—'}
                    </span>
                  </div>
                  <div className="metric-row">
                    <span>{t('model.features')}</span>
                    <span className="metric-value">
                      {structure
                        ? Object.values(structure.layers?.[0]?.features || {}).flat().length
                        : '—'}
                    </span>
                  </div>
                  <div className="metric-row">
                    <span>{t('common.status')}</span>
                    <span className="metric-value" style={{ color: structure ? "var(--success)" : "var(--warning)" }}>
                      {structure ? t('model.loaded') : t('model.loadingModel')}
                    </span>
                  </div>
                </div>

                {selectedNode && (
                  <div className="node-info">
                    <h4>{t('model.selectedNode')}</h4>
                    <div className="info-row">
                      <span>{t('model.id')}</span>
                      <span>{selectedNode}</span>
                    </div>
                  </div>
                )}

                <div className="settings-group">
                  <label>{t('model.zoomLevel')}</label>
                  <input
                    type="range"
                    min="30"
                    max="200"
                    value={zoom}
                    onChange={(e) => setZoom(Number(e.target.value))}
                  />
                  <span>{zoom}%</span>
                </div>

                <div className="features-list">
                  <h4>{t('model.pipelineStages')}</h4>
                  {[t('model.inputFeatures'), t('model.preprocessing'), t('model.randomForest'), t('model.predictionStage')].map((stage, i) => (
                    <div key={i} className="feature-row">
                      <span className="feature-rank">{i + 1}</span>
                      <span className="feature-name">{stage}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
