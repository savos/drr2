import './StubPage.css';

function StubPage({ title, description }) {
  return (
    <div className="stub-page">
      <div className="stub-content">
        <div className="stub-icon">🚧</div>
        <h1 className="stub-title">{title}</h1>
        <p className="stub-description">
          {description || 'This page is under construction and will be implemented soon.'}
        </p>
        <div className="stub-badge">Coming Soon</div>
      </div>
    </div>
  );
}

export default StubPage;
