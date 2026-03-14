import React, { memo } from 'react';
import { Handle, Position } from 'reactflow';
import useWorkflowStore from '../../store/workflowStore';

const TriggerNode = memo(({ id, data, selected }) => {
  const setSelectedNode = useWorkflowStore((s) => s.setSelectedNode);

  return (
    <div
      className={`workflow-node trigger-node ${selected ? 'selected' : ''}`}
      onClick={() => setSelectedNode(id)}
    >
      <div className="node-header trigger-header">
        <span className="node-icon">&#9889;</span>
        <span className="node-category">TRIGGER</span>
      </div>
      <div className="node-body">
        <div className="node-label">{data.label}</div>
        {data.description && (
          <div className="node-description">{data.description}</div>
        )}
      </div>
      <Handle
        type="source"
        position={Position.Bottom}
        className="handle handle-source"
      />
    </div>
  );
});

TriggerNode.displayName = 'TriggerNode';
export default TriggerNode;
