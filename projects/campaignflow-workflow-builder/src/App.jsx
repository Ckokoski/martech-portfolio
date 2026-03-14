import React, { useCallback, useRef } from 'react';
import ReactFlow, {
  ReactFlowProvider,
  Background,
  Controls,
  MiniMap,
} from 'reactflow';
import 'reactflow/dist/style.css';

import useWorkflowStore from './store/workflowStore';
import Sidebar from './components/Sidebar';
import Toolbar from './components/Toolbar';
import ConfigPanel from './components/ConfigPanel';
import TriggerNode from './components/nodes/TriggerNode';
import ConditionNode from './components/nodes/ConditionNode';
import ActionNode from './components/nodes/ActionNode';
import TimingNode from './components/nodes/TimingNode';

const nodeTypes = {
  triggerNode: TriggerNode,
  conditionNode: ConditionNode,
  actionNode: ActionNode,
  timingNode: TimingNode,
};

const minimapNodeColor = (node) => {
  switch (node.type) {
    case 'triggerNode': return '#16a34a';
    case 'conditionNode': return '#ca8a04';
    case 'actionNode': return '#2563eb';
    case 'timingNode': return '#9333ea';
    default: return '#64748b';
  }
};

function FlowCanvas() {
  const reactFlowWrapper = useRef(null);
  const [reactFlowInstance, setReactFlowInstance] = React.useState(null);

  const nodes = useWorkflowStore((s) => s.nodes);
  const edges = useWorkflowStore((s) => s.edges);
  const onNodesChange = useWorkflowStore((s) => s.onNodesChange);
  const onEdgesChange = useWorkflowStore((s) => s.onEdgesChange);
  const onConnect = useWorkflowStore((s) => s.onConnect);
  const addNode = useWorkflowStore((s) => s.addNode);
  const setSelectedNode = useWorkflowStore((s) => s.setSelectedNode);
  const selectedNode = useWorkflowStore((s) => s.selectedNode);

  const onDragOver = useCallback((event) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
  }, []);

  const onDrop = useCallback(
    (event) => {
      event.preventDefault();

      const data = event.dataTransfer.getData('application/reactflow');
      if (!data) return;

      const { nodeType, label, subtype, description } = JSON.parse(data);

      const position = reactFlowInstance.screenToFlowPosition({
        x: event.clientX,
        y: event.clientY,
      });

      addNode(nodeType, position, { label, subtype, description });
    },
    [reactFlowInstance, addNode]
  );

  const onNodeClick = useCallback(
    (_, node) => {
      setSelectedNode(node.id);
    },
    [setSelectedNode]
  );

  const onPaneClick = useCallback(() => {
    setSelectedNode(null);
  }, [setSelectedNode]);

  return (
    <div className="canvas-wrapper" ref={reactFlowWrapper}>
      <ReactFlow
        nodes={nodes.map((n) => ({
          ...n,
          selected: n.id === selectedNode,
        }))}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        onInit={setReactFlowInstance}
        onDrop={onDrop}
        onDragOver={onDragOver}
        onNodeClick={onNodeClick}
        onPaneClick={onPaneClick}
        nodeTypes={nodeTypes}
        fitView
        fitViewOptions={{ padding: 0.2 }}
        defaultEdgeOptions={{
          type: 'smoothstep',
          animated: true,
        }}
        deleteKeyCode="Backspace"
        proOptions={{ hideAttribution: true }}
      >
        <Background color="#d1d5db" gap={20} size={1} />
        <Controls
          showInteractive={false}
          className="flow-controls"
        />
        <MiniMap
          nodeColor={minimapNodeColor}
          nodeStrokeWidth={3}
          zoomable
          pannable
          className="flow-minimap"
        />
      </ReactFlow>
    </div>
  );
}

function App() {
  return (
    <ReactFlowProvider>
      <div className="app-container">
        <Toolbar />
        <div className="app-body">
          <Sidebar />
          <FlowCanvas />
          <ConfigPanel />
        </div>
      </div>
    </ReactFlowProvider>
  );
}

export default App;
