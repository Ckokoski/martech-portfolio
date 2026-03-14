import React from 'react';
import useWorkflowStore from '../store/workflowStore';
import { nodeConfigFields, nodeCategories } from '../data/nodeDefinitions';

const ConfigPanel = () => {
  const selectedNodeId = useWorkflowStore((s) => s.selectedNode);
  const nodes = useWorkflowStore((s) => s.nodes);
  const updateNodeData = useWorkflowStore((s) => s.updateNodeData);
  const setSelectedNode = useWorkflowStore((s) => s.setSelectedNode);
  const deleteNode = useWorkflowStore((s) => s.deleteNode);

  const node = nodes.find((n) => n.id === selectedNodeId);

  if (!node) {
    return (
      <div className="config-panel config-panel-empty">
        <div className="config-empty-state">
          <div className="config-empty-icon">&#9881;</div>
          <h3>Node Configuration</h3>
          <p>Select a node on the canvas to configure its properties.</p>
          <div className="config-tips">
            <div className="config-tip">
              <span className="tip-icon">&#128073;</span>
              <span>Click a node to select it</span>
            </div>
            <div className="config-tip">
              <span className="tip-icon">&#128257;</span>
              <span>Drag between nodes to connect</span>
            </div>
            <div className="config-tip">
              <span className="tip-icon">&#128465;</span>
              <span>Press Backspace to delete</span>
            </div>
          </div>
        </div>
      </div>
    );
  }

  const subtype = node.data.subtype;
  const fields = nodeConfigFields[subtype] || [];

  // Determine the category info
  const category = nodeCategories.find((c) => c.nodeType === node.type);
  const categoryColor = category?.color || '#64748b';
  const categoryLabel = category?.label || 'Node';
  const categoryIcon = category?.icon || '';

  const handleFieldChange = (key, value) => {
    updateNodeData(node.id, { [key]: value });
  };

  const handleDelete = () => {
    deleteNode(node.id);
  };

  return (
    <div className="config-panel">
      <div className="config-header" style={{ borderLeftColor: categoryColor }}>
        <div className="config-header-top">
          <div className="config-node-type" style={{ color: categoryColor }}>
            <span className="config-type-icon">{categoryIcon}</span>
            <span>{categoryLabel}</span>
          </div>
          <button
            className="config-close-btn"
            onClick={() => setSelectedNode(null)}
            title="Close panel"
          >
            &#10005;
          </button>
        </div>
        <h3 className="config-node-label">{node.data.label}</h3>
        {node.data.description && (
          <p className="config-node-desc">{node.data.description}</p>
        )}
      </div>

      <div className="config-body">
        {/* Label field (always present) */}
        <div className="config-field">
          <label className="config-label">Display Label</label>
          <input
            type="text"
            className="config-input"
            value={node.data.label || ''}
            onChange={(e) => handleFieldChange('label', e.target.value)}
          />
        </div>

        {/* Description field */}
        <div className="config-field">
          <label className="config-label">Description</label>
          <input
            type="text"
            className="config-input"
            value={node.data.description || ''}
            placeholder="Optional description..."
            onChange={(e) => handleFieldChange('description', e.target.value)}
          />
        </div>

        {/* Dynamic fields based on subtype */}
        {fields.length > 0 && (
          <>
            <div className="config-divider" />
            <div className="config-section-title">Configuration</div>
            {fields.map((field) => (
              <div key={field.key} className="config-field">
                <label className="config-label">{field.label}</label>
                {field.type === 'select' ? (
                  <select
                    className="config-input config-select"
                    value={node.data[field.key] || ''}
                    onChange={(e) => handleFieldChange(field.key, e.target.value)}
                  >
                    <option value="">Select...</option>
                    {field.options.map((opt) => (
                      <option key={opt} value={opt}>
                        {opt}
                      </option>
                    ))}
                  </select>
                ) : field.type === 'textarea' ? (
                  <textarea
                    className="config-input config-textarea"
                    value={node.data[field.key] || ''}
                    placeholder={field.placeholder || ''}
                    onChange={(e) => handleFieldChange(field.key, e.target.value)}
                    rows={3}
                  />
                ) : (
                  <input
                    type={field.type}
                    className="config-input"
                    value={node.data[field.key] || ''}
                    placeholder={field.placeholder || ''}
                    onChange={(e) => handleFieldChange(field.key, e.target.value)}
                  />
                )}
              </div>
            ))}
          </>
        )}
      </div>

      <div className="config-footer">
        <button className="config-delete-btn" onClick={handleDelete}>
          <span>&#128465;</span> Delete Node
        </button>
        <div className="config-node-id">ID: {node.id}</div>
      </div>
    </div>
  );
};

export default ConfigPanel;
