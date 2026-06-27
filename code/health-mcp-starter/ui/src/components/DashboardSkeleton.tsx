export function DashboardSkeleton() {
  return (
    <div className="dashboard-skeleton" aria-hidden="true">
      <div className="skel skel-hero" />
      <div className="skel-grid">
        <div className="skel skel-card tall" />
        <div className="skel skel-card" />
      </div>
    </div>
  );
}
