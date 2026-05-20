const labels = {
  valid: 'Válido',
  invalid: 'Inválido',
  not_verified: 'Não verificado',
  warning: 'Atenção',
  neutral: 'Info',
};

function StatusBadge({ status = 'neutral', children }) {
  return <span className={`status-badge ${status}`}>{children || labels[status] || status}</span>;
}

export default StatusBadge;
