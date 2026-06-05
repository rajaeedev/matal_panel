import { Outlet } from 'react-router-dom';
import Sidebar from '../components/Sidebar';
import MobileNav from '../components/MobileNav'; 
import { useAuth } from '../context/AuthContext';
import { useTranslation } from 'react-i18next';
import { FiLogOut, FiRefreshCw, FiGlobe } from 'react-icons/fi';
import BrandMark from '../components/BrandMark';

const DashboardLayout = () => {
  const { logout } = useAuth();
  const { t, i18n } = useTranslation();

  const handleRefresh = () => {
    window.location.reload();
  };

  const changeLanguage = () => {
    const newLang = i18n.language === 'en' ? 'fa' : 'en';
    i18n.changeLanguage(newLang);
    document.documentElement.dir = newLang === 'fa' ? 'rtl' : 'ltr';
  };

  return (
    <div id="main-container">
      <Sidebar />
      <div className="content-wrapper">
        <header className="main-header">
          <div className="header-logo-container">
            <BrandMark compact />
          </div>
          <div className="header-actions">
            <button onClick={changeLanguage} className="action-btn">
              <FiGlobe size={18} />
            </button>
            <button onClick={handleRefresh} className="action-btn">
              <FiRefreshCw size={18} />
            </button>
            <button onClick={logout} className="btn btn-danger logout-btn">
              <FiLogOut />
              <span className="logout-text">{t('logout')}</span>
            </button>
          </div>
        </header>
        <main>
          <Outlet />
        </main>
      </div>
      <MobileNav />
    </div>
  );
};

export default DashboardLayout;
