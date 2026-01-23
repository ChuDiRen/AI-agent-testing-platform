import dynamic from 'next/dynamic';
import './globals.css';

// Dynamically import the main component to avoid SSR issues with WebSocket
const Text2SQLPage = dynamic(() => import('@/components/Text2SQLPage'), {
  ssr: false,
  loading: () => (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mb-4"></div>
        <p className="text-gray-600">加载中...</p>
      </div>
    </div>
  ),
});

export default function Home() {
  return <Text2SQLPage />;
}
