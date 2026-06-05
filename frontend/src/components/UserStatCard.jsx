const UserStatCard = ({ icon, label, value, color, className }) => {
  return (
    <div
      className={`user-stat-card ${className || ''}`}
    >
      <div className="user-stat-icon" style={{ color }}>{icon}</div>
      <div className="user-stat-info">
        <div className="user-stat-label">{label}</div>
        <div className="user-stat-value">{value}</div>
      </div>
    </div>
  );
};

export default UserStatCard;
