function FieldError({ children }) {
  if (!children) return null;
  return <p className="field-error">{children}</p>;
}

export default FieldError;
