// src/components/Header.tsx
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { Leaf, User, LogOut } from 'lucide-react';
import { Button } from './ui/button';

interface HeaderProps {
  isLoggedIn?: boolean;
  userName?: string;
}

export function Header({ isLoggedIn = false, userName }: HeaderProps) {
  const location = useLocation();
  const navigate = useNavigate();
  
  const isActive = (path: string) => location.pathname === path;
  
  // Получаем реальное имя пользователя из localStorage
  const getActualUserName = (): string => {
    if (userName) return userName;
    
    try {
      const userStr = localStorage.getItem('user');
      if (userStr) {
        const user = JSON.parse(userStr);
        return user.full_name || user.email || 'Пользователь';
      }
    } catch (error) {
      console.error('Ошибка получения пользователя:', error);
    }
    
    return 'Пользователь';
  };
  
  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    navigate('/');
  };
  
  const actualUserName = getActualUserName();
  
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
          {isLoggedIn ? (
            <>
              <Link 
                to="/dashboard" 
                className={`transition-colors ${isActive('/dashboard') ? 'text-primary font-semibold' : 'text-muted-foreground hover:text-primary'}`}
              >
                Дашборд
              </Link>
              <Link 
                to="/analysis" 
                className={`transition-colors ${isActive('/analysis') ? 'text-primary font-semibold' : 'text-muted-foreground hover:text-primary'}`}
              >
                Анализ
              </Link>
              <Link 
                to="/history" 
                className={`transition-colors ${isActive('/history') ? 'text-primary font-semibold' : 'text-muted-foreground hover:text-primary'}`}
              >
                История
              </Link>
              <Link 
                to="/analytics" 
                className={`transition-colors ${isActive('/analytics') ? 'text-primary font-semibold' : 'text-muted-foreground hover:text-primary'}`}
              >
                Аналитика
              </Link>
              <div className="flex items-center gap-3 ml-4">
                <div className="flex items-center gap-2 bg-secondary/10 px-3 py-1.5 rounded-full">
                  <User className="size-4" />
                  <span className="font-medium">{actualUserName}</span>
                  {/* Показываем роль, если есть */}
                  <span className="text-xs px-2 py-0.5 bg-primary/10 rounded-full">
                    {(() => {
                      try {
                        const userStr = localStorage.getItem('user');
                        if (userStr) {
                          const user = JSON.parse(userStr);
                          return user.role === 'admin' ? 'Админ' : 
                                 user.role === 'manager' ? 'Менеджер' : 'Пользователь';
                        }
                      } catch {
                        return 'Пользователь';
                      }
                      return 'Пользователь';
                    })()}
                  </span>
                </div>
                <Button 
                  variant="ghost" 
                  size="sm" 
                  onClick={handleLogout}
                  className="text-red-600 hover:text-red-700 hover:bg-red-50"
                >
                  <LogOut className="size-4" />
                </Button>
              </div>
            </>
          ) : (
            <>
              <Link 
                to="/" 
                className={`transition-colors ${isActive('/') ? 'text-primary' : 'text-muted-foreground hover:text-primary'}`}
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