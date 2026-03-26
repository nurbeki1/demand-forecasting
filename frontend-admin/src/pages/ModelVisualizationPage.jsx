import { useState, useEffect, useRef } from "react";
import { NavLink } from "react-router-dom";
import { API_URL } from "../config";
import "../styles/neural-graph.css";

// Simple Sidebar without auth dependency
function SimpleSidebar() {
  const menuItems = [
    { path: "/", label: "Dashboard", icon: "◉" },
    { path: "/charts", label: "Charts", icon: "◈" },
    { path: "/table", label: "Table", icon: "☰" },
    { path: "/upload", label: "Upload", icon: "↑" },
    { path: "/chat", label: "AI Chat", icon: "◇" },
    { path: "/model", label: "ML Model", icon: "⬡" },
  ];

  return (
    <aside className="sidebar">
      <div className="profile">
        <div className="avatar">DF</div>
        <div>
          <div className="name">Neural View</div>
          <div className="role">Admin Panel</div>
        </div>
      </div>
      <nav className="menu">
        {menuItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) => `menuItem ${isActive ? "active" : ""}`}
          >
            <span style={{ fontSize: "16px", opacity: 0.7 }}>{item.icon}</span>
            {item.label}
          </NavLink>
        ))}
      </nav>

      <div style={{
        padding: "16px",
        borderTop: "1px solid rgba(0, 229, 255, 0.12)",
        marginTop: "auto"
      }}>
        <div style={{
          padding: "12px",
          background: "rgba(0, 229, 255, 0.08)",
          borderRadius: "8px",
          border: "1px solid rgba(0, 229, 255, 0.15)"
        }}>
          <div style={{
            fontFamily: "'Space Mono', monospace",
            fontSize: "10px",
            color: "#4a6580",
            textTransform: "uppercase",
            letterSpacing: "0.1em",
            marginBottom: "4px"
          }}>
            System Status
          </div>
          <div style={{
            display: "flex",
            alignItems: "center",
            gap: "8px"
          }}>
            <span style={{
              width: "8px",
              height: "8px",
              background: "#00ff88",
              borderRadius: "50%",
              boxShadow: "0 0 10px #00ff88"
            }}></span>
            <span style={{
              fontFamily: "'Space Mono', monospace",
              fontSize: "12px",
              color: "#00ff88"
            }}>
              Online
            </span>
          </div>
        </div>
      </div>
    </aside>
  );
}

