// src/components/Header.tsx
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { Leaf, User, LogOut, Settings, Users } from 'lucide-react';
import { Button } from './ui/button';
import { useState, useEffect } from 'react';
import { getAuthToken, getRefreshToken, removeTokens } from '../services/apiConfig';
import { authService } from '../services/authService';

interface HeaderProps {
  isLoggedIn?: boolean;
  userName?: string;
}

interface UserData {
  id: number;
  email: string;
  full_name: string;
  role: string;
  is_active: boolean;
  created_at: string;
}

export function Header({ isLoggedIn = false, userName }: HeaderProps) {
  const location = useLocation();
  const navigate = useNavigate();
  const [user, setUser] = useState<UserData | null>(null);

  useEffect(() => {
    try {
      const userStr = localStorage.getItem('user');
      if (userStr) {
        setUser(JSON.parse(userStr));
      }
    } catch (error) {
      console.error('Ошибка при получении пользователя:', error);
    }
  }, [isLoggedIn]);

  const isActive = (path: string): boolean => location.pathname === path;

  const getUserName = (): string => {
    if (userName) return userName;
    if (user) return user.full_name || user.email;
    return 'Пользователь';
  };

  const getUserRole = (): string => {
    if (user) return user.role;
    return 'user';
  };

  const getRoleDisplay = (): string => {
    const role = getUserRole();
    switch (role) {
      case 'admin': return 'Админ';
      case 'manager': return 'Менеджер';
      default: return 'Пользователь';
    }
  };

  const getRoleColor = (): string => {
    const role = getUserRole();
    switch (role) {
      case 'admin': return 'bg-purple-100 text-purple-700';
      case 'manager': return 'bg-blue-100 text-blue-700';
      default: return 'bg-gray-100 text-gray-700';
    }
  };

  const handleLogout = async () => {
    const refreshToken = getRefreshToken();   // теперь функция импортирована
    if (refreshToken) {
      await authService.logout(refreshToken).catch(() => {});
    } else {
      removeTokens();   // теперь функция импортирована
    }
    setUser(null);
    navigate('/');
  };

  const actualUserName = getUserName();
  const userRole = getUserRole();
  const roleDisplay = getRoleDisplay();
  const roleColor = getRoleColor();

  return (
    <header className="border-b bg-white/80 backdrop-blur-md shadow-sm sticky top-0 z-50">
      <div className="container mx-auto px-6 py-4 flex items-center justify-between max-w-7xl">
        <Link to="/" className="flex items-center gap-2 hover:scale-105 transition-transform">
          <div className="p-1.5 bg-primary/10 rounded-full">
            <Leaf className="size-8 text-primary" />
          </div>
          <span className="text-xl text-primary">Умный Сад</span>
        </Link>

        <nav className="flex items-center gap-6">
          {isLoggedIn || user ? (
            <>
              <Link
                to="/dashboard"
                className={`transition-colors ${
                  isActive('/dashboard')
                    ? 'text-primary font-semibold'
                    : 'text-muted-foreground hover:text-primary'
                }`}
              >
                Дашборд
              </Link>

              <Link
                to="/analysis"
                className={`transition-colors ${
                  isActive('/analysis')
                    ? 'text-primary font-semibold'
                    : 'text-muted-foreground hover:text-primary'
                }`}
              >
                Анализ
              </Link>

              <Link
                to="/history"
                className={`transition-colors ${
                  isActive('/history')
                    ? 'text-primary font-semibold'
                    : 'text-muted-foreground hover:text-primary'
                }`}
              >
                История
              </Link>

              <Link
                to="/analytics"
                className={`transition-colors ${
                  isActive('/analytics')
                    ? 'text-primary font-semibold'
                    : 'text-muted-foreground hover:text-primary'
                }`}
              >
                Аналитика
              </Link>

              {(userRole === 'manager' || userRole === 'admin') && (
                <Link
                  to="/gardens/manage"
                  className={`flex items-center gap-1 transition-colors ${
                    isActive('/gardens/manage')
                      ? 'text-primary font-semibold'
                      : 'text-muted-foreground hover:text-primary'
                  }`}
                >
                  <Settings className="size-4" />
                  <span>Управление садами</span>
                </Link>
              )}

              {userRole === 'admin' && (
                <Link
                  to="/admin/users"
                  className={`flex items-center gap-1 transition-colors ${
                    isActive('/admin/users')
                      ? 'text-primary font-semibold'
                      : 'text-muted-foreground hover:text-primary'
                  }`}
                >
                  <Users className="size-4" />
                  <span>Пользователи</span>
                </Link>
              )}

              <div className="flex items-center gap-3 ml-4">
                <div className="flex items-center gap-2 bg-secondary/10 px-3 py-1.5 rounded-full">
                  <User className="size-4" />
                  <span className="font-medium">{actualUserName}</span>
                  <span className={`text-xs px-2 py-0.5 rounded-full ${roleColor}`}>
                    {roleDisplay}
                  </span>
                </div>

                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleLogout}
                  className="text-red-600 hover:text-red-700 hover:bg-red-50"
                  aria-label="Выйти"
                >
                  <LogOut className="size-4" />
                </Button>
              </div>
            </>
          ) : (
            <>
              <Link
                to="/"
                className={`transition-colors ${
                  isActive('/') ? 'text-primary font-semibold' : 'text-muted-foreground hover:text-primary'
                }`}
              >
                Главная
              </Link>

              <Button asChild className="shadow-md hover:shadow-lg transition-all">
                <Link to="/auth">Войти / Регистрация</Link>
              </Button>
            </>
          )}
        </nav>
      </div>
    </header>
  );
}