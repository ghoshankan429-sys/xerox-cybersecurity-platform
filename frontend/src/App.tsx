import React from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { MainLayout } from "@/layouts/MainLayout";
import { DashboardPage } from "@/pages/DashboardPage";
import { AnalyzePage } from "@/pages/AnalyzePage";
import { HistoryPage } from "@/pages/HistoryPage";
import { ReportsPage } from "@/pages/ReportsPage";
import { SettingsPage } from "@/pages/SettingsPage";
import { LoginPage } from "@/pages/LoginPage";
import { RegisterPage } from "@/pages/RegisterPage";

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <MainLayout>
        <Routes>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/analyze" element={<AnalyzePage />} />
          <Route path="/history" element={<HistoryPage />} />
          <Route path="/history/:id" element={<ReportsPage />} />
          <Route path="/reports" element={<ReportsPage />} />
          <Route path="/settings" element={<SettingsPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </MainLayout>
    </BrowserRouter>
  );
};

export default App;