export default function ModelVisualizationPage() {
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
      categorical: "#00e5ff",
      numerical: "#7c3aed",
      temporal: "#ff6b2b",
      lag: "#00ff88",
      cyclic: "#ff00ff",
      transform: "#ffaa00",
      model: "#00ff88",
      output: "#ff6b2b",
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
        id: `tree_${i}`, label: `T${i + 1}`, color: "#22c55e", size: 14,
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
      links.push({ source: `tree_${i}`, target: "forest", color: "#22c55e" });
    }

    links.push({ source: "forest", target: "output", color: colors.model, width: 5 });

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

      // Clear
      ctx.fillStyle = "#080c14";
      ctx.fillRect(0, 0, width, height);

      // Grid
      ctx.strokeStyle = "rgba(0, 229, 255, 0.04)";
      ctx.lineWidth = 1;
      for (let x = 0; x < width; x += 50) {
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, height);
        ctx.stroke();
      }
      for (let y = 0; y < height; y += 50) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(width, y);
        ctx.stroke();
      }

      // Apply zoom and pan
      const scale = zoom / 100;
      ctx.save();
      ctx.translate(width / 2 + panRef.current.x, height / 2 + panRef.current.y);
      ctx.scale(scale, scale);
      ctx.translate(-600, -350); // Center the graph

      const nodes = nodesRef.current;
      const links = linksRef.current;

      // Draw links
      links.forEach(link => {
        const source = nodes.find(n => n.id === link.source);
        const target = nodes.find(n => n.id === link.target);
        if (!source || !target) return;

        // Line glow
        ctx.beginPath();
        ctx.strokeStyle = link.color + "25";
        ctx.lineWidth = (link.width || 2) + 6;
        ctx.lineCap = "round";
        ctx.moveTo(source.x, source.y);
        ctx.lineTo(target.x, target.y);
        ctx.stroke();

        // Main line
        ctx.beginPath();
        ctx.strokeStyle = link.color + "80";
        ctx.lineWidth = link.width || 2;
        ctx.moveTo(source.x, source.y);
        ctx.lineTo(target.x, target.y);
        ctx.stroke();

        // Animated pulse
        const t = (Date.now() % 2500) / 2500;
        const px = source.x + (target.x - source.x) * t;
        const py = source.y + (target.y - source.y) * t;

        ctx.beginPath();
        ctx.fillStyle = "#ffffff";
        ctx.shadowColor = link.color;
        ctx.shadowBlur = 12;
        ctx.arc(px, py, 5, 0, Math.PI * 2);
        ctx.fill();
        ctx.shadowBlur = 0;
      });

      // Draw nodes
      nodes.forEach(node => {
        const { x, y, size, color, label } = node;
        const isSelected = selectedNode === node.id;

        // Outer glow
        const glow = ctx.createRadialGradient(x, y, 0, x, y, size * 2.5);
        glow.addColorStop(0, color + "50");
        glow.addColorStop(1, "transparent");
        ctx.beginPath();
        ctx.fillStyle = glow;
        ctx.arc(x, y, size * 2.5, 0, Math.PI * 2);
        ctx.fill();

        // Selection ring
        if (isSelected) {
          ctx.beginPath();
          ctx.strokeStyle = "#ffffff";
          ctx.lineWidth = 2;
          ctx.arc(x, y, size + 8, 0, Math.PI * 2);
          ctx.stroke();
        }

        // Node border
        ctx.beginPath();
        ctx.strokeStyle = color;
        ctx.lineWidth = 3;
        ctx.shadowColor = color;
        ctx.shadowBlur = 20;
        ctx.arc(x, y, size, 0, Math.PI * 2);
        ctx.stroke();
        ctx.shadowBlur = 0;

        // Node fill
        ctx.beginPath();
        ctx.fillStyle = color + "35";
        ctx.arc(x, y, size, 0, Math.PI * 2);
        ctx.fill();

        // Inner core
        ctx.beginPath();
        ctx.fillStyle = color + "90";
        ctx.arc(x, y, size * 0.4, 0, Math.PI * 2);
        ctx.fill();

        // Label
        ctx.font = size > 30 ? "bold 13px Arial" : "bold 11px Arial";
        ctx.fillStyle = "#ffffff";
        ctx.textAlign = "center";
        ctx.shadowColor = "#000";
        ctx.shadowBlur = 5;

        if (size > 30) {
          ctx.fillText(label, x, y + 4);
        } else {
          ctx.fillText(label, x, y + size + 16);
        }
        ctx.shadowBlur = 0;
      });

      ctx.restore();

      // Draw legend (not affected by zoom/pan)
      const legendItems = [
        { color: "#00e5ff", label: "Categorical" },
        { color: "#7c3aed", label: "Numerical" },
        { color: "#ff6b2b", label: "Temporal" },
        { color: "#00ff88", label: "Lag Features" },
        { color: "#ff00ff", label: "Cyclic" },
        { color: "#ffaa00", label: "Transform" },
        { color: "#22c55e", label: "Trees" },
      ];

      ctx.fillStyle = "rgba(8, 12, 20, 0.95)";
      ctx.fillRect(15, 15, 130, legendItems.length * 24 + 25);
      ctx.strokeStyle = "rgba(0, 229, 255, 0.3)";
      ctx.lineWidth = 1;
      ctx.strokeRect(15, 15, 130, legendItems.length * 24 + 25);

      ctx.font = "bold 11px Arial";
      ctx.fillStyle = "#4a6580";
      ctx.textAlign = "left";
      ctx.fillText("LEGEND", 25, 34);

      legendItems.forEach((item, i) => {
        const ly = 52 + i * 24;
        ctx.beginPath();
        ctx.fillStyle = item.color;
        ctx.shadowColor = item.color;
        ctx.shadowBlur = 6;
        ctx.arc(30, ly, 6, 0, Math.PI * 2);
        ctx.fill();
        ctx.shadowBlur = 0;
        ctx.fillStyle = "#e8f4f8";
        ctx.font = "12px Arial";
        ctx.fillText(item.label, 45, ly + 4);
      });

      // Instructions
      ctx.font = "11px Arial";
      ctx.fillStyle = "#4a6580";
      ctx.textAlign = "right";
      ctx.fillText("Drag nodes • Scroll to zoom • Right-click to pan", width - 15, height - 15);

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
      <SimpleSidebar />
      <div className="main">
        <div className="topbar">
          <div className="search">
            <input placeholder="Quick search" />
          </div>
          <div className="topActions">
            <span style={{ fontFamily: "'Space Mono', monospace", fontSize: "12px", color: "#4a6580" }}>
              ML Visualization
            </span>
          </div>
        </div>

        <div className="neural-graph-page">
          <div className="graph-header">
            <div className="graph-title">
              <h1>ML Model Architecture</h1>
              <span className="graph-subtitle">Random Forest Pipeline • Drag nodes to rearrange</span>
            </div>
            <div className="graph-controls">
              <span style={{ color: "#4a6580", fontSize: "12px", marginRight: "12px" }}>
                Zoom: {zoom}%
              </span>
              <button className="settings-btn" onClick={() => { panRef.current = { x: 0, y: 0 }; setZoom(100); }}>
                Reset View
              </button>
              <button className="settings-btn" onClick={() => setShowSettings(!showSettings)}>
                {showSettings ? "Hide Panel" : "Show Panel"}
              </button>
            </div>
          </div>

          {error && <div className="graph-error">Error: {error}</div>}

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
                <h3>Model Info</h3>

                <div className="metrics-panel">
                  <div className="metric-row">
                    <span>Type</span>
                    <span className="metric-value">RandomForest</span>
                  </div>
                  <div className="metric-row">
                    <span>Trees</span>
                    <span className="metric-value">300</span>
                  </div>
                  <div className="metric-row">
                    <span>Features</span>
                    <span className="metric-value">25+</span>
                  </div>
                  <div className="metric-row">
                    <span>Status</span>
                    <span className="metric-value" style={{ color: structure ? "#00ff88" : "#ffaa00" }}>
                      {structure ? "Loaded" : "Loading..."}
                    </span>
                  </div>
                </div>

                {selectedNode && (
                  <div className="node-info">
                    <h4>Selected Node</h4>
                    <div className="info-row">
                      <span>ID</span>
                      <span>{selectedNode}</span>
                    </div>
                  </div>
                )}

                <div className="settings-group">
                  <label>Zoom Level</label>
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
                  <h4>Pipeline Stages</h4>
                  {["Input Features", "Preprocessing", "Random Forest", "Prediction"].map((stage, i) => (
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
