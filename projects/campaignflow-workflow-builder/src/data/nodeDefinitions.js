export const nodeCategories = [
  {
    id: 'triggers',
    label: 'Triggers',
    color: '#16a34a',
    icon: '\u26A1',
    nodeType: 'triggerNode',
    items: [
      { subtype: 'form_submission', label: 'Form Submission', description: 'Triggered when a form is submitted' },
      { subtype: 'list_membership', label: 'List Membership', description: 'Triggered when added to a list' },
      { subtype: 'date_based', label: 'Date-Based', description: 'Triggered on a specific date' },
      { subtype: 'event_based', label: 'Event-Based', description: 'Triggered by a custom event' },
      { subtype: 'api_webhook', label: 'API Webhook', description: 'Triggered by an incoming webhook' },
    ],
  },
  {
    id: 'conditions',
    label: 'Conditions',
    color: '#ca8a04',
    icon: '\u25C6',
    nodeType: 'conditionNode',
    items: [
      { subtype: 'if_else', label: 'If/Else', description: 'Branch based on attribute value' },
      { subtype: 'engagement_check', label: 'Engagement Check', description: 'Check email engagement level' },
      { subtype: 'segment_membership', label: 'Segment Membership', description: 'Check segment membership' },
      { subtype: 'random_split', label: 'Random Split', description: 'Randomly split traffic' },
    ],
  },
  {
    id: 'actions',
    label: 'Actions',
    color: '#2563eb',
    icon: '\u2192',
    nodeType: 'actionNode',
    items: [
      { subtype: 'send_email', label: 'Send Email', description: 'Send an email to the contact' },
      { subtype: 'send_sms', label: 'Send SMS', description: 'Send an SMS message' },
      { subtype: 'update_field', label: 'Update Field', description: 'Update a contact field' },
      { subtype: 'add_to_list', label: 'Add to List', description: 'Add contact to a list' },
      { subtype: 'remove_from_list', label: 'Remove from List', description: 'Remove contact from a list' },
      { subtype: 'create_task', label: 'Create Task', description: 'Create a task for follow-up' },
      { subtype: 'webhook', label: 'Webhook', description: 'Send data to an external URL' },
    ],
  },
  {
    id: 'timing',
    label: 'Timing',
    color: '#9333ea',
    icon: '\uD83D\uDD50',
    nodeType: 'timingNode',
    items: [
      { subtype: 'wait_duration', label: 'Wait Duration', description: 'Wait a set amount of time' },
      { subtype: 'wait_until_date', label: 'Wait Until Date', description: 'Wait until a specific date' },
      { subtype: 'wait_until_event', label: 'Wait Until Event', description: 'Wait for an event to occur' },
    ],
  },
];

