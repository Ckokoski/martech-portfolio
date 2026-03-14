import { create } from 'zustand';
import {
  applyNodeChanges,
  applyEdgeChanges,
  addEdge,
  MarkerType,
} from 'reactflow';

let nodeId = 0;
const getNodeId = () => `node_${++nodeId}`;

const useWorkflowStore = create((set, get) => ({
  nodes: [],
  edges: [],
  selectedNode: null,
  validationErrors: [],

  onNodesChange: (changes) => {
    set({
      nodes: applyNodeChanges(changes, get().nodes),
    });
  },

  onEdgesChange: (changes) => {
    set({
      edges: applyEdgeChanges(changes, get().edges),
    });
  },

  onConnect: (connection) => {
    set({
      edges: addEdge(
        {
          ...connection,
          type: 'smoothstep',
          animated: true,
          markerEnd: { type: MarkerType.ArrowClosed, color: '#64748b' },
          style: { stroke: '#64748b', strokeWidth: 2 },
        },
        get().edges
      ),
    });
  },

  setSelectedNode: (nodeId) => {
    set({ selectedNode: nodeId });
  },

  updateNodeData: (nodeId, newData) => {
    set({
      nodes: get().nodes.map((node) =>
        node.id === nodeId
          ? { ...node, data: { ...node.data, ...newData } }
          : node
      ),
    });
  },

  addNode: (type, position, data = {}) => {
    const id = getNodeId();
    const newNode = {
      id,
      type,
      position,
      data: { label: data.label || type, ...data },
    };
    set({ nodes: [...get().nodes, newNode] });
    return id;
  },

  deleteNode: (nodeId) => {
    set({
      nodes: get().nodes.filter((n) => n.id !== nodeId),
      edges: get().edges.filter(
        (e) => e.source !== nodeId && e.target !== nodeId
      ),
      selectedNode: get().selectedNode === nodeId ? null : get().selectedNode,
    });
  },

  clearCanvas: () => {
    nodeId = 0;
    set({ nodes: [], edges: [], selectedNode: null, validationErrors: [] });
  },

  loadTemplate: (template) => {
    nodeId = template.nodes.length;
    set({
      nodes: template.nodes.map((n) => ({ ...n })),
      edges: template.edges.map((e) => ({
        ...e,
        type: 'smoothstep',
        animated: true,
        markerEnd: { type: MarkerType.ArrowClosed, color: '#64748b' },
        style: { stroke: '#64748b', strokeWidth: 2 },
      })),
      selectedNode: null,
      validationErrors: [],
    });
  },

  validateWorkflow: () => {
    const { nodes, edges } = get();
    const errors = [];

    if (nodes.length === 0) {
      errors.push({ type: 'error', message: 'Workflow is empty. Add at least one node.' });
      set({ validationErrors: errors });
      return errors;
    }

    // Check for trigger
    const triggers = nodes.filter((n) => n.type === 'triggerNode');
    if (triggers.length === 0) {
      errors.push({ type: 'error', message: 'Workflow needs at least one Trigger node to start.' });
    }

    // Check for disconnected nodes
    const connectedNodeIds = new Set();
    edges.forEach((e) => {
      connectedNodeIds.add(e.source);
      connectedNodeIds.add(e.target);
    });
    nodes.forEach((n) => {
      if (!connectedNodeIds.has(n.id) && nodes.length > 1) {
        errors.push({
          type: 'warning',
          message: `"${n.data.label}" is disconnected from the workflow.`,
          nodeId: n.id,
        });
      }
    });

    // Check for dead ends (non-trigger nodes with no outgoing edges, excluding timing nodes at the end)
    const nodesWithOutgoing = new Set(edges.map((e) => e.source));
    nodes.forEach((n) => {
      if (n.type !== 'triggerNode' && !nodesWithOutgoing.has(n.id)) {
        const hasIncoming = edges.some((e) => e.target === n.id);
        if (hasIncoming) {
          // It's a leaf node — only warn if it's a condition (conditions should branch)
          if (n.type === 'conditionNode') {
            errors.push({
              type: 'warning',
              message: `"${n.data.label}" is a condition with no outgoing paths.`,
              nodeId: n.id,
            });
          }
        }
      }
    });

    // Check for triggers with no outgoing
    triggers.forEach((t) => {
      if (!nodesWithOutgoing.has(t.id)) {
        errors.push({
          type: 'warning',
          message: `Trigger "${t.data.label}" has no outgoing connection.`,
          nodeId: t.id,
        });
      }
    });

    // Check for nodes with no incoming (except triggers)
    const nodesWithIncoming = new Set(edges.map((e) => e.target));
    nodes.forEach((n) => {
      if (n.type !== 'triggerNode' && !nodesWithIncoming.has(n.id) && connectedNodeIds.has(n.id)) {
        errors.push({
          type: 'warning',
          message: `"${n.data.label}" has no incoming connection — it may be unreachable.`,
          nodeId: n.id,
        });
      }
    });

    if (errors.length === 0) {
      errors.push({ type: 'success', message: 'Workflow is valid! No issues found.' });
    }

    set({ validationErrors: errors });
    return errors;
  },

  exportWorkflow: () => {
    const { nodes, edges } = get();
    const workflow = {
      name: 'CampaignFlow Workflow',
      version: '1.0',
      exportedAt: new Date().toISOString(),
      nodes: nodes.map((n) => ({
        id: n.id,
        type: n.type,
        position: n.position,
        data: n.data,
      })),
      edges: edges.map((e) => ({
        id: e.id,
        source: e.source,
        target: e.target,
        sourceHandle: e.sourceHandle,
        targetHandle: e.targetHandle,
      })),
    };
    const blob = new Blob([JSON.stringify(workflow, null, 2)], {
      type: 'application/json',
    });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'campaignflow-workflow.json';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  },
}));

export default useWorkflowStore;
