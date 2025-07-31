import MomentumDashboard from '@/components/MomentumDashboard';

export default function Home() {
  return (
    <main className="min-h-screen bg-background">
      {/* Header */}
      <div className="momentum-gradient-primary">
        <div className="max-w-7xl mx-auto px-6 py-8">
          <div className="text-center">
            <h1 className="text-4xl font-bold text-white mb-2">
              Relate.io
            </h1>
            <p className="text-blue-100 text-lg">
              AI-Powered Financial Advisory Platform
            </p>
          </div>
        </div>
      </div>
      
      {/* Dashboard Content */}
      <div className="relative -mt-4">
        <MomentumDashboard />
      </div>
    </main>
  );
}
