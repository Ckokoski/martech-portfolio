import React, { memo } from 'react';
import { Handle, Position } from 'reactflow';
import useWorkflowStore from '../../store/workflowStore';

const ConditionNode = memo(({ id, data, selected }) => {
  const setSelectedNode = useWorkflowStore((s) => s.setSelectedNode);

  return (
    <div
      className={`workflow-node condition-node ${selected ? 'selected' : ''}`}
      onClick={() => setSelectedNode(id)}
    >
      <div className="node-header condition-header">
        <span className="node-icon">&#9670;</span>
        <span className="node-category">CONDITION</span>
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
        id="yes"
        className="handle handle-source handle-yes"
        style={{ left: '35%' }}
      />
      <Handle
        type="source"
        position={Position.Bottom}
        id="no"
        className="handle handle-source handle-no"
        style={{ left: '65%' }}
      />
      <div className="condition-labels">
        <span className="condition-label-yes">Yes</span>
        <span className="condition-label-no">No</span>
      </div>
    </div>
  );
});

ConditionNode.displayName = 'ConditionNode';
export default ConditionNode;
