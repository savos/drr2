import { Outlet } from 'react-router-dom';
import Header from './Header';

function PublicLayout({ user, onLogout }) {
  return (
    <>
      <Header user={user} onLogout={onLogout} />
      <Outlet />
    </>
  );
}

export default PublicLayout;