export const nodeConfigFields = {
  // Triggers
  form_submission: [
    { key: 'formName', label: 'Form Name', type: 'text', placeholder: 'e.g., Contact Us Form' },
    { key: 'redirectUrl', label: 'Redirect URL', type: 'text', placeholder: 'e.g., /thank-you' },
  ],
  list_membership: [
    { key: 'listName', label: 'List Name', type: 'text', placeholder: 'e.g., Newsletter Subscribers' },
    { key: 'listAction', label: 'Action', type: 'select', options: ['Added to list', 'Removed from list'] },
  ],
  date_based: [
    { key: 'dateField', label: 'Date Field', type: 'text', placeholder: 'e.g., birthday, signup_date' },
    { key: 'offset', label: 'Offset (days)', type: 'number', placeholder: '0' },
  ],
  event_based: [
    { key: 'eventName', label: 'Event Name', type: 'text', placeholder: 'e.g., purchase_completed' },
    { key: 'eventProperty', label: 'Event Property', type: 'text', placeholder: 'e.g., product_category' },
  ],
  api_webhook: [
    { key: 'webhookName', label: 'Webhook Name', type: 'text', placeholder: 'e.g., Shopify Order' },
    { key: 'endpointUrl', label: 'Endpoint URL', type: 'text', placeholder: '/api/webhooks/...' },
  ],
  // Conditions
  if_else: [
    { key: 'attribute', label: 'Attribute Name', type: 'text', placeholder: 'e.g., email_opens' },
    { key: 'operator', label: 'Operator', type: 'select', options: ['equals', 'not equals', 'contains', 'greater than', 'less than'] },
    { key: 'value', label: 'Value', type: 'text', placeholder: 'e.g., 5' },
  ],
  engagement_check: [
    { key: 'metric', label: 'Engagement Metric', type: 'select', options: ['Email Opens', 'Email Clicks', 'Website Visits', 'Page Views'] },
    { key: 'threshold', label: 'Threshold', type: 'number', placeholder: 'e.g., 3' },
    { key: 'period', label: 'Time Period', type: 'select', options: ['Last 7 days', 'Last 30 days', 'Last 90 days'] },
  ],
  segment_membership: [
    { key: 'segmentName', label: 'Segment Name', type: 'text', placeholder: 'e.g., High-Value Customers' },
    { key: 'membershipCheck', label: 'Check', type: 'select', options: ['Is member', 'Is not member'] },
  ],
  random_split: [
    { key: 'splitPercentage', label: 'Split % (Yes path)', type: 'number', placeholder: '50' },
  ],
  // Actions
  send_email: [
    { key: 'templateName', label: 'Email Template', type: 'text', placeholder: 'e.g., Welcome Email v2' },
    { key: 'subjectLine', label: 'Subject Line', type: 'text', placeholder: 'e.g., Welcome to {{company}}!' },
    { key: 'fromName', label: 'From Name', type: 'text', placeholder: 'e.g., Marketing Team' },
  ],
  send_sms: [
    { key: 'smsTemplate', label: 'SMS Template', type: 'text', placeholder: 'e.g., Order Confirmation' },
    { key: 'messagePreview', label: 'Message Preview', type: 'textarea', placeholder: 'Hi {{first_name}}, ...' },
  ],
  update_field: [
    { key: 'fieldName', label: 'Field Name', type: 'text', placeholder: 'e.g., lifecycle_stage' },
    { key: 'fieldValue', label: 'New Value', type: 'text', placeholder: 'e.g., customer' },
  ],
  add_to_list: [
    { key: 'targetList', label: 'Target List', type: 'text', placeholder: 'e.g., Active Customers' },
  ],
  remove_from_list: [
    { key: 'targetList', label: 'Target List', type: 'text', placeholder: 'e.g., Prospects' },
  ],
  create_task: [
    { key: 'taskTitle', label: 'Task Title', type: 'text', placeholder: 'e.g., Follow up with lead' },
    { key: 'assignee', label: 'Assignee', type: 'text', placeholder: 'e.g., Sales Rep' },
    { key: 'dueInDays', label: 'Due In (days)', type: 'number', placeholder: '3' },
  ],
  webhook: [
    { key: 'webhookUrl', label: 'Webhook URL', type: 'text', placeholder: 'https://api.example.com/...' },
    { key: 'httpMethod', label: 'HTTP Method', type: 'select', options: ['POST', 'PUT', 'PATCH'] },
  ],
  // Timing
  wait_duration: [
    { key: 'duration', label: 'Duration', type: 'number', placeholder: 'e.g., 3' },
    { key: 'unit', label: 'Unit', type: 'select', options: ['hours', 'days', 'weeks'] },
  ],
  wait_until_date: [
    { key: 'targetDate', label: 'Target Date', type: 'text', placeholder: 'e.g., 2025-01-15' },
    { key: 'targetTime', label: 'Target Time', type: 'text', placeholder: 'e.g., 09:00 AM' },
  ],
  wait_until_event: [
    { key: 'eventName', label: 'Event Name', type: 'text', placeholder: 'e.g., email_opened' },
    { key: 'timeout', label: 'Timeout (days)', type: 'number', placeholder: '7' },
  ],
};
