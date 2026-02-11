interface GlobalBannerProps {
  activeCount: number;
}

export default function GlobalBanner({ activeCount }: GlobalBannerProps) {
  if (activeCount === 0) return null;

  return (
    <div className="bg-red-500 dark:bg-red-600 text-white py-2 px-4 text-center font-medium">
      🔴 {activeCount} Active Scenario{activeCount !== 1 ? 's' : ''} Running
    </div>
  );
}
