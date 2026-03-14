import React, { useState, useRef, useEffect } from 'react';
import useWorkflowStore from '../store/workflowStore';
import { templates } from '../data/templates';

const Toolbar = () => {
  const [showTemplates, setShowTemplates] = useState(false);
  const [showValidation, setShowValidation] = useState(false);
  const dropdownRef = useRef(null);
  const validationRef = useRef(null);

  const loadTemplate = useWorkflowStore((s) => s.loadTemplate);
  const clearCanvas = useWorkflowStore((s) => s.clearCanvas);
  const validateWorkflow = useWorkflowStore((s) => s.validateWorkflow);
  const exportWorkflow = useWorkflowStore((s) => s.exportWorkflow);
  const validationErrors = useWorkflowStore((s) => s.validationErrors);
  const nodes = useWorkflowStore((s) => s.nodes);

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setShowTemplates(false);
      }
      if (validationRef.current && !validationRef.current.contains(e.target)) {
        setShowValidation(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleValidate = () => {
    validateWorkflow();
    setShowValidation(true);
  };

  const handleLoadTemplate = (template) => {
    loadTemplate(template);
    setShowTemplates(false);
  };

  const handleClear = () => {
    if (nodes.length === 0 || window.confirm('Clear the entire canvas? This cannot be undone.')) {
      clearCanvas();
    }
  };

  return (
    <div className="toolbar">
      <div className="toolbar-left">
        <div className="toolbar-brand">
          <span className="toolbar-title">Workflow Builder</span>
          <span className="toolbar-badge">{nodes.length} nodes</span>
        </div>
      </div>

      <div className="toolbar-center">
        {/* Templates dropdown */}
        <div className="toolbar-dropdown-wrapper" ref={dropdownRef}>
          <button
            className="toolbar-btn toolbar-btn-secondary"
            onClick={() => {
              setShowTemplates(!showTemplates);
              setShowValidation(false);
            }}
          >
            <span className="btn-icon">&#128196;</span>
            Templates
            <span className="btn-chevron">&#9662;</span>
          </button>
          {showTemplates && (
            <div className="toolbar-dropdown">
              <div className="dropdown-header">Pre-built Templates</div>
              {templates.map((t) => (
                <button
                  key={t.id}
                  className="dropdown-item"
                  onClick={() => handleLoadTemplate(t)}
                >
                  <div className="dropdown-item-name">{t.name}</div>
                  <div className="dropdown-item-desc">{t.description}</div>
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Validate button */}
        <div className="toolbar-dropdown-wrapper" ref={validationRef}>
          <button
            className="toolbar-btn toolbar-btn-primary"
            onClick={handleValidate}
          >
            <span className="btn-icon">&#10003;</span>
            Validate
          </button>
          {showValidation && validationErrors.length > 0 && (
            <div className="toolbar-dropdown validation-dropdown">
              <div className="dropdown-header">Validation Results</div>
              {validationErrors.map((err, i) => (
                <div key={i} className={`validation-item validation-${err.type}`}>
                  <span className="validation-icon">
                    {err.type === 'error' ? '\u2716' : err.type === 'warning' ? '\u26A0' : '\u2714'}
                  </span>
                  <span>{err.message}</span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Export button */}
        <button className="toolbar-btn toolbar-btn-secondary" onClick={exportWorkflow}>
          <span className="btn-icon">&#8615;</span>
          Export JSON
        </button>

        {/* Clear button */}
        <button className="toolbar-btn toolbar-btn-danger" onClick={handleClear}>
          <span className="btn-icon">&#10005;</span>
          Clear
        </button>
      </div>

      <div className="toolbar-right">
        <span className="toolbar-hint">Drag &amp; drop nodes from the sidebar</span>
      </div>
    </div>
  );
};

export default Toolbar;
