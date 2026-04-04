/**
 * MarkupSlider Component
 * Interactive slider for adjusting markup percentage with preset buttons
 */

import { useState, useEffect, useRef } from "react";

const PRESET_VALUES = [20, 25, 30, 40, 50];
const DEBOUNCE_DELAY = 300;

export default function MarkupSlider({ value = 25, onChange, disabled = false }) {
  const [localValue, setLocalValue] = useState(value);
  const debounceRef = useRef(null);

  // Sync local value with prop
  useEffect(() => {
    setLocalValue(value);
  }, [value]);

  const handleSliderChange = (e) => {
    const newValue = parseInt(e.target.value, 10);
    setLocalValue(newValue);

    // Debounce the onChange callback
    if (debounceRef.current) {
      clearTimeout(debounceRef.current);
    }
    debounceRef.current = setTimeout(() => {
      onChange?.(newValue);
    }, DEBOUNCE_DELAY);
  };

  const handlePresetClick = (preset) => {
    setLocalValue(preset);
    if (debounceRef.current) {
      clearTimeout(debounceRef.current);
    }
    onChange?.(preset);
  };

  // Cleanup timeout on unmount
  useEffect(() => {
    return () => {
      if (debounceRef.current) {
        clearTimeout(debounceRef.current);
      }
    };
  }, []);

  // Calculate color based on value (green for low, yellow for medium, orange for high)
  const getSliderColor = () => {
    if (localValue <= 25) return "#22c55e"; // green
    if (localValue <= 40) return "#f59e0b"; // yellow/amber
    return "#ef4444"; // red
  };

  const sliderPercentage = ((localValue - 10) / (100 - 10)) * 100;

  return (
    <div className={`kz-markup-slider ${disabled ? "disabled" : ""}`}>
      <div className="kz-slider-header">
        <span className="kz-slider-icon">💹</span>
        <span className="kz-slider-label">Наценка:</span>
        <span className="kz-slider-value" style={{ color: getSliderColor() }}>
          {localValue}%
        </span>
      </div>

      <div className="kz-slider-track-container">
        <input
          type="range"
          min="10"
          max="100"
          step="5"
          value={localValue}
          onChange={handleSliderChange}
          disabled={disabled}
          className="kz-slider-input"
          style={{
            background: `linear-gradient(to right, ${getSliderColor()} 0%, ${getSliderColor()} ${sliderPercentage}%, var(--bg-tertiary) ${sliderPercentage}%, var(--bg-tertiary) 100%)`,
          }}
        />
        <div className="kz-slider-labels">
          <span>10%</span>
          <span>100%</span>
        </div>
      </div>

      <div className="kz-slider-presets">
        {PRESET_VALUES.map((preset) => (
          <button
            key={preset}
            className={`kz-preset-btn ${localValue === preset ? "active" : ""}`}
            onClick={() => handlePresetClick(preset)}
            disabled={disabled}
          >
            {preset}%
            {localValue === preset && <span className="check-mark">✓</span>}
          </button>
        ))}
      </div>
    </div>
  );
}
