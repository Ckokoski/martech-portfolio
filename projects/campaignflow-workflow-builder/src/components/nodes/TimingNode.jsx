import React, { memo } from 'react';
import { Handle, Position } from 'reactflow';
import useWorkflowStore from '../../store/workflowStore';

const TimingNode = memo(({ id, data, selected }) => {
  const setSelectedNode = useWorkflowStore((s) => s.setSelectedNode);

  return (
    <div
      className={`workflow-node timing-node ${selected ? 'selected' : ''}`}
      onClick={() => setSelectedNode(id)}
    >
      <div className="node-header timing-header">
        <span className="node-icon">&#128336;</span>
        <span className="node-category">TIMING</span>
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

TimingNode.displayName = 'TimingNode';
export default TimingNode;
