import React, { memo } from 'react';
import { Handle, Position } from 'reactflow';
import useWorkflowStore from '../../store/workflowStore';

const ActionNode = memo(({ id, data, selected }) => {
  const setSelectedNode = useWorkflowStore((s) => s.setSelectedNode);

  return (
    <div
      className={`workflow-node action-node ${selected ? 'selected' : ''}`}
      onClick={() => setSelectedNode(id)}
    >
      <div className="node-header action-header">
        <span className="node-icon">&rarr;</span>
        <span className="node-category">ACTION</span>
      </div>
      <div className="node-body">
        <div className="node-label">{data.label}</div>
        {data.description && (
          <div className="node-description">{data.description}</div>
        )}
      </div>
      <Handle
        type="target"
        position={Position.Top}
        className="handle handle-target"
      />
      <Handle
        type="source"
        position={Position.Bottom}
        className="handle handle-source"
      />
    </div>
  );
});

ActionNode.displayName = 'ActionNode';
export default ActionNode;
