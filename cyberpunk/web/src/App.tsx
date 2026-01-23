import { ConfigProvider } from 'antd';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { modernTheme } from './theme/antdTheme';
import { Login } from './pages/Login';
import { WorkspaceSelection } from './pages/WorkspaceSelection';
import { DashboardLayout } from './layouts/DashboardLayout';
import { HomeOverview } from './pages/HomeOverview';
import { AgentWorkbench } from './pages/AgentWorkbench';
import { PromptLibrary } from './pages/PromptLibrary';
import { ApiRepository } from './pages/ApiRepository';
import { TestCaseManagement } from './pages/TestCaseManagement';
import { EnvironmentSettings } from './pages/EnvironmentSettings';
import { RagKnowledgeBase } from './pages/RagKnowledgeBase';
import { KnowledgeGraphExplorer } from './pages/KnowledgeGraphExplorer';
import { RagChunkDebugger } from './pages/RagChunkDebugger';
import { TestSuiteOrchestration } from './pages/TestSuiteOrchestration';
import { JobQueueHistory } from './pages/JobQueueHistory';
import LiveExecutionConsole from './pages/LiveExecutionConsole';
import TestRunReportDetail from './pages/TestRunReportDetail';
import QualityAnalyticsDashboard from './pages/QualityAnalyticsDashboard';
import Integrations from './pages/Integrations';
import TeamPermissions from './pages/TeamPermissions';
import UserProfileSettings from './pages/UserProfileSettings';

function App() {
  return (
    <ConfigProvider theme={modernTheme}>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/workspace" element={<WorkspaceSelection />} />
          <Route path="/dashboard" element={<DashboardLayout />}>
            <Route index element={<HomeOverview />} />
            <Route path="agents" element={<AgentWorkbench />} />
            <Route path="prompts" element={<PromptLibrary />} />
            <Route path="api-repository" element={<ApiRepository />} />
            <Route path="knowledge" element={<RagKnowledgeBase />} />
            <Route path="graph-explorer" element={<KnowledgeGraphExplorer />} />
            <Route path="chunk-debugger" element={<RagChunkDebugger />} />
            <Route path="test-cases" element={<TestCaseManagement />} />
            <Route path="test-suites" element={<TestSuiteOrchestration />} />
            <Route path="jobs" element={<JobQueueHistory />} />
            <Route path="execution-console" element={<LiveExecutionConsole />} />
            <Route path="report-detail" element={<TestRunReportDetail />} />
            <Route path="analytics" element={<QualityAnalyticsDashboard />} />
            <Route path="integrations" element={<Integrations />} />
            <Route path="team" element={<TeamPermissions />} />
            <Route path="profile" element={<UserProfileSettings />} />
            <Route path="settings" element={<EnvironmentSettings />} />
            <Route path="settings/members" element={<TeamPermissions />} />
          </Route>
          <Route path="/settings/*" element={<Navigate to="/dashboard/settings" replace />} />
          <Route path="/" element={<Navigate to="/login" replace />} />
        </Routes>
      </BrowserRouter>
    </ConfigProvider>
  );
}

export default App;

