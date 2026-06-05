const BrandMark = ({ compact = false }) => {
  return (
    <div className={`brand-mark ${compact ? 'brand-mark-compact' : ''}`}>
      <div className="brand-sigil" aria-hidden="true">
        <span />
      </div>
      {!compact && (
        <div className="brand-copy">
          <strong>NEXUS Gate</strong>
          <small>Secure Access Console</small>
        </div>
      )}
    </div>
  );
};

export default BrandMark;
