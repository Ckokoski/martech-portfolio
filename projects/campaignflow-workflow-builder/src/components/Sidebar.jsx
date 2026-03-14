import React, { useState } from 'react';
import { nodeCategories } from '../data/nodeDefinitions';

const Sidebar = () => {
  const [expandedCategories, setExpandedCategories] = useState(
    nodeCategories.reduce((acc, cat) => ({ ...acc, [cat.id]: true }), {})
  );

  const toggleCategory = (categoryId) => {
    setExpandedCategories((prev) => ({
      ...prev,
      [categoryId]: !prev[categoryId],
    }));
  };

  const onDragStart = (event, nodeType, item) => {
    const dragData = JSON.stringify({
      nodeType,
      label: item.label,
      subtype: item.subtype,
      description: item.description,
    });
    event.dataTransfer.setData('application/reactflow', dragData);
    event.dataTransfer.effectAllowed = 'move';
  };

  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <div className="sidebar-logo">
          <span className="logo-icon">&#9889;</span>
          <span className="logo-text">CampaignFlow</span>
        </div>
        <p className="sidebar-subtitle">Drag nodes onto the canvas</p>
      </div>

      <div className="sidebar-content">
        {nodeCategories.map((category) => (
          <div key={category.id} className="node-category-group">
            <button
              className="category-header"
              onClick={() => toggleCategory(category.id)}
              style={{ '--category-color': category.color }}
            >
              <span className="category-indicator" style={{ background: category.color }} />
              <span className="category-icon">{category.icon}</span>
              <span className="category-label">{category.label}</span>
              <span className={`category-chevron ${expandedCategories[category.id] ? 'expanded' : ''}`}>
                &#9662;
              </span>
            </button>

            {expandedCategories[category.id] && (
              <div className="category-items">
                {category.items.map((item) => (
                  <div
                    key={item.subtype}
                    className="draggable-node"
                    draggable
                    onDragStart={(e) => onDragStart(e, category.nodeType, item)}
                    style={{ '--node-color': category.color }}
                  >
                    <span className="draggable-node-icon" style={{ color: category.color }}>
                      {category.icon}
                    </span>
                    <div className="draggable-node-info">
                      <span className="draggable-node-label">{item.label}</span>
                      <span className="draggable-node-desc">{item.description}</span>
                    </div>
                    <span className="drag-handle">&#8942;&#8942;</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>

      <div className="sidebar-footer">
        <div className="sidebar-footer-text">
          <span>Built with React Flow</span>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
